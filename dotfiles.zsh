#!/bin/zsh
# Run with zsh; no Python, Git, package manager, or scanner assumed beforehand.
emulate -LR zsh
setopt ERR_EXIT NO_UNSET PIPE_FAIL
repo_script_dir=${0:A:h}

main() {
    local repo_dir=$repo_script_dir
    local action=${1:-doctor}
    (( $# == 0 )) || shift
    local python_cmd=''
    local candidate
    for candidate in python3 python; do
        if (( $+commands[$candidate] )) && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then
            python_cmd=$commands[$candidate]
            break
        fi
    done
    if [[ -z $python_cmd ]]; then
        print -u2 'Python 3.8+ is required. No files collected or packages installed.'
        print -u2 'Install Python 3 through your OS/NAS package manager, then rerun this command.'
        return 1
    fi
    case $action in
        doctor)
            print 'Python 3.8+: available; capture and compare are ready.'
            if (( $+commands[git] )); then
                print 'Git: available.'
            else
                print 'Git: missing; needed only for committing/syncing snapshots.'
            fi
            if (( $+commands[gitleaks] )); then
                if gitleaks dir --help >/dev/null 2>&1; then
                    print 'Gitleaks: available; export will verify required flags and scan results.'
                else
                    print -u2 'Gitleaks: incompatible; install a release supporting dir scans.'
                    return 1
                fi
            else
                print 'Gitleaks: missing; export is blocked until installed (see docs/capture-workflow.md).'
            fi
            ;;
        capture|compare) "$python_cmd" "$repo_dir/scripts/$action.py" "$@" ;;
        init-export|export)
            "$python_cmd" "$repo_dir/scripts/export.py" "$action" "$@"
            ;;
        *) print -u2 'Usage: zsh dotfiles.zsh {doctor|capture|compare|init-export|export} [arguments]'; return 2 ;;
    esac
}

main "$@"
