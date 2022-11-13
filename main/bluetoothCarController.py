import pygame
import time
import serial

port="/dev/ttyUSB0"
while True:
    try:
        sr=serial.Serial(port, 9600, timeout=0.5)
    except:
        print('Blad podczas polaczenia z', port, 'podaj nowy port lub sprawdz polaczenie:')
        port=input()
        if 'exit' in port: quit()

    else:
        print('Polaczono z', port)
        break

pomiar = False
tyl = 4
przod = 5
skr = 0
speed_multipl = 30
turn_multipl = 40
deadzone = 3
done = False
pmr = False
clock = pygame.time.Clock()


pygame.init()
pygame.joystick.init()
joystick=pygame.joystick.Joystick(0)
joystick.init()
name = joystick.get_name()
axes = joystick.get_numaxes()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.JOYBUTTONDOWN and pmr == False:
            print("Pomiar rozpoczęty")
            pomiar = True
            pmr = True

    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        print('Brak kontrolera')
        time.sleep(3)
        quit()

    if joystick.get_button(1) == 1:
        print('stop')
        quit()

    predkosc = ((round(joystick.get_axis(tyl),1) + 1) * -1 + round(joystick.get_axis(przod),1) + 1) * speed_multipl
    skret = (round(joystick.get_axis(skr),1)) * turn_multipl
    if abs(skret) < deadzone: skret = 0

    if pomiar:
        print("skret {}, predkosc {}".format(round(skret),round(predkosc)))
    else:
        print("Aby rozpoczac pomiar kliknij dowolny przycisk")
    clock.tick(20)

pygame.quit()
