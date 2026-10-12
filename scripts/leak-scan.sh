#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 PersonifAI LLC

# leak-scan.sh — this repository is public; nothing private may land in it.
#
#   scripts/leak-scan.sh TREE [HOSTMAP]
#
# Generic checks, always on (the patterns here are safe to publish):
#   * names of other private packages and products (see NAMES below);
#   * private-network addresses: 10/8, 172.16/12, 192.168/16, CGNAT 100.64/10;
#   * internal host suffixes: .internal, .local, .lan, .ts.net, .ngrok.app;
#   * credential shapes: private keys, GitHub/HF/AWS/Anthropic/Tailscale tokens,
#     long bearer tokens, SOPS/age material.
# With HOSTMAP (a "<real> <generic>" file kept OUTSIDE this repo), every real
# name in it is a hit too. CI also runs the private maintainer list (fetched at
# run time, never committed) over the same tree.
#
# Waive one exact line with a same-line comment `leak-ok: <reason>` (a reason is
# required). There is no file of waivers.

set -uo pipefail
TREE="${1:?usage: leak-scan.sh TREE [HOSTMAP]}"
HOSTMAP="${2:-}"

PATTERNS=(
    '(^|[^A-Za-z])[Ee]volve'
    '(^|[^A-Za-z])[Ii]ntel([^A-Za-z]|ligen|$)'
    '(^|[^0-9.])10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}([^0-9]|$)'
    '(^|[^0-9.])172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3}([^0-9]|$)'
    '(^|[^0-9.])192\.168\.[0-9]{1,3}\.[0-9]{1,3}([^0-9]|$)'
    '(^|[^0-9.])100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]{1,3}\.[0-9]{1,3}([^0-9]|$)'
    '[A-Za-z0-9-]+\.(internal|local|lan|ts\.net|ngrok\.app)([^A-Za-z0-9]|$)'
    '-----BEGIN [A-Z ]*PRIVATE KEY-----'
    'gh[pousr]_[A-Za-z0-9]{20,}'
    # Prefixes are split in two (the shell joins adjacent quoted parts) so this
    # file never holds a credential prefix whole and no scanner needs a waiver.
    'github_''pat_[A-Za-z0-9_]{20,}'
    'hf_[A-Za-z0-9]{16,}'
    'sk-ant-[A-Za-z0-9-]{16,}'
    'AKIA[0-9A-Z]{16}'
    'tskey-(api|auth)-[A-Za-z0-9-]{10,}'
    '(noo|pai)-(sk|mcp)-[A-Za-z0-9]{16,}'
    '[Bb]earer +[A-Za-z0-9._-]{30,}'
    'ENC\[AES256_GCM'
    'AGE-SECRET''-KEY-1'
)
if [[ -n "$HOSTMAP" ]]; then
    while read -r real _; do
        [[ -z "$real" || "$real" == \#* ]] && continue
        PATTERNS+=("(^|[^A-Za-z0-9])(${real}|${real//-/}|${real//-/_})([^A-Za-z0-9]|$)")
    done < "$HOSTMAP"
fi

ARGS=(-rnEI -i)
for p in "${PATTERNS[@]}"; do ARGS+=(-e "$p"); done
HITS=$(grep "${ARGS[@]}" --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.pytest_cache \
          --exclude-dir=dist --exclude-dir=build --exclude=LICENSE "$TREE" 2>/dev/null \
       | grep -vE 'leak-ok:[[:space:]]*[^[:space:]]' || true)
# This script's own pattern lines are the patterns, not leaks.
HITS=$(printf '%s\n' "$HITS" | grep -v "^${TREE%/}/scripts/leak-scan.sh:" | grep -v '^$' || true)

if [[ -n "$HITS" ]]; then
    echo "leak-scan: FAIL"
    printf '%s\n' "$HITS" | sed 's/^/  /' | head -60
    exit 1
fi
echo "leak-scan: clean (${#PATTERNS[@]} patterns)"
