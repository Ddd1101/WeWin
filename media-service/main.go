// N1 media origin. No public listener or external runtime dependency.
package main

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"syscall"
	"time"
)

const maxImage = 100 << 20
const trashLimit = 5 << 30
const trashAge = 7 * 24 * time.Hour

type Config struct {
	Root       string `json:"root"`
	ReadToken  string `json:"read_token"`
	WriteToken string `json:"write_token"`
	Listen     string `json:"listen"`
	MinFree    uint64 `json:"min_free"`
}
type Origin struct {
	cfg     Config
	mu      sync.RWMutex
	uploads chan struct{}
}
type Item struct {
	Name   string `json:"name"`
	Size   int64  `json:"size"`
	SHA256 string `json:"sha256"`
}

func digest(name string) (string, error) {
	f, e := os.Open(name)
	if e != nil {
		return "", e
	}
	defer f.Close()
	h := sha256.New()
	_, e = io.Copy(h, f)
	return hex.EncodeToString(h.Sum(nil)), e
}
func (o *Origin) path(key string) (string, error) {
	if !strings.HasPrefix(key, "products/") || strings.ContainsAny(key, "\\\x00") || filepath.Clean(key) != key || strings.HasPrefix(key, "/") {
		return "", errors.New("invalid path")
	}
	for _, p := range strings.Split(key, "/") {
		if p == "" || p == "." || p == ".." || strings.HasPrefix(p, ".") {
			return "", errors.New("invalid path")
		}
	}
	ext := strings.ToLower(filepath.Ext(key))
	if ext != ".jpg" && ext != ".jpeg" && ext != ".png" && ext != ".webp" && ext != ".gif" {
		return "", errors.New("unsupported extension")
	}
	p := o.cfg.Root
	for _, part := range strings.Split(key, "/") {
		p = filepath.Join(p, part)
		st, e := os.Lstat(p)
		if e == nil && st.Mode()&os.ModeSymlink != 0 {
			return "", errors.New("symbolic link rejected")
		}
		if e != nil && !os.IsNotExist(e) {
			return "", e
		}
	}
	return p, nil
}
func (o *Origin) auth(r *http.Request, write bool) bool {
	token := o.cfg.ReadToken
	if write {
		token = o.cfg.WriteToken
	}
	return subtle.ConstantTimeCompare([]byte(r.Header.Get("Authorization")), []byte("Bearer "+token)) == 1
}
func reply(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}
func (o *Origin) space() bool {
	var st syscall.Statfs_t
	if syscall.Statfs(o.cfg.Root, &st) != nil {
		return false
	}
	return st.Bavail*uint64(st.Bsize) > o.cfg.MinFree
}
func (o *Origin) probe() error {
	if !o.space() {
		return errors.New("low space")
	}
	f, e := os.CreateTemp(filepath.Join(o.cfg.Root, ".tmp"), "probe-")
	if e != nil {
		return e
	}
	defer os.Remove(f.Name())
	_, e = f.WriteString("wewin-media-ready\n")
	if e == nil {
		e = f.Sync()
	}
	f.Close()
	if e != nil {
		return e
	}
	rename := f.Name() + ".rename"
	if e = os.Rename(f.Name(), rename); e != nil {
		return e
	}
	defer os.Remove(rename)
	b, e := os.ReadFile(rename)
	if e != nil || string(b) != "wewin-media-ready\n" {
		return errors.New("probe mismatch")
	}
	return nil
}
func syncDir(path string) error {
	f, e := os.Open(path)
	if e != nil {
		return e
	}
	defer f.Close()
	return f.Sync()
}
func (o *Origin) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	write := r.Method != "GET" && r.Method != "HEAD"
	if !o.auth(r, write) {
		reply(w, 401, map[string]bool{"ok": false})
		return
	}
	if r.URL.Path == "/health" {
		if r.Method != "GET" {
			reply(w, 405, nil)
			return
		}
		o.mu.Lock()
		e := o.probe()
		o.mu.Unlock()
		if e != nil {
			reply(w, 503, map[string]bool{"ok": false})
		} else {
			reply(w, 200, map[string]bool{"ok": true})
		}
		return
	}
	if r.URL.Path == "/manifest" && r.Method == "GET" {
		o.mu.RLock()
		defer o.mu.RUnlock()
		items := []Item{}
		e := filepath.WalkDir(filepath.Join(o.cfg.Root, "products"), func(p string, d os.DirEntry, e error) error {
			if os.IsNotExist(e) {
				return nil
			}
			if e != nil {
				return e
			}
			if d.Type()&os.ModeSymlink != 0 {
				return errors.New("symlink")
			}
			if d.IsDir() {
				return nil
			}
			name, _ := filepath.Rel(o.cfg.Root, p)
			if _, e = o.path(name); e != nil {
				return e
			}
			st, e := d.Info()
			if e != nil {
				return e
			}
			hash, e := digest(p)
			if e != nil {
				return e
			}
			items = append(items, Item{name, st.Size(), hash})
			return nil
		})
		if e != nil {
			reply(w, 503, nil)
		} else {
			reply(w, 200, map[string]any{"files": items})
		}
		return
	}
	if !strings.HasPrefix(r.URL.Path, "/objects/") {
		reply(w, 404, nil)
		return
	}
	key := strings.TrimPrefix(r.URL.Path, "/objects/")
	path, e := o.path(key)
	if e != nil {
		reply(w, 400, nil)
		return
	}
	switch r.Method {
	case "GET", "HEAD":
		o.mu.RLock()
		f, e := os.Open(path)
		if e != nil {
			o.mu.RUnlock()
			if os.IsNotExist(e) {
				reply(w, 404, nil)
			} else {
				reply(w, 503, nil)
			}
			return
		}
		st, e := f.Stat()
		o.mu.RUnlock()
		defer f.Close()
		if e != nil {
			reply(w, 503, nil)
			return
		}
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Cache-Control", "public, max-age=3600")
		http.ServeContent(w, r, filepath.Base(path), st.ModTime(), f)
	case "PUT":
		select {
		case o.uploads <- struct{}{}:
			defer func() { <-o.uploads }()
		default:
			reply(w, 503, nil)
			return
		}
		if !o.space() {
			reply(w, 507, nil)
			return
		}
		if r.ContentLength < 0 || r.ContentLength > maxImage {
			reply(w, 413, nil)
			return
		}
		want := r.Header.Get("X-Content-SHA256")
		if len(want) != 64 {
			reply(w, 400, nil)
			return
		}
		f, e := os.CreateTemp(filepath.Join(o.cfg.Root, ".tmp"), "upload-")
		if e != nil {
			reply(w, 503, nil)
			return
		}
		defer os.Remove(f.Name())
		h := sha256.New()
		n, e := io.Copy(io.MultiWriter(f, h), http.MaxBytesReader(w, r.Body, maxImage))
		if e == nil {
			e = f.Sync()
		}
		f.Close()
		got := hex.EncodeToString(h.Sum(nil))
		if e != nil || n != r.ContentLength || got != want {
			reply(w, 400, nil)
			return
		}
		// Validate actual content; full decoding and decompression checks run in Django.
		in, e := os.Open(f.Name())
		if e != nil {
			reply(w, 503, nil)
			return
		}
		header := make([]byte, 512)
		nHeader, _ := in.Read(header)
		in.Close()
		mime := http.DetectContentType(header[:nHeader])
		ext := strings.ToLower(filepath.Ext(path))
		allowed := map[string]string{".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
		if mime != allowed[ext] {
			reply(w, 415, nil)
			return
		}
		o.mu.Lock()
		defer o.mu.Unlock()
		if old, e := digest(path); e == nil {
			if old == got {
				reply(w, 200, Item{key, n, got})
			} else {
				reply(w, 409, nil)
			}
			return
		} else if !os.IsNotExist(e) {
			reply(w, 503, nil)
			return
		}
		if _, e = o.path(key); e != nil {
			reply(w, 400, nil)
			return
		}
		if e = os.MkdirAll(filepath.Dir(path), 0750); e == nil {
			e = os.Rename(f.Name(), path)
		}
		if e == nil {
			e = syncDir(filepath.Dir(path))
		}
		if e != nil {
			reply(w, 503, nil)
			return
		}
		reply(w, 201, Item{key, n, got})
	case "DELETE":
		o.mu.Lock()
		defer o.mu.Unlock()
		if _, e = os.Stat(path); os.IsNotExist(e) {
			w.WriteHeader(204)
			return
		}
		dir, e := os.MkdirTemp(filepath.Join(o.cfg.Root, ".trash"), time.Now().UTC().Format("20060102T150405.000000000Z")+"-")
		if e != nil {
			reply(w, 503, nil)
			return
		}
		meta := map[string]any{"name": key, "deleted_at": time.Now().UTC()}
		b, _ := json.Marshal(meta)
		if e = os.WriteFile(filepath.Join(dir, "metadata.json"), b, 0600); e == nil {
			e = os.Rename(path, filepath.Join(dir, "image"))
		}
		if e != nil {
			os.RemoveAll(dir)
			reply(w, 503, nil)
			return
		}
		syncDir(filepath.Dir(path))
		syncDir(dir)
		o.cleanTrash()
		w.WriteHeader(204)
	default:
		reply(w, 405, nil)
	}
}
func (o *Origin) cleanTrash() {
	tmp, _ := os.ReadDir(filepath.Join(o.cfg.Root, ".tmp"))
	for _, d := range tmp {
		if d.IsDir() {
			continue
		}
		p := filepath.Join(o.cfg.Root, ".tmp", d.Name())
		st, e := d.Info()
		if e == nil && time.Since(st.ModTime()) > time.Hour {
			os.Remove(p)
		}
	}
	type old struct {
		p string
		t time.Time
		s int64
	}
	all := []old{}
	var total int64
	dirs, _ := os.ReadDir(filepath.Join(o.cfg.Root, ".trash"))
	for _, d := range dirs {
		if !d.IsDir() {
			continue
		}
		p := filepath.Join(o.cfg.Root, ".trash", d.Name())
		st, e := os.Stat(filepath.Join(p, "image"))
		if e != nil {
			continue
		}
		ds, e := os.Stat(p)
		if e != nil {
			continue
		}
		all = append(all, old{p, ds.ModTime(), st.Size()})
		total += st.Size()
	}
	sort.Slice(all, func(i, j int) bool { return all[i].t.Before(all[j].t) })
	for _, a := range all {
		st, _ := os.Stat(a.p)
		if st != nil && (time.Since(st.ModTime()) > trashAge || total > trashLimit) {
			if os.RemoveAll(a.p) == nil {
				total -= a.s
			}
		}
	}
}
func main() {
	if len(os.Args) != 2 {
		log.Fatal("usage: wewin-media config.json")
	}
	b, e := os.ReadFile(os.Args[1])
	if e != nil {
		log.Fatal(e)
	}
	var c Config
	if json.Unmarshal(b, &c) != nil || len(c.ReadToken) < 32 || len(c.WriteToken) < 32 || c.ReadToken == c.WriteToken || !filepath.IsAbs(c.Root) {
		log.Fatal("invalid config")
	}
	host, _, e := net.SplitHostPort(c.Listen)
	if e != nil || net.ParseIP(host) == nil || !net.ParseIP(host).IsLoopback() {
		log.Fatal("loopback listener required")
	}
	if c.MinFree == 0 {
		c.MinFree = 5 << 30
	}
	for _, p := range []string{c.Root, filepath.Join(c.Root, "products"), filepath.Join(c.Root, ".tmp"), filepath.Join(c.Root, ".trash")} {
		if e = os.MkdirAll(p, 0750); e != nil {
			log.Fatal(e)
		}
	}
	origin := &Origin{cfg: c, uploads: make(chan struct{}, 4)}
	go func() {
		for range time.Tick(time.Hour) {
			origin.mu.Lock()
			origin.cleanTrash()
			origin.mu.Unlock()
		}
	}()
	server := &http.Server{Addr: c.Listen, Handler: origin, ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 120 * time.Second, WriteTimeout: 120 * time.Second, IdleTimeout: 30 * time.Second, MaxHeaderBytes: 16 << 10}
	fmt.Println("WeWin media origin started on loopback")
	log.Fatal(server.ListenAndServe())
}
