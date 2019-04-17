# DCcron
DCcron是区块链的一个辅助性工具，基于django 2开发，支持binance,okex,huobipro等上百个平台，提供了定投和条件投两大功能:一个追求长期价值，看好未来，佛系坚守;一个追求最大价值，助你低进高出，游刃有余。
## 功能说明：
- __定投__
- __条件投__
## 配置文件：
settings.py
## 安装配置：
(注：因某种原因，请在国外网络环境下运行或配置http代理）<br>
一、源码方式安装(调测用）<br>
要求：python3.6+<br>
建议系统环境：CentOS 6+/Ubuntu 14+

1.安装MySQL 5.6+数据库。<br>
建立数据库和用户：<br>
create database dccron character set utf8;<br>
grant all privileges on dccron.\* to dccron@'localhost' identified by 'dccron';<br>
flush privileges;<br>


2.下载项目源码<br>
git clone https://github.com/496080199/dccron.git<br>
或使用zip包下载<br>

3.安装python3依赖<br>
安装pip工具，具体网上搜索(下载配置加速可参见https://pypi-mirrors.org/ ）<br>
cd dccron<br>
pip install -r requirements.txt<br>
依赖安装过程遇到问题请自行查找网上寻找解决方法<br>

4.配置修改<br>
再cd dccron目录，复制settings.py.conf为config.py<br>
默认配置即可，可根据自己的环境进行相应修改其他配置参数<br>

5.初始化数据<br>
返回项目根目录，顺序执行以下命令<br>
python3 manage.py makemigrations<br>
python3 manage.py migrate<br>
python3 manage.py loaddata initial_data.yaml<br>

5.启动运行<br>
返回项目根目录，执行命令<br>
python3 manage.py runserver 0.0.0.0:8000<br>



6.访问<br>

http://(部署服务器IP):8000/<br>
初始帐号密码：admin/admin<br>
注：防火墙端口8000需要放开<br>

二、Docker方式安装(生产用）<br>
1.安装docker环境<br>
自行上网查找<br>
2.配置外部数据库<br>
使用第三方MySQL数据库或自建数据库配置账号密码<br>
3.下载镜像<br>
docker pull 496080199/dccron<br>
4.启动镜像<br>
1)首次启动（安装初始数据）<br>
docker run -d -p 80:80 -e "DCINIT=1" -e "DBHOST=(数据库IP)" -e "DBNAME=(数据库名)" -e "DBUSER=(数据库账号)" -e "DBPASS=(数据库密码)" 496080199/dccron<br>
2)正常启动<br>
docker run -d -p 80:80 -e "DBHOST=(数据库IP)" -e "DBNAME=(数据库名)" -e "DBUSER=(数据库账号)" -e "DBPASS=(数据库密码)" 496080199/dccron<br>
5.访问<br>
http://(部署服务器IP):80/<br>
初始帐号密码：admin/admin<br>
注：防火墙端口80需要放开<br>

<br>
## 使用说明：<br>
1.（可选）进入代理管理，配置http代理<br>
2.进入交易所，更新最新的交易所列表，配置对应平台的API_KEY和并SECRET_KEY，并启用（请自行去对应平台申请）<br>
3.进入交易所查看支持交易对，更新最新的交易对列表，将需要的交易对点击添加<br>
4.进入定投，添加定投任务，根据crontab设置时间，选择交易对，每期投入量，及增长百分百，完成后加载启动任务<br>
5.进入条件投，添加条件投任务，，选择交易对，交易方向，价格与数量，完成后加载启动任务<br>
<br>
## 欢迎捐赠：<br>
<p>BTC地址：18Fd9TBMnqAA4BEeEtHvzKZ3phwE5xVrcr</p>
<p>ETH地址：0x8b74e2a75ce6e80663f24fcfd0e48c3eb4b4cae2</p>
<p>EOS地址：cljcljcolden</p>
<p>USDT地址：18JSQhT6XMQZpbzxjjt4jpwznrAnFpcAU3</p>
<br>
## 系统演示:<br>
https://dccron.xiaopao.tk<br>
账号密码：admin/admin<br>
## 声明:<br>
本系统为开源项目，仅供学习研究，技术交流，希望能抛砖引玉。可免费参考或使用系统，但因此产生各种风险损失，概不负责。<br>
<br>
<p>tg社区交流：https://t.me/DCcron</p>
