from OmegaExpansion import onionI2C

class ADC_LTC2499:
    def __init__(self) -> None:
        self.temp_data = []
        self.i2c_address = 0x76

