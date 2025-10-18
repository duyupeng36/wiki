FROM 35dn2jjh8x8qtf.xuanyuan.run/duyupeng/ubuntu:24.04


# 创建工作目录 /wiki
RUN mkdir /wiki

# 拷贝当前目录的内容到 /wiki
ADD . /wiki

# 设置工作目录
WORKDIR /wiki

# entrypoint.sh 添加执行全新
# RUN chmod +x /wiki/entrypoint.sh

# 安装 gitbook-cli
RUN npm install -g gitbook-cli \
&& gitbook init \
&& gitbook install \
&& gitbook build 

WORKDIR /wiki/_book

ENTRYPOINT ["python3", "-m", "http.server"]
CMD ["4000"]