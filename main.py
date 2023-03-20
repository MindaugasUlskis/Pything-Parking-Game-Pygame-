import pygame, math, sys
import Button


pygame.init()
from pytmx.util_pygame import load_pygame
import random

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement



screen = pygame.display.set_mode((640, 576))

pygame.display.set_caption("car game")

img = pygame.image.load("car.png").convert_alpha()



#print(pygame.font.get_fonts())
MAP_COUNT = 2

play_img = pygame.image.load("PlayButton.png")
playBtn = Button.Button(215, 200, play_img, 0.4)
emptyBtnImg = pygame.image.load("SmallEmptyButton.png")
emptyBtn = Button.Button(215, 200, emptyBtnImg, 0.4)

font = pygame.font.SysFont("calibri", 72)
TEXT_COL = (255,255,255)





def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def RandomCell(matrix, startx, starty):
    candidates = []
    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            if matrix[y][x] == 1:
                if startx != x and starty != y:
                    candidates.append((x, y))
    x, y = random.choice(candidates)
    return x, y

class Pathfinder:
    def __init__(self, matrix):
        self.matrix = matrix
        self.grid = Grid(matrix=matrix)


        self.person = pygame.sprite.GroupSingle(Person())

    def crate_path(self):

        startx, starty = self.person.sprite.get_coord()
        start = self.grid.node(x=startx, y=starty)

        endx, endy = RandomCell(self.matrix, startx, startx)
        end = self.grid.node(endx, endy)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        self.path,_ = finder.find_path(start, end, self.grid)
        self.grid.cleanup()
        self.person.sprite.set_path(self.path)
        print(self.path)
    def draw_path(self):
         if self.path:
            points = []
            for point in self.path:
                x = (point[0] * 64)+32
                y = (point[1] * 64)+32
                points.append((x, y))
            pygame.draw.lines(screen, '#4a4a4a', False, points, 5)

    def update(self):
        if hasattr(self, 'path'):
            self.draw_path()
            self.person.update()
            self.person.draw(screen)

    def getPersonPos(self):
        return self.person.sprite.pos




class Car:
    def __init__(self, x, y, height, width):
        self.x = x - width / 2
        self.y = y - height / 2
        self.height = height
        self.width = width
        self.rect = pygame.Rect(x, y, height, width)
        self.surface = pygame.Surface((height, width), pygame.SRCALPHA)
        self.surface.blit(img, (0, 0))
        self.angle = 0
        self.speed = 0 # 2
        self.mask = pygame.mask.from_surface(pygame.transform.rotate(self.surface, self.angle))
        self.sensor_angles = [0, 30, -30]
        self.sensor_distances = [0] * len(self.sensor_angles)

    def draw(self): # 3
        self.rect.topleft = (int(self.x), int(self.y))
        rotated = pygame.transform.rotate(self.surface, self.angle)
        surface_rect = self.surface.get_rect(topleft = self.rect.topleft)
        new_rect = rotated.get_rect(center = surface_rect.center)
        screen.blit(rotated, new_rect.topleft)
        border_color = (255, 0, 0)
        border_width = 2
        pygame.draw.rect(screen, border_color, new_rect, border_width)

class Person(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('person.png').convert_alpha()
        self.rect = self.image.get_rect(center = (150,150))

        self.pos = self.rect.center
        self.speed = 0.050
        self.direction = pygame.math.Vector2(0,0)
        self.path = []
        self.collsion_rects = []

    def get_coord(self):
        col = self.rect.centerx // 64
        row = self.rect.centery //64
        return(col, row)
    def set_path(self, path):
        self.path = path
        self.create_collision_rects()
        self.get_direction()

    def create_collision_rects(self):
        if self.path:
            self.collsion_rects = []
            for point in self.path:
                x = (point[0] * 64) + 32
                y = (point[1] * 62) + 32
                rect = pygame.Rect((x - 2, y - 2), (4,4))
                self.collsion_rects.append(rect)
    def get_direction(self):
        if self.collsion_rects:
            start = pygame.math.Vector2(self.pos)
            end = pygame.math.Vector2(self.collsion_rects[0].center)
            self.direction = (end - start)
        else:
            self.direction = pygame.math.Vector2(0,0)
            self.path = []
            pathfinder.crate_path()
            pathfinder.draw_path()
    def check_collisions(self):
        if self.collsion_rects:
            for rect in self.collsion_rects:
                if rect.collidepoint(self.pos):
                    del self.collsion_rects[0]
                    self.get_direction()
    def update(self):
        self.pos += self.direction * self.speed
        self.check_collisions()
        self.rect.center = self.pos

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, border_color=None, border_width=0,):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(surf)

        if border_color is not None and border_width > 0:
            border_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(border_surf, border_color, border_surf.get_rect(), border_width)
            self.image.blit(border_surf, (0, 0))

class MapData:
    def __init__(self):
        self.tmx_data = load_pygame('map1.tmx')
        self.sprite_group = pygame.sprite.Group()
        self.sprite_col = pygame.sprite.Group()
        self.car1 = Car(1,1,43,74)
        self.Start_Y = 0
        self.Start_X = 0
        self.finish_rect = pygame.Rect(1,1,1,1)
        self.border_rects = []
        self.matrix = [[0,0,0,0,0,0,0,0,0,0],
[0,1,1,1,1,1,1,1,1,0],
[1,1,1,1,1,1,1,1,1,0],
[1,1,1,1,1,1,1,1,1,0],
[0,1,1,1,1,1,1,1,1,0],
[0,1,1,1,1,1,1,1,1,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0],
]

    def objectsToGroups(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 64, y * 64)
                    Tile(pos=pos, surf=surf, groups=self.sprite_group)
        for obj in self.tmx_data.objects:
            pos = obj.x, obj.y
            if obj.name == 'RandomCar':
                print("random car object exists")
                if obj.image is not None:
                    Tile(pos=pos, surf=obj.image, groups=self.sprite_col, border_color='red', border_width=0)
            if obj.name == 'Border':
                print("border object exists")
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.border_rects.append(rect)
            if obj.name == "Finish":
                print("Finish object exists")
                self.finish_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        for obj in self.tmx_data.objects:
            print(obj.name)

        # get start position
        for obj in self.tmx_data.objects:
            pos = obj.x, obj.y
            if obj.name == 'Start':
                self.Start_Y = obj.y-40
                self.Start_X = obj.x
        self.car1 = Car(self.Start_X, self.Start_Y, 43, 74)

    def coll(self):
        for Colide in self.sprite_col:
            offset_x = Colide.rect[0] - self.car1.rect.left
            offset_y = Colide.rect[1] - self.car1.rect.top
            if  self.car1.mask.overlap(pygame.mask.from_surface(Colide.image), (offset_x, offset_y)):
                print("Collision detected with car!")
                self.resetCar()
                return True

            # check for collisions with borders
        for border_rect in self.border_rects:
            if self.car1.rect.colliderect(border_rect):
                print("Collision detected with border!")
                self.resetCar()
                return True

    def resetCar(self):
        self.car1.x = self.Start_X
        self.car1.y = self.Start_Y
        self.car1.speed = 0
        self.car1.angle = 0

    def DidItFinish(self):
        if self.finish_rect and self.car1.rect.colliderect(self.finish_rect) and self.finish_rect.contains(self.car1.rect):
            print("Car has reached the finish zone!")
            return True
    def NextLevel(self, level_number):

        if(level_number == 2):
            self.tmx_data = load_pygame('map2.tmx')
        self.sprite_group = pygame.sprite.Group()
        self.sprite_col = pygame.sprite.Group()
        self.car1 = Car(1,1,43,74)
        self.Start_Y = 0
        self.Start_X = 0
        self.finish_rect = pygame.Rect(1,1,1,1)
        self.border_rects = []
        self.matrix =\
        [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
         [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
         [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
         [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
         [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         ]

        self.objectsToGroups()




mapData = MapData()

clock = pygame.time.Clock()

mapData.objectsToGroups()



game_run = "menu"
personExist = False

while True:

    if not personExist:
        pathfinder = Pathfinder(mapData.matrix)
        pathfinder.crate_path()
        pathfinder.draw_path()
        personExist = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if game_run == "game":
        if(mapData.coll()):
            game_run = "col"
            #check if car is inside finish zone
        if(mapData.DidItFinish()):
            game_run = "finish"
        if (mapData.car1.rect.collidepoint(pathfinder.getPersonPos())):
            mapData.resetCar()
            print("person has been hit!")
            game_run = "hit"

        pressed = pygame.key.get_pressed()
        mapData.car1.speed *= 0.9
        if pressed[pygame.K_UP]: mapData.car1.speed += 0.5 # 6
        if pressed[pygame.K_DOWN]: mapData.car1.speed -= 0.5 # 6



        if pressed[pygame.K_LEFT]: mapData.car1.angle += mapData.car1.speed / 2
        if pressed[pygame.K_RIGHT]: mapData.car1.angle -= mapData.car1.speed / 2
        mapData.car1.x -= mapData.car1.speed * math.sin(math.radians(mapData.car1.angle))
        mapData.car1.y -= mapData.car1.speed * math.cos(math.radians(-mapData.car1.angle))

        #screen.fill((0, 0, 0))
        mapData.sprite_group.draw(screen)
        mapData.sprite_col.draw(screen)

        mapData.car1.draw()
        pathfinder.update()
        pygame.display.flip()
        clock.tick(60)
    elif game_run == "menu":
        screen.fill((24,24,24))
        if playBtn.draw(screen):
            game_run = "game"
        pygame.display.update()
        clock.tick(60)
    elif game_run == "col":
        draw_text("C R A S H E D", font, TEXT_COL, 140, 80)
        draw_text("RETRY", font, TEXT_COL, 225, 220)
        if emptyBtn.draw(screen):
            game_run = "game"
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]: game_run = "game"
        pygame.display.update()
    elif game_run == "hit":
        draw_text("HIT A PERSON!", font, TEXT_COL, 140, 80)
        draw_text("RETRY", font, TEXT_COL, 225, 220)
        if emptyBtn.draw(screen):
            game_run = "game"
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]: game_run = "game"
        pygame.display.update()

    elif game_run == "finish":
        draw_text("P A R K E D", font, TEXT_COL, 160, 80)
        draw_text("NEXT", font, TEXT_COL, 235, 220)
        if emptyBtn.draw(screen):
            mapData.NextLevel(2)
            pathfinder = Pathfinder(mapData.matrix)
            personExist = False
            game_run = "game"

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_n]:
            mapData.NextLevel(2)
            pathfinder = Pathfinder(mapData.matrix)
            personExist = False
            game_run = "game"
        pygame.display.update()

pygame.quit()

















