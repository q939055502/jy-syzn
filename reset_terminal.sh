#!/bin/bash
# 重置终端环境脚本
export VIRTUAL_ENV="/opt/jy-syzn/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
export PS1="(venv) [\u@\h \W]\$ "
unset _OLD_VIRTUAL_PS1

