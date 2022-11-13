import paramiko
import time

target_ip = "192.168.8.199"
target_username = "pi"
target_password = "m1chol"
ssh = paramiko.SSHClient()

ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(target_ip, username=target_username, password=target_password, look_for_keys=False )

channel = ssh.invoke_shell()
host = str()
srcfile = str()
channel_data = bytes()
driving=False

while True:
    if channel.recv_ready():
        channel_data+=channel.recv(1000)
        print(channel_data)
    else:
        continue
    if channel_data.endswith(b'pi@raspberrypi:~$ '):
        channel.send(b'cd /home/pi/Desktop/Scripts/Arduino/samochod; python3 arduinoConnect.py\n')

    elif channel_data.endswith(b'arduinoConnect> '):
        driving = True
        while driving:

            channel.send(b'')

ssh.close()

