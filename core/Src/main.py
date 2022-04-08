from smbus2 import SMBus

class ADC_LTC2499:
    '''Data Out:
        Byte #1                                     Byte #2
        START  SA6 SA5 SA4 SA3 SA2 SA1 SA0 R SACK   SGN MSB D23 D22 D21 D20 D19 D18 MACK
        
        Byte #3                                Byte #4
        D17 D16 D15 D14 D13 D12 D11 D10 MACK   D9 D8 D7 D6 D5 D4 D3 D2
        
        Byte #5
        MACK D1 D0 SUB5 SUB4 SUB3 SUB2 SUB1 SUB0 MNACK STOP'''
    def __init__(self, i2c) -> None:
        self.i2c = i2c
        self.temp_data = []
        self.i2c_address = 0x76 #LTC2449 address

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
        self.i2c.write_block_data(self.i2c_address, 0, config_data)

    def read(self):
        for channel_num in range(0,16):
            self.setChannel(channel_num)
            Data = self.i2c.read_block_data(self.i2c_address, 0, 4)

    def setChannel(self, channel):
        self.EN = 0b0 #save previous configuration
        self.SGL = 0b1
        self.Channel = bin(channel)

        config_data = [(0b10 << 6) | (self.EN << 5) | (self.SGL << 4) | self.Channel]
        self.i2c.write_byte_data(self.i2c_address, config_data)

if __name__ == '__main__':
    i2c = SMBus(0)

    adc = ADC_LTC2499(i2c)
    adc.init()