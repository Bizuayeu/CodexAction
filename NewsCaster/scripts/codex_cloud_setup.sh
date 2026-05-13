#!/usr/bin/env bash
# Setup entrypoint for running NewsCaster from Codex Cloud.
#
# Codex Cloud secrets are available to setup scripts only. If
# NEWSCASTER_OAUTH_TOKEN_JSON is configured as a secret, this script writes it to
# a private token file and persists NEWSCASTER_OAUTH_TOKEN_PATH for the agent
# phase through ~/.bashrc.

set -euo pipefail

log() { echo "[newscaster-cloud-setup] $*"; }

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "$script_dir/.." && pwd)"
config_root="${HOME}/.newscaster"
env_file="${config_root}/env.sh"

mkdir -p "$config_root"
chmod 700 "$config_root" 2>/dev/null || true

write_export() {
    local key="$1"
    local value="$2"
    printf 'export %s=%q\n' "$key" "$value" >>"$env_file"
}

log "project_dir=${project_dir}"
cd "$project_dir"

log "installing Python dependencies"
python -m pip install --quiet --upgrade pip setuptools wheel
if ! python -m pip install --quiet --upgrade -e ".[dev]" 2>/tmp/newscaster-cloud-pip.log; then
    log "first install failed; retrying cffi/cryptography before reinstall"
    cat /tmp/newscaster-cloud-pip.log >&2
    python -m pip install --quiet --ignore-installed cffi cryptography
    python -m pip install --quiet --upgrade -e ".[dev]"
fi

: >"$env_file"
chmod 600 "$env_file" 2>/dev/null || true

for ca_bundle in \
    /etc/ssl/certs/ca-certificates.crt \
    /etc/pki/tls/certs/ca-bundle.crt \
    /etc/ssl/cert.pem; do
    if [ -f "$ca_bundle" ]; then
        write_export "HTTPLIB2_CA_CERTS" "$ca_bundle"
        log "HTTPLIB2_CA_CERTS=${ca_bundle}"
        break
    fi
done

if [ -n "${NEWSCASTER_OAUTH_TOKEN_JSON:-}" ]; then
    token_path="${config_root}/oauth_token.json"
    printf '%s' "$NEWSCASTER_OAUTH_TOKEN_JSON" >"$token_path"
    python -m json.tool "$token_path" >/dev/null
    chmod 600 "$token_path" 2>/dev/null || true
    write_export "NEWSCASTER_OAUTH_TOKEN_PATH" "$token_path"
    log "materialized NEWSCASTER_OAUTH_TOKEN_JSON to ${token_path}"
elif [ -n "${NEWSCASTER_OAUTH_TOKEN_PATH:-}" ]; then
    write_export "NEWSCASTER_OAUTH_TOKEN_PATH" "$NEWSCASTER_OAUTH_TOKEN_PATH"
fi

bashrc="${HOME}/.bashrc"
source_line="source \"${env_file}\""
touch "$bashrc"
if ! grep -Fqx "$source_line" "$bashrc"; then
    printf '\n# NewsCaster Codex Cloud environment\n%s\n' "$source_line" >>"$bashrc"
fi

log "verifying imports"
python - <<'PY'
from zoneinfo import ZoneInfo

import google.auth
import google_auth_oauthlib
import googleapiclient

ZoneInfo("Asia/Tokyo")
PY

log "ready"
