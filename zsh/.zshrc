zstyle ':completion:*' list-colors "${(@s.:.)LS_COLORS}"
zstyle ':completion:*' menu select
zstyle ':completion:*' rehash true
zstyle ':completion:*:matches'         group 'yes'
zstyle ':completion:*'                 group-name ''
zstyle ':completion:*' list-dirs-first true

# Prevent autocompleting to a different parent directory when
# the child does not exist.
#
# Ex.
# /a1/other
# /a2/file
#
# Without this option, `cd a1/f` would complete to `a2/file`.
# That's annoying.
zstyle ':completion:*' accept-exact-dirs true

autoload -U colors && colors
autoload -U compinit
autoload -U add-zsh-hook

HISTSIZE=100000
SAVEHIST=100000
HISTFILE=~/.zhistory

setopt hist_no_store
setopt hist_ignore_all_dups
setopt hist_ignore_space
setopt inc_append_history
setopt share_history
setopt auto_pushd
setopt null_glob

unsetopt correct_all

bindkey "^[[A" history-beginning-search-backward
bindkey "^[[B" history-beginning-search-forward

# Fixes up+down history completion in certain situations.
# Replicate:
#   1. ssh into a remote machine and launch tmux
#   2. kill the session from the remote machine
#   3. attempt using partial completion (enter `ls ` and press up)
#
# ---
# Notes:
#
# https://espterm.github.io/docs/VT100%20escape%20codes.html
# `setcursor DECCKM      Set cursor key to cursor               ^[[?1l`
#
add-zsh-hook precmd set_cursor_key_to_cursor
set_cursor_key_to_cursor () {
    printf '\e[?1l'
}

# change otherwriteable to more-readable blue txt, black background
export LS_COLORS='rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=01;34:st=37;44:ex=01;32:*.7z=01;31:*.ace=01;31:*.alz=01;31:*.apk=01;31:*.arc=01;31:*.arj=01;31:*.bz=01;31:*.bz2=01;31:*.cab=01;31:*.cpio=01;31:*.crate=01;31:*.deb=01;31:*.drpm=01;31:*.dwm=01;31:*.dz=01;31:*.ear=01;31:*.egg=01;31:*.esd=01;31:*.gz=01;31:*.jar=01;31:*.lha=01;31:*.lrz=01;31:*.lz=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.lzo=01;31:*.pyz=01;31:*.rar=01;31:*.rpm=01;31:*.rz=01;31:*.sar=01;31:*.swm=01;31:*.t7z=01;31:*.tar=01;31:*.taz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tgz=01;31:*.tlz=01;31:*.txz=01;31:*.tz=01;31:*.tzo=01;31:*.tzst=01;31:*.udeb=01;31:*.war=01;31:*.whl=01;31:*.wim=01;31:*.xz=01;31:*.z=01;31:*.zip=01;31:*.zoo=01;31:*.zst=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:';
alias ls='ls --color=auto --group-directories-first'
alias diff='diff --color=auto'

setopt PROMPT_SUBST

insert_mode_color='magenta'
default_mode_color='green'
vi_mode_color=$default_mode_color

prompt_user='%F{green}%n%f'
prompt_separator='%F{black}.%f'
prompt_current_dir='%F{cyan}%~%f'
if [ -n "$SSH_TTY" ] && [ -z "$TMUX" ]; then
    prompt_host='%m'
else
    prompt_host=''
fi

PROMPT='%F{$vi_mode_color}$prompt_host\$%f '
RPROMPT="$prompt_current_dir"

# hide when start typing
setopt TRANSIENT_RPROMPT

bindkey -v

KEYTIMEOUT=1

function zle-line-init zle-keymap-select {
    vi_mode_color="${${KEYMAP/vicmd/$insert_mode_color}/(main|viins)/$default_mode_color}"
    zle reset-prompt
}

zle -N zle-line-init
zle -N zle-keymap-select

fpath=("$DOTFILES/zsh/functions" "$fpath[@]")

host_dir="$DOTFILES/zsh/hosts/$HOST_DOTFILES"
if [ -r "$host_dir/.zshrc" ]; then
    . "$host_dir/.zshrc"
fi
if [ -d "$host_dir/functions" ]; then
    fpath=("$host_dir/functions" "$fpath[@]")
fi
unset host_dir

for plugin in "$DOTFILES"/zsh/plugins/*/.zshrc(N); do
    . "$plugin"
done

compinit -C

zsh_reload_comp() {
    rm -f ~/.zcompdump
    zsh -ic "echo -n"
}

all_commands() {
    autoload -Uz bashcompinit
    bashcompinit
    compgen -c | sort -u
}

PROMPT_EOL_MARK=''

# ensures tmux opens in the symlink pwd instead of the resolved link
pwd_osc_7() {
    printf '\033]7;%s\033\\' "$PWD" > /dev/tty
}
add-zsh-hook chpwd pwd_osc_7
pwd_osc_7

# allows backspace to work properly when exiting vim mode
bindkey '^?' backward-delete-char
bindkey '^H' backward-delete-char
export PATH=/Users/andrewr/.local/bin:$PATH
