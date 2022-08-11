import paramiko
import pygame
import time

#zmienne samochodu
carAccel=2
lastTurnCmd = ''
lastMoveCmd = ''
#zmienne wyświetlanie
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
pomiar = False
tyl = 4
przod = 5
skr = 0
#zmienne kontrolera
speed_multipl = 30
turn_multipl = 40
deadzone = 3
done = False
pmr = False
clock = pygame.time.Clock()
#zmienne zdalnego połącznia
target_ip = "192.168.8.199"
target_username = "pi"
target_password = "m1chol"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#stworzenie kanału komunikacji
try:
    ssh.connect(target_ip, username=target_username, password=target_password, look_for_keys=False)
except:
    print("Błąd podczas połacznia zdalnego")
channel = ssh.invoke_shell()
host = str()
srcfile = str()
channel_data = bytes()
driving = False

#klasa obsługująca proste wypisanie tekstu
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

def CloseApp():
    ssh.close()
    pygame.quit()
#funkcje pygame
pygame.init()
pygame.joystick.init()
textPrint = TextPrint()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("RcCar")

#pętla komunikacji
while True:
    if channel.recv_ready():
        channel_data += channel.recv(1000)
    else:
        continue
    if channel_data.endswith(b'pi@raspberrypi:~$ '):
        channel.send(b'cd /home/pi/Desktop/Scripts/Arduino/samochod; python3 arduinoConnect.py\n')

    elif channel_data.endswith(b'arduinoConnect> '):
        driving = True
        while driving:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    CloseApp()
                elif event.type == pygame.JOYBUTTONDOWN and pmr == False:
                    print("Pomiar rozpoczęty")
                    pomiar = True
                    pmr = True

            screen.fill(WHITE)
            textPrint.reset()

            joystick_count = pygame.joystick.get_count()
            if joystick_count == 0:
                textPrint.tprint(screen, "Kontroler: BRAK")
                textPrint.tprint(screen, "Wychodzenie z aplikacji...")
                pygame.display.flip()
                time.sleep(4)
                quit()

            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            if joystick.get_button(1) == 1:
                CloseApp()

            name = joystick.get_name()
            axes = joystick.get_numaxes()
            predkosc = ((round(joystick.get_axis(tyl), 1) + 1) * -1 + round(joystick.get_axis(przod),
                                                                            1) + 1) * speed_multipl
            skret = (round(joystick.get_axis(skr), 1)) * turn_multipl
            if abs(skret) < deadzone: skret = 0

            textPrint.tprint(screen, "Kontroler: {}".format(name))
            if pomiar:
                textPrint.tprint(screen, "skret wartosc: {}".format(int(skret)))
                textPrint.tprint(screen, "predkosc wartosc: {}".format(int(predkosc)))

                moveCmd = bytes('rMove {}\n'.format(int(predkosc)), 'utf-8')
                turnCmd = bytes('rTurn {}\n'.format(int(skret)), 'utf-8')
                print(moveCmd)
                print(turnCmd)
                if lastMoveCmd!=moveCmd: channel.send(moveCmd) #wysłanie komendy do arduino
                if lastTurnCmd!=turnCmd: channel.send(turnCmd) #wysłanie komendy do arduino
                lastMoveCmd = moveCmd
                lastTurnCmd = turnCmd
            else:
                textPrint.tprint(screen, "Aby rozpoczac wysyłanie komend kliknij dowolny przycisk")

            pygame.display.flip()
            clock.tick(20)
    time.sleep(0.1)

CloseApp()
