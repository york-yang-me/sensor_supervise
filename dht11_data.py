import datetime
import json
import requests
import time

import RPi.GPIO as GPIO

data = []  # 用来存放读取到的数据
channel = 2  # DHT11的data引脚连接到的树莓派的GPIO引脚，使用BCM编号 这边我的数据引脚对应物理引脚的3号位
temperature_sum = 0  # 用来存放单次执行程序获取温度后的温度值总和
count = 0  # 用来判断记载了几次有效数据


# 微秒级延时函数
def delayMicrosecond(t):
    start, end = 0, 0  # 声明变量
    start = time.time()  # 记录开始时间
    t = (t - 3) / 1000000  # 将输入t的单位转换为秒，-3是时间补偿
    while end - start < t:  # 循环至时间差值大于或等于设定值时
        end = time.time()  # 记录结束时间


# 延迟分析函数
def analyzeDelay(t):
    end_time = time.time()  # 记录结束时间
    if (end_time - t) > 0.1:  # 判断循环时间是否超过0.1秒，避免程序进入死循环卡死
        return True


# 信号分析函数
def analyzeSignal():
    GPIO.setup(channel, GPIO.OUT)  # 设置GPIO口为输出模式
    GPIO.output(channel, GPIO.HIGH)  # 设置GPIO输出高电平
    delayMicrosecond(10 * 1000)  # 延时10毫秒
    GPIO.output(channel, GPIO.LOW)  # 设置GPIO输出低电平
    delayMicrosecond(25 * 1000)  # 延时25毫秒
    GPIO.output(channel, GPIO.HIGH)  # 设置GPIO输出高电平
    GPIO.setup(channel, GPIO.IN)  # 设置GPIO口为输入模式
    start_time = time.time()  # 记录循环开始时间
    while GPIO.input(channel):  # 一直循环至输入为低电平
        if analyzeDelay(start_time):  # 判断循环时间是否超过0.1秒，避免程序进入死循环卡死
            break  # 跳出循环

    start_time = time.time()
    while GPIO.input(channel) == 0:  # 一直循环至输入为高电平
        if analyzeDelay(start_time):
            break

    start_time = time.time()
    while GPIO.input(channel):  # 一直循环至输入为低电平
        if analyzeDelay(start_time):
            break

    for i in range(40):  # 循环40次，接收温湿度数据
        start_time = time.time()
        while GPIO.input(channel) == 0:  # 一直循环至输入为高电平
            if analyzeDelay(start_time):
                break

        delayMicrosecond(28)  # 延时28微秒

        if GPIO.input(channel):  # 超过28微秒后判断是否还处于高电平
            data.append(1)  # 记录接收到的bit为1

            start_time = time.time()
            while GPIO.input(channel):  # 一直循环至输入为低电平
                if analyzeDelay(start_time):
                    break
        else:
            data.append(0)  # 记录接收到的bit为0


# 解码
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


for i in range(10):
    # 记录10次数据
    GPIO.setmode(GPIO.BCM)  # 设置为BCM编号模式
    GPIO.setwarnings(False)
    del data[0:]  # 删除列表
    time.sleep(1)  # 延时1秒

    analyzeSignal()

    humidity_bit = data[0:8]  # 分隔列表，第0到7位是湿度整数数据
    humidity_point_bit = data[8:16]  # 湿度小数
    temperature_bit = data[16:24]  # 温度整数
    temperature_point_bit = data[24:32]  # 温度小数
    check_bit = data[32:40]  # 校验数据

    humidity_int = 0
    humidity_point = 0
    temperature_int = 0
    temperature_point = 0
    check = 0

    for i in range(8):  # 二进制转换为十进制
        humidity_int += humidity_bit[i] * 2 ** (7 - i)
        humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
        temperature_int += temperature_bit[i] * 2 ** (7 - i)
        temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
        check += check_bit[i] * 2 ** (7 - i)

    humidity = humidity_int + humidity_point / 10
    temperature = temperature_int + temperature_point / 10

    check_data = humidity_int + humidity_point + temperature_int + temperature_point

    if check == check_data and temperature != 0 and humidity != 0:  # 判断数据是否正常
        print("temperature :", temperature, "*C, humidity :", humidity, "%")
        if 20 <= temperature <= 40:  # 判断温度是否正常(有时可能会因为传感器等不可控因素输出异常温度)
            res = '{temperature:%.1f}' % temperature
            temperature_sum += temperature
            count += 1
        import json

        with open('data.txt', 'a') as outfile:
            json.dump(res, outfile)
        out_test = open('data.txt', 'a')
        out_test.write(res)
        out_test.close
    else:
        print("error")

    time.sleep(1)
    GPIO.cleanup()

# Post Data to webpage
rqs_headers = {'Content-Type': 'application/json'}
req_url = 'http://192.168.0.108:8000/sensor_data/temperature_api/'
new_data = {
    "capTime": datetime.datetime.now(),
    "capTemperature": '%.1f' % (temperature_sum / count)
}

test_data = json.dumps(new_data, cls=ComplexEncoder)

response = requests.post(url=req_url, headers=rqs_headers, data=test_data)

temperature_sum = 0  # 运算结束后置0
count = 0
