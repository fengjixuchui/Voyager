#!/usr/bin/env bash

# 安装docker和依赖
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
echo 'deb [arch=amd64] https://download.docker.com/linux/debian buster stable' > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce -y && apt install build-essential libffi-dev zlib1g-dev libbz2-dev libssl-dev libreadline-dev libsqlite3-dev -y
systemctl enable docker
systemctl start docker

# 准备Python环境
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.8.2
pyenv global 3.8.2
pip install pipenv docker-compose
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
