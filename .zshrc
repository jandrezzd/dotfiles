# Autocompletado
autoload -Uz compinit promptinit
compinit
promptinit

# Alias
alias ls='ls --color=auto'
alias grep='grep --color=auto'

# Prompt personalizado
PS1='%F{cyan} 󰌽 %1~%f%F{green} %f%F{white} %f'

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Ubicación del archivo de historial
HISTFILE=$HOME/.zsh_history

# Cantidad de líneas a recordar en memoria
HISTSIZE=10000

# Cantidad de líneas a guardar en el archivo
SAVEHIST=10000

# Opciones para el manejo del historial
setopt APPEND_HISTORY        # Agrega en vez de sobrescribir
setopt HIST_IGNORE_DUPS      # No guarda comandos duplicados seguidos
setopt HIST_IGNORE_SPACE     # No guarda comandos que empiecen con espacio
setopt SHARE_HISTORY         # Comparte historial entre distintas sesiones

# Created by `pipx` on 2025-09-10 21:59:51
export PATH="$PATH:/home/seven/.local/bin"

# Pywal
(cat ~/.cache/wal/sequences &)
