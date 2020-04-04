import time

f = open("/etc/dhcpcd.conf", "a+")

f.write("\n\n")
f.write("#----\n")
f.write("#" + time.strftime("%Y-%m-%d %H:%M") + "\n")

f.write("interface wlan0\n\n")
f.write("static ip_address=192.168.0.1\n")
f.write("static routers=192.168.1.254\n")
f.write("static domain_name_servers=192.168.1.254\n")
f.close()

