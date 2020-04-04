import os

def RPi_core_temperature():
        temp = os.popen("vcgencmd measure_temp").readline()
        # temp = temp.replace("temp=", "")
        temp = temp[5:9]
        return temp
