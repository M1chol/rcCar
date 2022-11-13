import pygame

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
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


pygame.init()
pygame.joystick.init()
textPrint = TextPrint()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("RcCar")

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.JOYBUTTONDOWN and pmr == False:
            print("Pomiar rozpoczęty")
            pomiar = True
            pmr = True

    screen.fill(WHITE)
    textPrint.reset()

    joystick_count = pygame.joystick.get_count()
    if joystick_count == 0:
        textPrint.tprint(screen, "Kontroler: BRAK")
        pygame.display.flip()
        while joystick_count == 0:
            pass

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    name = joystick.get_name()
    axes = joystick.get_numaxes()
    predkosc = ((round(joystick.get_axis(tyl),1) + 1) * -1 + round(joystick.get_axis(przod),1) + 1) * speed_multipl
    skret = (round(joystick.get_axis(skr),1)) * turn_multipl
    if abs(skret) < deadzone: skret = 0

    textPrint.tprint(screen, "Kontroler: {}".format(name))
    if pomiar:
        textPrint.tprint(screen, "skret wartosc: {}".format(round(skret)))
        textPrint.tprint(screen, "predkosc wartosc: {}".format(round(predkosc)))
    else:
        textPrint.tprint(screen, "Aby rozpoczac pomiar kliknij dowolny przycisk")

    pygame.display.flip()
    clock.tick(20)
pygame.quit()
