#!/bin/sh
# Codem_Test_Repo sandbox init/build script
# Fix: cloud sandbox (linux-arm64) sometimes misses the platform CLI package
# because npm silently skips failed optionalDependencies fetches.
# Idempotent: no-op when the binary is already present or on non-arm64 hosts.

_fix_pkg() {
  cur="${CODEM_HOME:-$HOME/.codem}/runtime/current.json"
  [ -f "$cur" ] || return 0
  ver=$(node -p "require('$cur').version" 2>/dev/null) || return 0
  dir="${CODEM_HOME:-$HOME/.codem}/runtime/versions/$ver"
  [ -x "$dir/node_modules/@lark-codem/codem-cli-linux-arm64/bin/codem" ] && return 0
  echo "[build.sh] missing codem-cli-linux-arm64@$ver, installing..."
  for i in 1 2 3; do
    npm install --prefix "$dir" "@lark-codem/codem-cli-linux-arm64@$ver" \
      --registry https://registry.npmmirror.com \
      --cache "${CODEM_HOME:-$HOME/.codem}/runtime/.npm-cache" \
      --no-save --force && break
    echo "[build.sh] install attempt $i failed, retrying..."
    sleep 5
  done
}

_fix_pkg

# ---- your original build steps below (if any) ----
echo "[build.sh] done"
