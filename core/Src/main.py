import time, math
from smbus2 import SMBus, i2c_msg
from datetime import datetime

from LTC2499 import LTC2499
from DataLog import DataLog

if __name__ == '__main__':
    i2c = SMBus(0)

    adc1 = LTC2499(i2c, V_ref= 3.3, V_com= 1.65, Address= 0x76)
    adc2 = LTC2499(i2c, V_ref= 3.3, V_com= 1.65, Address= 0x74)

    adc1.init()
    adc2.init()

    logger = DataLog()
    while True:
        for channel_num in range(0,16):
            time.sleep(0.17)#typical convert time
            adc1.setChannel(channel_num)# set channel
            adc2.setChannel(channel_num)# set channel

            time.sleep(0.17) #typical convert time
            adc1.read()
            adc2.read()
        
        # get Temperature
        temp_adc1 = adc1.get_temperature()
        temp_adc2 = adc2.get_temperature()

        #Clear Temperature data array
        adc1.clear_temperature()
        adc2.clear_temperature()
        
        temp_24 = []
        for index in range(0,15):
            temp_24.append(temp_adc1[index])
            temp_24.append(temp_adc2[index])
        
        print(temp_24) # Terminal output
        logger.write_data(temp_24) # log file: "../../log/"