#!/usr/bin/env bash

# 判断是否为root用户
if [[ $EUID -ne 0 ]]; then
    echo "请使用root账户运行该脚本"
    exit 1
fi

# 安装docker-ce和依赖
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/debian/gpg | apt-key add -
echo 'deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/debian buster stable' > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce -y && apt install build-essential libbz2-dev zlib1g-dev libffi-dev libssl-dev libreadline-dev libsqlite3-dev -y

# 更换为中科大仓库镜像
echo '{"registry-mirrors": ["https://docker.mirrors.ustc.edu.cn/"]}' > /etc/docker/daemon.json
systemctl enable docker
systemctl start docker

# 安装pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# 使用pyenv淘宝镜像源安装python3.8.2
wget https://npm.taobao.org/mirrors/python/3.8.2/Python-3.8.2.tar.xz -P ~/.pyenv/cache/;pyenv install 3.8.2
pyenv global 3.8.2

# 更换为pypi清华镜像
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装docker-compose
pip3 install docker-compose

# 安装pipenv
pip3 install pipenv
pipenv install

# 下载所需的镜像
docker pull ap0llo/oneforall:0.1.0
docker pull ap0llo/nmap:7.80
docker pull ap0llo/dirsearch:0.3.9
docker pull ap0llo/poc:xunfeng
docker pull ap0llo/poc:kunpeng
docker pull ap0llo/poc:bugscan
docker pull mongo:4.1

# 运行数据库并初始化poc
docker-compose up -d

# 结束
echo "OK"
