#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BASE_DIR="$HOME/secret-backup-$TIMESTAMP"
SECRETS_DIR="$BASE_DIR/secrets"
EXPORT_DIR="$BASE_DIR/exports"

mkdir -p "$SECRETS_DIR"
mkdir -p "$EXPORT_DIR"

echo "[+] Creating secret backup at $BASE_DIR"

########################################
# 1. Copy Known Secret Directories
########################################

copy_if_exists () {
    if [ -d "$1" ]; then
        echo "[+] Copying directory: $1"
        cp -a "$1" "$SECRETS_DIR/"
    fi
    if [ -f "$1" ]; then
        echo "[+] Copying file: $1"
        cp -a "$1" "$SECRETS_DIR/"
    fi
}

copy_if_exists "$HOME/.ssh"
copy_if_exists "$HOME/.aws"
copy_if_exists "$HOME/.kaggle"
copy_if_exists "$HOME/.docker"
copy_if_exists "$HOME/.pki"
copy_if_exists "$HOME/.gsutil"
copy_if_exists "$HOME/.npmrc"
copy_if_exists "$HOME/.pypirc"

if [ -d "$HOME/.config/gcloud" ]; then
    mkdir -p "$SECRETS_DIR/.config"
    cp -a "$HOME/.config/gcloud" "$SECRETS_DIR/.config/"
fi

########################################
# 2. Export GPG Secret Keys (Safer)
########################################

if command -v gpg >/dev/null 2>&1; then
    echo "[+] Exporting GPG secret keys"
    gpg --export-secret-keys --armor > "$EXPORT_DIR/gpg-private-keys.asc" || true
    gpg --export-ownertrust > "$EXPORT_DIR/gpg-ownertrust.txt" || true
fi

########################################
# 3. Scan for Likely Secret Files
########################################

echo "[+] Scanning for .env / credentials / token files"

find "$HOME" \
  -type f \
  \( -name ".env" \
  -o -name ".env.*" \
  -o -name "*credentials*" \
  -o -name "*secret*" \
  -o -name "*token*" \
  -o -name "kaggle.json" \
  \) \
  ! -path "*/.cache/*" \
  ! -path "*/.local/*" \
  ! -path "*/.mozilla/*" \
  2>/dev/null \
  | while read -r file; do
        DEST="$SECRETS_DIR/discovered$(dirname "${file#$HOME}")"
        mkdir -p "$DEST"
        cp -a "$file" "$DEST/"
    done

########################################
# 4. Fix Permissions
########################################

chmod -R go-rwx "$BASE_DIR"

########################################
# 5. Create Encrypted Archive
########################################

ARCHIVE="$HOME/secret-backup-$TIMESTAMP.tar.gz"

echo "[+] Creating archive $ARCHIVE"
tar -czf "$ARCHIVE" -C "$BASE_DIR" .

echo "[+] Encrypting archive"
gpg -c "$ARCHIVE"

echo "[+] Removing unencrypted archive"
shred -u "$ARCHIVE"

echo ""
echo "✅ Encrypted secret backup created:"
echo "   $ARCHIVE.gpg"
echo ""
echo "⚠️  Store this securely (offline USB or password manager)."
