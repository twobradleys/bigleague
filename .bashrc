export PS1="\[\033[48;5;95;38;5;214m\] [bigleague] \u@\h \[\033[0;38;5;31;48;5;240;22m\] \$git_branch\$git_dirty \[\033[0;38;5;252;48;5;240;1m\]\$PWD \[\033[0;38;5;240;49;22m\]\[\033[0m\] "
bind '"\C-i": menu-complete' 2> /dev/null
alias ls='ls -G -a -l -tr --color'
