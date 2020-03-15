#!/usr/bin/env bash

yum remove -y docker docker-common docker-selinux docker-engine
yum install -y yum-utils gcc git libffi-devel device-mapper-persistent-data lvm2 wget zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel libpcap-devel xz-devel
wget -O /etc/yum.repos.d/docker-ce.repo https://download.docker.com/linux/centos/docker-ce.repo
sed -i 's+download.docker.com+mirrors.tuna.tsinghua.edu.cn/docker-ce+' /etc/yum.repos.d/docker-ce.repo
yum makecache fast
yum install -y docker-ce

mkdir /etc/docker
echo '{"registry-mirrors": ["https://docker.mirrors.ustc.edu.cn/"]}' > /etc/docker/daemon.json
systemctl restart docker
systemctl enable docker


# 安装pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# 使用pyenv淘宝镜像源安装python3.8.1
wget https://npm.taobao.org/mirrors/python/3.8.1/Python-3.8.1.tar.xz -P ~/.pyenv/cache/;pyenv install 3.8.1
pyenv global 3.8.1

# 更换为pypi清华镜像
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装pipenv
pip3 install pipenv
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

