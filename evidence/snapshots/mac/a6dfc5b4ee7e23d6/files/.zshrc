setopt histignorealldups                # Ignore duplicate commands
setopt sharehistory                     # Share history between sessions

HISTSIZE=1000                           # max number of cmds in the history buffer
SAVEHIST=1000                           # max number of cmds in the history file
HISTFILE=~/.zsh_history                 # History file
ZSH_DISABLE_COMPFIX="true"              # Disable compfix

autoload -Uz run-help

source ~/.config/.shell_exports         # Load exports
#source ~/.config/.shell_exports_private # Load exports
source ~/.config/.shell_alias           # Load aliases
source ~/.config/.shell_completers      # Load completers
source ~/.config/.shell_completers_openclaw
source ~/.config/.shell_utils           # Load utils

eval "$(starship init zsh)"             # Use starship prompt
#eval "$(thefuck --alias)"               # Use thefuck
eval "$(gh completion -s zsh)"          # Use gh completion

# OpenClaw Completion
#source "__LOCAL_PATH_2__"

# Created by `pipx` on 2026-02-18 02:04:41
export PATH="$PATH:__LOCAL_PATH__"


export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && . "/opt/homebrew/opt/nvm/nvm.sh"
[ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && . "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"

# nanobrew
export PATH="/opt/nanobrew/prefix/bin:$PATH"
