# 旅行者探测器系统

**项目正在快速迭代中，请即时更新源代码 https://github.com/ody5sey/Voyager/**
![旅行者2号](img/Voyager.jpg)

##  0x01 功能介绍
作为一个渗透人员，在每次渗透网站的时候都要拿出一堆黑客工具，比如nmap, awvs, 御剑等工具进行测试，由于实在厌烦了一些低级重复性的工作，趁着2020年新年创建了一个工具集合平台，将渗透测试常见的域名扫描，端口扫描，目录扫描，漏洞扫描的工具集合在一起

目前平台还在持续开发中，肯定有不少问题和需要改进的地方，欢迎大佬们提交建议和Bug，也非常欢迎各位大佬Star或者是Fork

![展示](img/img0.png)

## 0x02 系统结构

### 开发框架

基础语言: **Python(3.8.1)**

Web框架: **Flask(1.1.1)**

数据库: **Mongodb**

逻辑处理: **Docker**

前端: **Layui**

### 数据载入

数据流入有两种方式，一种是从WEB界面引入，还有一种是从上级任务引入，比如说端口扫描任务的IP既可以从WEB页面引入，也可以从域名扫描处获得。漏洞扫描的任务只能从端口扫描和域名扫描的任务中引入


## 0x02 功能介绍

### 0x001 域名扫描
采用的是[oneforall](https://github.com/shmilylty/OneForAll)，当前使用的版本是0.0.9,我修改了部分代码，使得工具和平台能够结合


![](img/img5.png)

### 0x002 端口扫描
程序采用的是[masscan](https://github.com/robertdavidgraham/masscan)和[nmap](https://github.com/nmap/nmap)结合的方式，先用masscan扫描开放的端口，然后再用nmap对开放的端口进行详细的信息探测，
这步是最重要的一步，通过nmap给端口打上标签，为以后的POC扫描提供数据，由于nmap只能识别广义的操作系统，中间件，数据库三层结构，再往上的web应用nmap无法识别，只能通过接下来的cms识别给web应用程序打标签

### 0x003 目录扫描
目录扫描采用的工具是[dirsearch](https://github.com/maurosoria/dirsearch),排除了部分bug并且扩充了字典然后进行封装

### 0x004 指纹识别
指纹识别采用的是新潮团队的[TideFinger](https://github.com/TideSec/TideFinger), 我提取出了TideFinger的指纹进行比对，原先TideFinger是单任务运行多线程请求的方式，为了配合框架我改成了多任务并发单线程请求的方式，由于Python3和Python2在字符编码上存在差异，导致相同的字符串可能会计算出不同的MD5值，这个指纹识别的库以后需要大量修改

导出的扫描结果
![扫描结果](img/img1.png)

### 0x005 漏洞扫描
漏洞扫描功能现在引入了xunfeng和kunpeng的poc，一共144个，标签以nmap的标签为主，比如445端口的标签是microsoft-ds， 3389的标签是ms-wbt-server。这两个框架合并存在一定问题，比如说:xunfeng和kunpeng的poc主要针对非WEB应用，两个框架的POC存在重复的问题.我做了一定的去重工作，后期随着POC的增多，去重会是一个问题

**漏洞扫描的任务只能从端口扫描和指纹识别的数据中继承，也就是说必须完成端口扫描或者是指纹识别才能获取到数据**

### 0x006 WAF探测
分析了一下sqlmap的源代码，从中提取出了sqlmap用于WAF探测的代码并进行了封装, 用来探测类http端口是否有WAF保护，此功能并未在前台展示，一些模块比如目录扫描会自动进行调用

### 0x007 主动扫描

**此功能暂时处于冻结状态,我正在测试AWVS13的API**

主动扫描用的是AWVS12，已经封装在Docker里了，通过AWVS12的restful进行API调用

## 0x03 安装教程

这里以Kali linux 2019.4作为基础操作系统



### 0x001 下载源码安装

我把步骤都写在run.sh里了，理论上run.sh适应于Debian系操作系统(包括Debian, Kali, Ubuntu)

```bash
git clone https://github.com/ody5sey/Voyager.git
cd Voyager
bash run.sh
```

国内用户建议运行debian_run.sh，会使用国内源进行安装

```bash
git clone https://github.com/ody5sey/Voyager.git
cd Voyager
bash debian_run.sh
```

红帽系操作系统(包括redhat, fedora, centos)请用redhat_run.sh

```bash
git clone https://github.com/ody5sey/Voyager.git
cd Voyager
bash redhat_run.sh
```


### 0x002 运行

```bash
source ~/.bashrc
pipenv shell
python manager.py
```

运行后没有默认用户

请访问http://127.0.0.1:5000/add 以添加新用户

或使用 curl http://127.0.0.1:5000/add

然后访问 http://127.0.0.1:5000/ 登录即可

默认的用户名和密码是luffy:s1riu5


![展示](img/img4.png)

正式开始前需要先创建一个项目

## 0x04 时间参数

**域名扫描**: 开启了爆破模式，一个域名大约需要6分钟

**端口扫描**: 服务器环境中百兆宽带内网测试将全C端，全端口的扫描压缩到10分钟之内，但是家用路由器根本无法承受如此巨大的负载，只好限制速度。现在单IP全端口扫描时间不到一分钟

**目录扫描**: 四个字典单个目标6分钟

## 0x05 TODO

权当是立FLAG吧

### 功能更新

- [ ] POC框架中引入bugscan和beebeeto，以改善针对WEB应用扫描不全的问题，这样四个主流POC框架的POC数量总计有1500+
- [ ] 引入AWVS12，首先对类http标签进行WAF测试,没有WAF保护的WEB应用将推送给AWVS检测
- [ ] 引入被动扫描器XRAY，和之前AWVS的一样，没有WAF保护的WEB应用将用AWVS的爬虫和xray进行检测
- [ ] 引入IP代理功能，为部分模块添加代理参数
- [ ] 引入Metasploit, 可以调用metasploit接口
- [ ] 引入爆破功能，本来想用hydra实现的，但是发现效果并不是很好，现在比较倾向于写爆破组件然后以插件的形式载入
- [ ] 引入一键日站功能，在输入IP地址或者是域名之后自动依次载入攻击组件
- [ ] 引入微信接口，从微信载入攻击目标然后后台自动攻击

### 长期更新

- [ ] 各组件的协调优化以及BUG修复, 漏报，误报的修复
- [ ] 指纹库的更新和poc库的更新

### 0x06 Q&A

一. 为什么域名扫描添加任务之后长时间不动

关于单个任务进度条的说明:ap0llo/oneforall:0.0.8采用的是oneforall:0.0.8版本。还是存在单个任务进度统计的，但是ap0llo/oneforall:0.0.9由于oneforall代码结构的变化，无法将爆破任务的进度数据分离出来，所以无法统计，在200M宽带下，单个域名扫描任务需要时间最长六分钟，从0.00%直接跳到100.00%


二. 为什么漏洞扫描无法添加数据

漏洞扫描采用的是POC扫描，要想扫描端口或者是网站必须有标签，比如21端口是"ftp", 22端口是"ssh",poc要根据这些标签才能扫描，这也意味着POC扫描必须在端口扫描和指纹识别之后，当有端口扫描或者是指纹识别的任务完成之后就能在漏洞扫描下面看到任务列表了


三. 为什么扫描这么慢

扫描速度受限与网速和系统本身的硬件性能，不建议在虚拟机(vmware,virtualbox, pd)上跑,虚拟网卡有性能损失


四. 为什么端口扫描很慢

在这个框架下，性能测试的极限是百兆内网全C段，全端口扫描需要时间是10分钟，但是考虑到个人的宽带和家用路由性能，全速扫描的话，路由器分分钟瘫痪，所以我将性能进行了大幅压缩，所以端口扫描的时间变长了


五. 为什么漏洞扫描没有扫描到漏洞

现在漏洞扫描用的144个POC，来自于xunfeng和kunpeng，这两个框架检测不到扫描器也检测不到，我正在测试其他的POC框架
