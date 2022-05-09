import time, math
from smbus2 import SMBus, i2c_msg
from datetime import datetime

import LTC2499



if __name__ == '__main__':
    i2c = SMBus(0)

    adc1 = LTC2499(i2c, V_ref= 3.244, V_com= 1.62, Address= 0x76)
    adc2 = LTC2499(i2c, V_ref= 3.244, V_com= 1.62, Address= 0x74)

    adc1.init()
    adc2.init()

    while True:
        adc1.read()
        adc2.read()
        time.sleep(2)
        print(adc1.get_temperature())
        print(adc2.get_temperature())