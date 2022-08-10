import serial

try:
    sr=serial.Serial("/dev/ttyUSB0",9600, timeout=0.5)
except:
    print('Blad podczas polaczenia z dev/ttyUSB0')
    quit()
else:
    print('Polaczono z dev/ttyUSB0')
    
sr.flush()
print('Rozpoczynam komunikacje')
slucham=True
while slucham!=False:
    inp=str(input())
    if 'stop' in inp:
        slucham=False
    else:
        sr.write(bytes(inp+'\n','utf-8'))
        