setopt histignorealldups                # Ignore duplicate commands
setopt sharehistory                     # Share history between sessions

HISTSIZE=1000                           # max number of cmds in the history buffer
SAVEHIST=1000                           # max number of cmds in the history file
HISTFILE=~/.zsh_history                 # History file
ZSH_DISABLE_COMPFIX="true"              # Disable compfix

source ~/.config/.shell_exports         # Load exports
#source ~/.config/.shell_exports_private # Load exports
source ~/.config/.shell_alias           # Load aliases
source ~/.config/.shell_completers      # Load completers
source ~/.config/.shell_utils           # Load utils

eval "$(starship init zsh)"             # Use starship prompt
#eval "$(thefuck --alias)"               # Use thefuck
#eval "$(gh completion -s zsh)"          # Use gh completion

# Set up the prompt

autoload -Uz promptinit
# Use emacs keybindings even if our EDITOR is set to vi
bindkey -e
# Use modern completion system
autoload -Uz compinit
compinit

