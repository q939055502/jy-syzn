#!/bin/bash
# 重置终端环境
unset VIRTUAL_ENV
unset _OLD_VIRTUAL_PS1
PS1="[\u@\h \W]\$ "
exec bash

