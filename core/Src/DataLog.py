from datetime import datetime
import re

class DataLog:
    def __init__(self) -> None:
        self.fileName = "../../log/" + re.sub('[.:-]', '_',str(datetime.now())) + ".txt"
        
        dataLabel = "time,1A,2A,3A,4A,5A,6A,1B,2B,3B,4B,5B,6B,1C,2C,3C,4C,5C,6C,1D,2D,3D,4D,5D,6D,water_6A,water_1A,water_1D,water_6D,air_1C,air_6C"
        with open(self.fileName, "a+") as log:
            log.write(dataLabel + "\n")

    # 24 data in single 1-D list
    def write_data(self, data:list):
        strData = self.List2Str(data)
        timestamp_str = str(datetime.now()) + ","
        with open(self.fileName, "a+") as log:
            log.write(timestamp_str + strData + "\n")

    # convert list to string, using comma to saperate each element
    def List2Str(self, data:list or tuple) -> str:
        str1 = ','.join((str(element)) for element in data)
        return str1