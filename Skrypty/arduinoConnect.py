import serial
port="/dev/ttyUSB0"
while True:
    try:
        sr=serial.Serial(port,9600, timeout=0.5)
    except:
        print('Blad podczas polaczenia z',port,'podaj nowy port lub sprawdz polaczenie:')
        port=input()
        if 'exit' in port: quit()
        
    else:
        print('Polaczono z',port)
        break
    
sr.flush()
slucham=True
while slucham:
    inp=str(input('arduinoConnect> '))
    if 'exit' in inp:
        slucham=False
    else:
        sr.write(bytes(inp,'utf-8'))

