#!/bin/bash
# 加载环境变量
source ~/.bashrc

# 切换到工作目录
cd /wiki/_book

# 启动 HTTP 服务器
exec python3 -m http.server 4000
