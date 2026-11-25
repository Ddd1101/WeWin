#!/usr/bin/env bash
# Run as root on Ali-Server. Fixed filesystems prevent image cache/temp growth.
set -euo pipefail
provision() {
    local volume_name="$1" volume_size="$2" mount_path="$3"
    local image_path="/var/lib/${volume_name}.img"
    if [[ ! -f "$image_path" ]]; then
        truncate -s "$volume_size" "$image_path"
        mkfs.ext4 -F -m 0 "$image_path"
    fi
    mkdir -p "$mount_path"
    if ! mountpoint -q "$mount_path"; then
        if [[ -n "$(find "$mount_path" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
            echo "Refusing to hide nonempty mount directory: $mount_path" >&2
            exit 1
        fi
        mount -o loop,nodev,nosuid,noexec "$image_path" "$mount_path"
    fi
    local entry="$image_path $mount_path ext4 loop,nodev,nosuid,noexec 0 0"
    if ! grep -Fqx "$entry" /etc/fstab; then
        printf '%s\n' "$entry" >> /etc/fstab
    fi
}
provision wewin-media-cache 2G /var/cache/wewin-media
provision wewin-upload-temp 512M /var/lib/wewin-upload
chown www-data:wewin /var/cache/wewin-media
chmod 0770 /var/cache/wewin-media
install -d -m 0700 -o www-data -g www-data /var/lib/wewin-upload/nginx
install -d -m 0700 -o wewin -g wewin /var/lib/wewin-upload/django
