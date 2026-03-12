#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bootstrap_refs.sh [--dry-run] [dest_dir] [research_api_path]

Defaults:
  dest_dir = $HOME/.codex/cache/scipy-pro-refs

Examples:
  bootstrap_refs.sh --dry-run
  bootstrap_refs.sh "$HOME/.codex/cache/scipy-pro-refs"
  bootstrap_refs.sh "$HOME/.codex/cache/scipy-pro-refs" "/path/to/research_api"
EOF
}

dry_run=0

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=1
  shift
fi

dest_dir="${1:-$HOME/.codex/cache/scipy-pro-refs}"
research_api_path="${2:-${RESEARCH_API_PATH:-}}"

repos=(
  "numpy https://github.com/numpy/numpy.git"
  "scipy https://github.com/scipy/scipy.git"
  "pandas https://github.com/pandas-dev/pandas.git"
  "scikit-learn https://github.com/scikit-learn/scikit-learn.git"
  "spacy https://github.com/explosion/spaCy.git"
  "sentence-transformers https://github.com/UKPLab/sentence-transformers.git"
  "faiss https://github.com/facebookresearch/faiss.git"
  "networkx https://github.com/networkx/networkx.git"
  "pykeen https://github.com/pykeen/pykeen.git"
  "pytorch https://github.com/pytorch/pytorch.git"
  "altair https://github.com/vega/altair.git"
  "rank-bm25 https://github.com/dorianbrown/rank_bm25.git"
  "pymc https://github.com/pymc-devs/pymc.git"
)

clone_or_update() {
  local name="$1"
  local url="$2"
  local target="$dest_dir/$name"

  if [[ "$dry_run" -eq 1 ]]; then
    if [[ -d "$target/.git" ]]; then
      echo "update $name -> $target"
    else
      echo "clone  $name -> $target"
    fi
    return
  fi

  mkdir -p "$dest_dir"

  if [[ -d "$target/.git" ]]; then
    git -C "$target" fetch --depth 1 origin
    git -C "$target" reset --hard FETCH_HEAD
  else
    git clone --depth 1 "$url" "$target"
  fi
}

for repo in "${repos[@]}"; do
  name="${repo%% *}"
  url="${repo#* }"
  clone_or_update "$name" "$url"
done

if [[ -n "$research_api_path" ]]; then
  if [[ ! -d "$research_api_path" ]]; then
    echo "research_api path not found: $research_api_path" >&2
    exit 1
  fi

  if [[ "$dry_run" -eq 1 ]]; then
    echo "link   research_api -> $dest_dir/research_api"
  else
    rm -rf "$dest_dir/research_api"
    ln -s "$research_api_path" "$dest_dir/research_api"
  fi
fi

cat <<EOF

Reference root: $dest_dir
Suggested next commands:
  rg "SentenceTransformer|CrossEncoder" "$dest_dir/sentence-transformers"
  rg "PageRank|community|louvain" "$dest_dir/networkx"
  rg "TfidfVectorizer|TruncatedSVD" "$dest_dir/scikit-learn"
EOF
