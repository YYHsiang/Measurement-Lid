import time, math

from smbus2 import SMBus, i2c_msg
from datetime import datetime

#TODO clamp detection

class LTC2499:
    '''Data Out:
        Byte #1                                     Byte #2
        START  SA6 SA5 SA4 SA3 SA2 SA1 SA0 R SACK   SGN MSB D23 D22 D21 D20 D19 D18 MACK
        
        Byte #3                                Byte #4
        D17 D16 D15 D14 D13 D12 D11 D10 MACK   D9 D8 D7 D6 D5 D4 D3 D2
        
        Byte #5
        MACK D1 D0 SUB5 SUB4 SUB3 SUB2 SUB1 SUB0 MNACK STOP'''
    def __init__(self, i2c, V_ref:float, V_com:float, Address:int) -> None:
        self.temp_data = [] # Temperature data

        self.V_ref = V_ref # Reference voltage = REF+ - REF- = Vcc
        self.V_com = V_com # Common voltage

        self.RES_10K = 10 # k Ohm
        self.B_CONSTANT = 3977
        self.ROOM_TEMP = 25 + 273.15
        self.RES_NTC_ROOM_TEMP = 10 # k Ohm

        self.i2c = i2c
        self.i2c_address = Address #LTC2449 address

        self.EN = 0b1
        self.SGL = 0b1
        self.Channel = 0b0000 # ODD + A2 A1 A0
        
        self.EN2 = 0b1
        self.IM = 0b0
        self.FA = 0b1
        self.FB = 0b0
        self.SPD = 0b0

    def init(self):
        self.EN = 0b1
        self.SGL = 0b1
        self.Channel = 0b0000 # ODD + A2 A1 A0

        self.EN2 = 0b1
        self.IM = 0b0
        self.FA = 0b1
        self.FB = 0b0
        self.SPD = 0b0

        config_data = [(0b10 << 6) | (self.EN << 5) | (self.SGL << 4) | self.Channel]
        config_data.append( (self.EN2 << 7) | (self.IM << 6) | (self.FA << 5) | (self.FB << 4) | (self.SPD << 3))
        for byte in config_data:
            print("{:b}".format(byte))
        #self.i2c.write_i2c_block_data(self.i2c_address, 0, config_data)
        msg = i2c_msg.write(self.i2c_address, config_data)
        self.i2c.i2c_rdwr(msg)

    def get_temperature(self):
        return self.temp_data
    
    # Clear Temperature Data
    def clear_temperature(self): 
        self.temp_data = []

    def read(self):
        # read data
        rawData= i2c_msg.read(self.i2c_address, 4)
        self.i2c.i2c_rdwr(rawData)

        # convert data into temperature
        full, temp_bin, clamp = self.List2Bin(list(rawData))
        temp_bin = self.Bin2Vol(temp_bin)
        if(temp_bin <= 0):
            temp_c = None
        else:
            temp_c = self.Vol2Temp(temp_bin)
        
        # store data
        self.temp_data.append(temp_c)

    def setChannel(self, channel):
        print(str(datetime.now().time()) + " --> " + "setChannel: " + str(channel))
        
        self.EN = 0b1
        self.SGL = 0b1
        self.Channel = (channel%2 << 3) | int(channel/2)

        config_data = [(0b10 << 6) | (self.EN << 5) | (self.SGL << 4) | self.Channel]
        msg = i2c_msg.write(self.i2c_address, config_data)
        self.i2c.i2c_rdwr(msg)
        #print(str(datetime.now().time()) + " --> " + "config: " + str(list(msg)))

    def List2Bin(self, input_list:list):
        '''convert [Byte3, Byte2, Byte1, Byte0] 

            @return: full_data= [Byte3 << 8*3 | Byte2 << 8*2 | Byte1 << 8*1 | Byte0]
            @return: temp_data= bit 30(MSB)~ 6(LSB)
            @return: clamp_flag= Vin >= FS or Vin <=-FS
        '''
        full_data = int(0)
        for index in range(0,len(input_list)):
            full_data |= input_list[index] << (8 * (len(input_list)-1-index))

        temp_data = int(full_data / pow(2,6)) & 0x01ffffff # extract bit 30(MSB)~ 6(LSB)
        temp_data_2s = self.twos_comp(temp_data, 25) # 2's complement

        #TODO: status bit
        clamp_flag = 0

        '''print("full: " + bin(full_data))
        print("temp: " +bin(temp_data))
        print(temp_data_2s)'''

        if((full_data >> 29) == 0b110 or (full_data >> 29) == 0b001):
            clamp_flag = 1
        else:
            clamp_flag = 0
        #print("clamp_flag: " + str(clamp_flag))

        return full_data, temp_data_2s, clamp_flag

    def Bin2Vol(self, ADC_data:int):
        #! why 26 bit? 
        FS = self.V_ref / 2
        voltage =  ADC_data * (FS / pow(2, 24)) + self.V_com

        return voltage

    def Vol2Temp(self, voltage):
        NTC_Res = ( voltage) / ((self.V_ref - voltage) / self.RES_10K)
        K_Temp = 1 / ( (1 / self.ROOM_TEMP) - (math.log(self.RES_NTC_ROOM_TEMP / NTC_Res)) / self.B_CONSTANT)
        C_Temp = K_Temp - 273.15

        return C_Temp
    
    def twos_comp(self, val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val                         # return positive value as is
