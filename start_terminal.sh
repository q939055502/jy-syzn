#!/bin/bash
# 自定义终端启动脚本
cd /opt/jy-syzn
unset VIRTUAL_ENV
unset _OLD_VIRTUAL_PS1
PS1="[\u@\h \W]\$ "
source venv/bin/activate

