# sensor_supervise 

### 树莓派4B温湿度传感器dht11数据检测 
### monitor the data of temperature and humidity sensor dht11 for raspberry pi 4B 
  
课业需求做个demo出来玩玩， 觉得好用不妨点个Star谢谢

## 介绍  
通过树莓派4B获取一天内的室温以及湿度，用txt文件进行相应保存，同时将温度数据提取出来进行可视化显示。

目前是PC做服务端和客户端，树莓派做数据接受器。当然也可以都放树莓派中，但要做相应的修改

1. 只用Django进行了逻辑处理，简便可用  
2. 树莓派数据接收端和服务端分离，减少代码耦合

## 配置部署
### Step 0
- 树莓派 4B 1个 
- DHT11型号温湿度传感器 1个
- PC 一台

### Step 1 PC端
1. 安装Django```pip install Django```
2. 安装REST Framework```pip install djangorestframework```
3. 在项目根目录下执行如下命令进行Django的基本配置
    ```
    python manage.py migrate # 初始化数据库
    python manage.py makemigrations sensor_data # 激活数据库模型
    python manage.py createsuperuser # 创建管理员(输入对应账号密码即可)
    python manage.py runserver 0.0.0.0:8000 # 在8000端口监听所有服务器的公开IP
    ```
### Step 2 树莓派4B
1. 将dht11_data.py文件放到树莓派4b中直接运行```python dht11_data.py```即可

**注意！！！**  如果需要进行定时检测数据，比如一个小时检测一次，则可运行如下命令：
```
crontab -e 
0 * * * * python /usr/local/dht11/dht11_data.py 
# 把这个命令加入crontab到最后一行 目录根据自己文件位置自行修改
sudo /etc/init.d/cron restart
```

[参照文章](https://zhuanlan.zhihu.com/p/270196679)

