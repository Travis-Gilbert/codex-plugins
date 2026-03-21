#!/bin/bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PLUGIN_DIR="$SCRIPT_DIR"
readonly PLUGIN_NAME="ml-pro"

log_info() { echo "[${PLUGIN_NAME}] $*"; }
log_error() { echo "[${PLUGIN_NAME}] ERROR: $*" >&2; }

# Clone a source repo into refs/ (shallow, no .git)
clone_ref() {
    local repo="$1"
    local target="$2"

    if [[ -d "${PLUGIN_DIR}/refs/${target}" ]]; then
        log_info "OK refs/${target}/"
    else
        log_info "Cloning ${repo} -> refs/${target}/"
        git clone --depth 1 --single-branch \
            "https://github.com/${repo}.git" "${PLUGIN_DIR}/refs/${target}"
        rm -rf "${PLUGIN_DIR}/refs/${target}/.git"
        log_info "OK refs/${target}/"
    fi
}

# Register slash commands
register_commands() {
    local cmd_dir="${PLUGIN_DIR}/.claude/commands"
    mkdir -p "$cmd_dir"

    local count=0
    for cmd in "${PLUGIN_DIR}/commands/"*.md; do
        [[ -f "$cmd" ]] || continue
        local name
        name=$(basename "$cmd" .md)
        ln -sf "$cmd" "${cmd_dir}/${name}.md"
        count=$((count + 1))
    done

    log_info "Registered ${count} commands"
}

main() {
    log_info "Installing ML-Pro plugin..."

    # Clone source repos for API verification
    log_info "Cloning reference source repos (this may take a few minutes)..."
    clone_ref "pytorch/pytorch"                    "pytorch"
    clone_ref "pyg-team/pytorch_geometric"         "pytorch-geometric"
    clone_ref "huggingface/transformers"            "transformers"
    clone_ref "pykeen/pykeen"                      "pykeen"
    clone_ref "DLR-RM/stable-baselines3"            "stable-baselines3"
    clone_ref "pytorch/torchtune"                   "torchtune"
    clone_ref "UKPLab/sentence-transformers"        "sentence-transformers"
    clone_ref "optuna/optuna"                       "optuna"

    # Register slash commands
    register_commands

    log_info "Install complete."
    log_info ""
    log_info "Available commands:"
    log_info "  /ml-build   - Build an ML system from a handoff doc"
    log_info "  /ml-debug   - Diagnose training failures"
    log_info "  /ml-train   - Generate a training pipeline"
    log_info "  /ml-deploy  - Export, optimize, and deploy a model"
}

main "$@"
