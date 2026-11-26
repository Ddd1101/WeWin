package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"image"
	"image/png"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func fixture(t *testing.T) *Origin {
	t.Helper()
	root := t.TempDir()
	for _, dir := range []string{"products", ".tmp", ".trash"} {
		if e := os.MkdirAll(filepath.Join(root, dir), 0750); e != nil {
			t.Fatal(e)
		}
	}
	return &Origin{cfg: Config{Root: root, ReadToken: strings.Repeat("r", 40), WriteToken: strings.Repeat("w", 40), MinFree: 1}, uploads: make(chan struct{}, 4)}
}
func pngData() []byte {
	var b bytes.Buffer
	png.Encode(&b, image.NewRGBA(image.Rect(0, 0, 8, 8)))
	return b.Bytes()
}
func send(o *Origin, method, path string, b []byte, token string) *httptest.ResponseRecorder {
	r := httptest.NewRequest(method, path, bytes.NewReader(b))
	r.Header.Set("Authorization", "Bearer "+token)
	h := sha256.Sum256(b)
	r.Header.Set("X-Content-SHA256", hex.EncodeToString(h[:]))
	w := httptest.NewRecorder()
	o.ServeHTTP(w, r)
	return w
}
func TestOriginLifecycle(t *testing.T) {
	o := fixture(t)
	key := "/objects/products/2026/11/25/image.png"
	data := pngData()
	if w := send(o, "PUT", key, data, o.cfg.WriteToken); w.Code != 201 {
		t.Fatal(w.Code, w.Body.String())
	}
	if w := send(o, "PUT", key, data, o.cfg.WriteToken); w.Code != 200 {
		t.Fatal("same upload must be idempotent", w.Code)
	}
	if w := send(o, "GET", key, nil, o.cfg.ReadToken); w.Code != 200 || !bytes.Equal(w.Body.Bytes(), data) {
		t.Fatal("read mismatch")
	}
	if w := send(o, "DELETE", key, nil, o.cfg.ReadToken); w.Code != 401 {
		t.Fatal("read key can delete")
	}
	if w := send(o, "DELETE", key, nil, o.cfg.WriteToken); w.Code != 204 {
		t.Fatal(w.Code)
	}
	if w := send(o, "GET", key, nil, o.cfg.ReadToken); w.Code != 404 {
		t.Fatal("deleted image still served")
	}
	dirs, _ := os.ReadDir(filepath.Join(o.cfg.Root, ".trash"))
	if len(dirs) != 1 {
		t.Fatal("deleted original missing from trash")
	}
	saved, _ := os.ReadFile(filepath.Join(o.cfg.Root, ".trash", dirs[0].Name(), "image"))
	if !bytes.Equal(data, saved) {
		t.Fatal("trash mismatch")
	}
}
func TestInvalidRequests(t *testing.T) {
	o := fixture(t)
	for _, key := range []string{"products/../escape.png", "products/.hidden/x.png", "products//x.png", "/products/x.png", "products/x.exe"} {
		if _, e := o.path(key); e == nil {
			t.Fatal(key)
		}
	}
	if w := send(o, "PUT", "/objects/products/x.png", []byte("invalid image"), o.cfg.WriteToken); w.Code != 415 {
		t.Fatal(w.Code)
	}
	if w := send(o, "GET", "/manifest", nil, "wrong"); w.Code != 401 {
		t.Fatal(w.Code)
	}
	outside := t.TempDir()
	os.Symlink(outside, filepath.Join(o.cfg.Root, "products", "link"))
	if _, e := o.path("products/link/image.png"); e == nil {
		t.Fatal("symlink accepted")
	}
}
func TestInterruptedAndLowSpaceUpload(t *testing.T) {
	o := fixture(t)
	r := httptest.NewRequest("PUT", "/objects/products/x.png", bytes.NewReader(pngData()))
	r.ContentLength += 10
	r.Header.Set("Authorization", "Bearer "+o.cfg.WriteToken)
	h := sha256.Sum256(pngData())
	r.Header.Set("X-Content-SHA256", hex.EncodeToString(h[:]))
	w := httptest.NewRecorder()
	o.ServeHTTP(w, r)
	if w.Code != 400 {
		t.Fatal(w.Code)
	}
	if _, e := os.Stat(filepath.Join(o.cfg.Root, "products/x.png")); !os.IsNotExist(e) {
		t.Fatal("interrupted file committed")
	}
	o.cfg.MinFree = ^uint64(0)
	if w := send(o, "PUT", "/objects/products/y.png", pngData(), o.cfg.WriteToken); w.Code != 507 {
		t.Fatal(w.Code)
	}
}
