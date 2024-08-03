import pygame, json, os

script_directory = os.path.dirname(os.path.abspath(__file__))

renderxscale = 1
renderyscale = 1

camerax = 0
cameray = 0

editstatus = 0
objectedit = 0
pointedit = 0
posoffset = [0, 0]
enter = 0

pygame.init()
W, H=1600, 900
#W, H=400, 800
screen = pygame.display.set_mode([W, H])
pygame_icon = pygame.image.load(os.path.join(script_directory, "images/Hammer Icon.png"))
pygame.display.set_icon(pygame_icon)
pygame.display.set_caption("Half Life III")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial" , 12 , bold = True)

running = True

color=(50,50,50)

bcg=(200, 200, 200)
red=(255, 0 ,0)
purp=(255, 0, 255)
wall=(100, 100, 100)
colorchange = False

leveledit = "physics-level.json"

json_file_path = os.path.join(script_directory, "levels/"+leveledit)

with open(json_file_path, "r") as levelfile:
    leveldict = json.load(levelfile)
    levelfile.close()

def playerinput():
    global running, renderxscale, renderyscale, clickdown, clickup, v, objectedit, editstatus, posoffset, enter, colorchange, color
    keys=pygame.key.get_pressed()
    mousekey=pygame.mouse.get_pressed()
    mousepos=pygame.mouse.get_pos()

    if keys[pygame.K_ESCAPE]: running = False

    p.direction = ((keys[pygame.K_LEFT]-keys[pygame.K_RIGHT]), (keys[pygame.K_UP]-keys[pygame.K_DOWN]))

    if keys[pygame.K_c]: p.dash=True
    else: p.dash=False

    if keys[pygame.K_o]:
        renderxscale /= 1.0125
        renderyscale /= 1.0125

    if keys[pygame.K_p]:
        renderxscale *= 1.0125
        renderyscale *= 1.0125

    p.noclipmove()

def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))

class player:
    def bg(self):        
        screen.fill((200, 200, 200))
        for c in range(0, len(leveldict['tri'])):
            self.poly = self.createrenderPolygon(camerax, cameray, leveldict['tri'][c][0]['points'])
            pygame.draw.polygon(screen, (leveldict["tri"][c][1]['color'][0], leveldict["tri"][c][1]['color'][1], leveldict["tri"][c][1]['color'][2]), self.poly)
        for c in range(0, len(leveldict['rect'])):
            rectangle = pygame.Rect((leveldict['rect'][c][0]['points'][0]+camerax)*renderxscale, (leveldict['rect'][c][0]['points'][1]+cameray)*renderyscale, leveldict['rect'][c][0]['points'][2]*renderxscale, leveldict['rect'][c][0]['points'][3]*renderyscale)
            pygame.draw.rect(screen, (leveldict['rect'][c][1]['color'][0], leveldict['rect'][c][1]['color'][1], leveldict['rect'][c][1]['color'][2]), rectangle)

    def createrenderPolygon(self, x, y, list):
        return [
            ((x+list[0])*renderxscale, (list[1]+y)*renderyscale), ((x+list[2])*renderxscale, (list[3]+y)*renderyscale), 
            ((x+list[4])*renderxscale, (list[5]+y)*renderyscale), ((x+list[6])*renderxscale, (list[7]+y)*renderyscale)]

    def __init__(self, color):
        self.x=leveldict["player"]["startpos"][0]
        self.y=leveldict["player"]["startpos"][1]
        self.col=color
        self.xsize=20
        self.ysize=20
        self.speed=.025
        self.xvelosity=0
        self.yvelosity=0
        self.maxxvelosity=9
        self.maxyvelosity=20
        self.direction=(0, 0)
        self.friction=0.5
        self.gravity=.025
        self.jump=False
        self.stepup=0
        self.maxstepup=1
        self.dash=False
        self.candash=False
        self.groundtimer = 0
        self.noclip = False

    def noclipmove(self):
        global camerax, cameray
        self.x -= self.direction[0]*(self.dash+1)*3
        self.y -= self.direction[1]*(self.dash+1)*3

        camerax = -self.x+W/renderxscale/2
        cameray = -self.y+H/renderyscale/2


v = 0
p=player(red)
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: clickdown = True
        else: clickdown = False
        if event.type == pygame.MOUSEBUTTONUP: 
            clickup = True
        else: clickup = False
    p.bg()

    playerinput()
    
    fps_counter()
    pygame.display.update()

pygame.quit()