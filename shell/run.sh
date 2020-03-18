#!/usr/bin/env bash

# 安装docker和依赖
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
echo 'deb [arch=amd64] https://download.docker.com/linux/debian buster stable' > /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce -y && apt install build-essential libffi-dev libbz2-dev libssl-dev libreadline-dev libsqlite3-dev -y
systemctl enable docker
systemctl start docker

# 准备Python环境
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.8.1
pyenv global 3.8.1
pip install pipenv
pipenv install


# 下载所需的镜像
docker pull ap0llo/oneforall:0.0.9
docker pull ap0llo/nmap:7.80
docker pull ap0llo/dirsearch:0.3.9
docker pull ap0llo/poc:xunfeng
docker pull ap0llo/poc:kunpeng
docker pull ap0llo/poc:bugscan
docker pull mongo:4.1

# 运行数据库
docker run --rm -d -p 127.0.0.1:27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=shad0wBrok3r mongo:4.1


# 初始化xunfeng镜像
docker run --rm --network="host" ap0llo/poc:xunfeng init

# 初始化kunpeng镜像
docker run --rm --network="host" ap0llo/poc:kunpeng init

# 初始化bugscan镜像
docker run --rm --network="host" ap0llo/poc:bugscan init

# 结束
echo "OK"
