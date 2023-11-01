#!/usr/bin/env python3
"""
RPZ-CO2-Sensor拡張基板用サンプルコード
CO2濃度に応じてLEDの色を変化させ, 一定以上ならリレーをONする. 
Indoor Corgi, https://www.indoorcorgielec.com
GitHub: https://github.com/IndoorCorgi/cgsensor
解説ページ: https://www.indoorcorgielec.com/resources/raspberry-pi/co2-monitor/

必要環境:
1) Raspberry Pi OS, Python3
2) I2Cインターフェース
  Raspberry PiでI2Cを有効にして下さい
  https://www.indoorcorgielec.com/resources/raspberry-pi/raspberry-pi-i2c/

3) 拡張基板
  RPZ-CO2-Sensor: https://www.indoorcorgielec.com/products/rpz-co2-sensor/

4) cgsensorパッケージ
  sudo python3 -m pip install -U cgsensor
"""

import time
from datetime import datetime
import json
import requests
import RPi.GPIO as GPIO
import cgsensor

#----------------------------
# カスタマイズ可能なパラメーター

# LEDの色やリレーを切り替えるCO2濃度のしきい値[ppm]
LED_CO2_TH = [
    1000,  # これより低ければ緑
    1500,  # これより低ければ青
    2000,  # これより低ければ黄, これ以上なら赤
]

# リレーをON/OFFするCO2濃度のしきい値[ppm]
# 0を指定するとリレー制御は無効
RELAY_CO2_TH = 0

# しきい値付近でLEDやリレーが頻繁に変化するのを回避するためのマージン
# マージン50ppm, 緑/青のしきい値1000ppmの場合, 1050ppmを超えたら緑->青になり,
# 950ppmを下回ったら青->緑になる. リレーも同様.
CO2_MARGIN = 50

# 次の測定までの待ち時間[分]
INTERVAL = 1
#----------------------------

# RGB LEDの色指定用
COLORS = {'off': 0, 'red': 1, 'green': 2, 'blue': 3, 'yellow': 4, 'purple': 5, 'lightblue': 6, 'white': 7}

# GPIO番号
RELAY = 19  # MOSFETリレーのGPIO番号
LEDR = 18  # 赤色LED GPIO番号
LEDG = 17  # 緑色LED GPIO番号
LEDB = 22  # 青色LED GPIO番号


GPIO.setmode(GPIO.BCM)  # GPIOの準備

# RGB LEDピン出力設定
GPIO.setup(LEDR, GPIO.OUT)
GPIO.setup(LEDG, GPIO.OUT)
GPIO.setup(LEDB, GPIO.OUT)
led_state = 0  # 現在LEDがどの色か. 0:緑, 1:青, 2:黄, 3:赤


def set_rgbled(color=COLORS['off']):
  """
  RPZ-CO2-Sensor基板のRGB LEDを指定の色で光らせるか、消灯する

  Args:
    color: 色を指定. 0-7の数値か, COLORS辞書を使ってCOLORS['red']のように指定する.
  """

  # offの場合は消灯
  if COLORS['off'] == color:
    GPIO.output(LEDR, 0)
    GPIO.output(LEDG, 0)
    GPIO.output(LEDB, 0)
  elif COLORS['red'] == color:
    GPIO.output(LEDR, 1)
    GPIO.output(LEDG, 0)
    GPIO.output(LEDB, 0)
  elif COLORS['green'] == color:
    GPIO.output(LEDR, 0)
    GPIO.output(LEDG, 1)
    GPIO.output(LEDB, 0)
  elif COLORS['blue'] == color:
    GPIO.output(LEDR, 0)
    GPIO.output(LEDG, 0)
    GPIO.output(LEDB, 1)
  elif COLORS['yellow'] == color:
    GPIO.output(LEDR, 1)
    GPIO.output(LEDG, 1)
    GPIO.output(LEDB, 0)
  elif COLORS['purple'] == color:
    GPIO.output(LEDR, 1)
    GPIO.output(LEDG, 0)
    GPIO.output(LEDB, 1)
  elif COLORS['lightblue'] == color:
    GPIO.output(LEDR, 0)
    GPIO.output(LEDG, 1)
    GPIO.output(LEDB, 1)
  elif COLORS['white'] == color:
    GPIO.output(LEDR, 1)
    GPIO.output(LEDG, 1)
    GPIO.output(LEDB, 1)


# 解码
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


set_rgbled(COLORS['off'])

# リレー&LED5ピン出力設定
if RELAY_CO2_TH != 0:
  GPIO.setup(RELAY, GPIO.OUT)
  relay_state = False  # 現在のリレーの状態. TrueならON.
  GPIO.output(RELAY, 0)

scd41 = cgsensor.SCD41()
scd41.stop_periodic_measurement()  # 初期状態がわからないので一度stopコマンド実行
scd41.start_periodic_measurement()  # SCD41測定開始

print('時刻, CO2濃度[ppm]')

try:
  datestr = datetime.now().strftime("%Y/%m/%d %H:%M:%S")  # 現在時刻
  scd41.read_measurement(timeout=40)  # CO2の値を読み出し

  if scd41.co2>0:
      print(datestr + ', {}'.format(scd41.co2))
      res = datestr + ', {}'.format(scd41.co2)

      with open('co2.txt', 'a') as outfile:
          json.dump(res, outfile)
      out_test = open('co2.txt', 'a')
      out_test.write(res)
      out_test.close()
  else:
      print("error")

  # 必要に応じてLEDの色を変更
  led_th = list(LED_CO2_TH)  # マージン込みのしきい値を計算するためにコピー
  for i in range(3):
    if i >= led_state:
      led_th[i] += CO2_MARGIN
    else:
      led_th[i] -= CO2_MARGIN

  if scd41.co2 < led_th[0]:
    if led_state != 0:
      print('値がしきい値をまたいだため, LEDを緑に変更します. ')
    led_state = 0
    set_rgbled(COLORS['green'])
  elif scd41.co2 < led_th[1]:
    if led_state != 1:
      print('値がしきい値をまたいだため, LEDを青に変更します. ')
    led_state = 1
    set_rgbled(COLORS['blue'])
  elif scd41.co2 < led_th[2]:
    if led_state != 2:
      print('値がしきい値をまたいだため, LEDを黄に変更します. ')
    led_state = 2
    set_rgbled(COLORS['yellow'])
  else:
    if led_state != 3:
      print('値がしきい値をまたいだため, LEDを赤に変更します. ')
    led_state = 3
    set_rgbled(COLORS['red'])

  # 必要に応じてリレーの状態を変更
  if RELAY_CO2_TH != 0:
    if relay_state:
      relay_th = RELAY_CO2_TH - CO2_MARGIN
    else:
      relay_th = RELAY_CO2_TH + CO2_MARGIN

    if scd41.co2 > relay_th:
      if not relay_state:
        print('値がしきい値をまたいだため, リレーをONします. ')
      relay_state = True
      GPIO.output(RELAY, 1)
    else:
      if relay_state:
        print('値がしきい値をまたいだため, リレーをOFFします. ')
      relay_state = False
      GPIO.output(RELAY, 0)

  # 一定時間待機
  time.sleep(INTERVAL * 60)

except KeyboardInterrupt:
  # LEDとリレーOFF
  set_rgbled(COLORS['off'])
  if RELAY_CO2_TH != 0:
    GPIO.output(RELAY, 0)

  GPIO.cleanup()

# Post Data to webpage
rqs_headers = {'Content-Type': 'application/json'}
req_url = 'http://127.0.0.1:8000/sensor_data/co2_api'
new_data = {
  "capTime": datestr,
  "capCO2": '{}'.format(scd41.co2),
}
test_data = json.dumps(new_data, cls=ComplexEncoder)

response = requests.post(url=req_url, headers=rqs_headers, data=test_data)


