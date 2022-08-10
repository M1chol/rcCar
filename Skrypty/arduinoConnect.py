import serial
port="/dev/ttyUSB0"
try:
    sr=serial.Serial(port,9600, timeout=0.5)
except:
    print('Blad podczas polaczenia z',port)
    quit()
else:
    print('Polaczono z',port)
    
sr.flush()
print('Rozpoczynam komunikacje')
slucham=True
while slucham!=False:
    inp=str(input())
    if 'stop' in inp:
        slucham=False
    else:
        sr.write(bytes(inp+'\n','utf-8'))
