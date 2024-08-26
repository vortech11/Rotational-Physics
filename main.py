import pygame, json, os
from pygame import Vector2 as Vector2

script_directory = os.path.dirname(os.path.abspath(__file__))

renderscale = Vector2(1, 1)
camera = Vector2(0, 0)

pygame.init()
W, H=1600, 900
#W, H=400, 800
screen = pygame.display.set_mode([W, H])
pygame_icon = pygame.image.load(os.path.join(script_directory, "images/Hammer Icon.png"))
pygame.display.set_icon(pygame_icon)
pygame.display.set_caption("Half Life III")
clock = pygame.time.Clock()

FPS = 60

font = pygame.font.SysFont("Arial" , 12 , bold = True)

running = True

color=(50,50,50)

bcg=(200, 200, 200)
purp=(255, 0, 255)
wall=(100, 100, 100)
colorchange = False

level = "physics-level.json"

json_file_path = os.path.join(script_directory, "levels/"+level)

with open(json_file_path, "r") as levelfile:
    leveldict = json.load(levelfile)
    levelfile.close()

class objectmanager:
    def __init__(self):
        self.objects = []

    def tick_objects(self):
        for x in range(len(self.objects)):
            self.objects[x].apply_physics_tick(dt)

    def project_points(self, points : list, axis : Vector2):
        min = float('inf')
        max = float('-inf')

        for x in points:
            projection = x.dot(axis)

            if projection > max: max = projection
            if projection < min: min = projection

        return([min, max])

    def find_collisions(self, object1, object2):
        points = object1.get_global_points()
        
        lines = [points[x] - points[(x+1) % len(points)] for x in range(len(points))]

        axes = [Vector2(-lines[x][1], lines[x][0]) for x in range(len(lines))]

        object1_object2_profile = [self.project_points(object1.get_global_points(), axes[x]) for x in range(len(axes))]

        object2_object1_profile = [self.project_points(object2.get_global_points(), axes[x]) for x in range(len(axes))]

        combinded_profiles = [min1 > max2 or min2 > max1 for (min1, max1), (min2, max2) in zip(object1_object2_profile, object2_object1_profile)]

        object1.colliding_color, object2.colliding_color = (0, 0, 0), (0, 0, 0)

        if not(True in combinded_profiles):
            object1.colliding_color = (230, 55, 55)
            object2.colliding_color = (230, 55, 55)

    def handle_collisions(self):
        objects_yet_to_be_checked = self.objects
        
        for object1 in objects_yet_to_be_checked:
            for object2 in objects_yet_to_be_checked:
                if object2 is object1:
                    continue
                
                self.find_collisions(object1, object2)
                self.find_collisions(object2, object1)


class physics_object:
    def __init__(self, controlable, center_of_mass:Vector2, point_offset:list, rotation:float, rotation_speed:float, forces:list, initial_velocity:Vector2, mass_of_object, drag:float, moment_of_inertia:float, color):
        self.center = center_of_mass
        self.points = point_offset
        self.default_color = color
        self.rotation = rotation
        self.angular_velocity = rotation_speed
        self.velocity = initial_velocity
        self.forces = forces
        self.mass = mass_of_object
        self.moment_of_inertia = moment_of_inertia
        self.drag = drag

        self.controlable = controlable
        self.speed = 2

        self.colliding_color = (0, 0, 0)
        self.color = (0, 0, 0)

    def get_global_points(self):
        updated_points = [x.rotate(self.rotation) + self.center for x in self.points]
        return(updated_points)

    def apply_physics_tick(self, time):
        if self.controlable == False:
            for x in range(len(self.forces)):
            
                self.velocity += (self.forces[x][0] / self.mass) * time
                self.angular_velocity += ((self.forces[x][0].cross(self.forces[x][1]-self.center)) / self.moment_of_inertia) * time

                self.forces[x][2] -= 1
                if self.forces[x][2] < 0:
                    del self.forces[x]

            self.velocity *= self.drag
        else:
            keys = pygame.key.get_pressed()
            direction = Vector2(0, 0)
            if keys[pygame.K_a]:
                direction += Vector2(-self.speed, 0)
            if keys[pygame.K_d]:
                direction += Vector2(self.speed, 0)
            if keys[pygame.K_w]:
                direction += Vector2(0, -self.speed)
            if keys[pygame.K_s]:
                direction += Vector2(0, self.speed)

            self.velocity = direction

        if not(self.colliding_color == (0, 0, 0)):
            self.color = self.colliding_color
        else:
            self.color = self.default_color

        self.rotation += self.angular_velocity
        self.center += self.velocity


class player:
    def renderworld(self, camera, renderscale):        
        
        for c in range(0, len(leveldict['tri'])):
            self.poly = self.createrenderPolygon(camera[0], camera[1], leveldict['tri'][c][0]['points'], renderscale)
            pygame.draw.polygon(screen, (leveldict["tri"][c][1]['color'][0], leveldict["tri"][c][1]['color'][1], leveldict["tri"][c][1]['color'][2]), self.poly)
        for c in range(0, len(leveldict['rect'])):
            rectangle = pygame.Rect((leveldict['rect'][c][0]['points'][0]+camera[0])*renderscale[0], (leveldict['rect'][c][0]['points'][1]+camera[1])*renderscale[1], leveldict['rect'][c][0]['points'][2]*renderscale[0], leveldict['rect'][c][0]['points'][3]*renderscale[1])
            pygame.draw.rect(screen, (leveldict['rect'][c][1]['color'][0], leveldict['rect'][c][1]['color'][1], leveldict['rect'][c][1]['color'][2]), rectangle)

    def createrenderPolygon(self, x, y, list, renderscale):
        return [
            ((x+list[0])*renderscale[0], (list[1]+y)*renderscale[1]), ((x+list[2])*renderscale[0], (list[3]+y)*renderscale[1]), 
            ((x+list[4])*renderscale[0], (list[5]+y)*renderscale[1]), ((x+list[6])*renderscale[0], (list[7]+y)*renderscale[1])
            ]

    def __init__(self):
        self.x=leveldict["player"]["startpos"][0]
        self.y=leveldict["player"]["startpos"][1]
        self.direction=(0, 0)
        self.dash=False

    def noclipmove(self):
        global camera
        self.x -= self.direction[0]*(self.dash*1+1)*6
        self.y -= self.direction[1]*(self.dash*1+1)*6

        camera[0] = -self.x+W/renderscale[0]/2
        camera[1] = -self.y+H/renderscale[1]/2

def multiply_vectors(input1:Vector2, input2:Vector2):
    return(Vector2(input1[0] * input2[0], input1[1] * input2[1]))

def apply_render_transformations(object, camera, renderscale):
    points = object.get_global_points()
    updated_points = [multiply_vectors(x + camera, renderscale) for x in points]
    return(updated_points)

def render_physics_object(camera, renderscale):
    for x in range(len(object_manager.objects)):
        pygame.draw.polygon(screen, object_manager.objects[x].color, apply_render_transformations(object_manager.objects[x], camera, renderscale))

def playerinput():
    global running, renderscale
    keys=pygame.key.get_pressed()
    mousekey=pygame.mouse.get_pressed()
    mousepos=pygame.mouse.get_pos()

    if keys[pygame.K_ESCAPE]: running = False

    p.direction = ((keys[pygame.K_LEFT]-keys[pygame.K_RIGHT]), (keys[pygame.K_UP]-keys[pygame.K_DOWN]))

    if keys[pygame.K_c]: p.dash=True
    else: p.dash=False

    if keys[pygame.K_o]:
        renderscale[0] /= 1.0125
        renderscale[1] /= 1.0125

    if keys[pygame.K_p]:
        renderscale[0] *= 1.0125
        renderscale[1] *= 1.0125

    p.noclipmove()

def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))

object_manager = objectmanager()

apple = physics_object(True, Vector2(0, 0), [Vector2(-20, 20), Vector2(20, 20), Vector2(20, -20), Vector2(-20, -20)], 5, 0, [], Vector2(0, 0), 1, 1, 1, (255, 0, 255))
object_manager.objects.append(apple)

banana = physics_object(False, Vector2(50, 50), [Vector2(-20, 20), Vector2(20, 20), Vector2(20, -20), Vector2(-20, -20)], 5, 0, [], Vector2(0, 0), 1, 1, 1, (255, 0, 255))
object_manager.objects.append(banana)

p=player()
while running:
    dt = clock.tick(FPS)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN: clickdown = True
        else: clickdown = False
        if event.type == pygame.MOUSEBUTTONUP: 
            clickup = True
        else: clickup = False
    
    screen.fill((200, 200, 200))
    p.renderworld(camera, renderscale)
    render_physics_object(camera, renderscale)
    
    playerinput()
    
    object_manager.tick_objects()

    object_manager.handle_collisions()

    fps_counter()
    pygame.display.update()

pygame.quit()