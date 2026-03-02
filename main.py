import sys, pygame, math
from classes import *

class Camera:
    def __init__(self, position: Vector2, zoom):
        self.position = position
        self.zoom = zoom

pygame.init()

#Target FPS
FPS = 60
fpsClock = pygame.time.Clock()

#Create Window
WINDOWX = 800
WINDOWY = 600
DISPLAYSURFACE = pygame.display.set_mode((WINDOWX, WINDOWY), 0, 32)
pygame.display.set_caption("Bad Ideas Jam")

#Rendering
WORLDX = WINDOWX / 2
WORLDY = WINDOWY / 2
WORLDSCALE = 10 #meters

mainCamera = Camera(Vector2(0, 0), 1)

def RenderizeVector(vector: Vector2):
    return ((vector.x * mainCamera.zoom * WORLDSCALE) + WORLDX + mainCamera.position.x,
             (vector.y * mainCamera.zoom * WORLDSCALE * -1) + WORLDY + mainCamera.position.y)

def RenderCircle(color, position: Vector2, radius, width=0):
    pygame.draw.circle(DISPLAYSURFACE, color, RenderizeVector(position), radius * WORLDSCALE, width)

def RenderBox(sizeX, sizeY, width, color):
    px = (sizeX * WORLDSCALE * mainCamera.zoom) + WORLDX + mainCamera.position.x
    py = (sizeY * WORLDSCALE * mainCamera.zoom) + WORLDY + mainCamera.position.y
    nx = (-sizeX * WORLDSCALE * mainCamera.zoom) + WORLDX + mainCamera.position.x
    ny = (-sizeY * WORLDSCALE * mainCamera.zoom) + WORLDY + mainCamera.position.y
    #points = [(-x, y), (-x, -y), (x, -y), (x, y)]
    points = [(nx, ny), (nx, py), (px, py), (px, ny)]
    pygame.draw.lines(DISPLAYSURFACE, color, False, points, width)

def DrawLeg(playerPosition: Vector2, legPosition, width, color):
    RenderCircle(Color.GREEN, legPosition, player.radius / 2)
    pygame.draw.line(DISPLAYSURFACE, color, RenderizeVector(playerPosition), RenderizeVector(legPosition), width)

#Debug Screen
debugFont = pygame.font.SysFont("Arial", 15)
debugSurface = debugFont.render(f"FPS = {0}", False, Color.WHITE)

#-----Initialize-----

boxX = 10
boxY = 10
floor = -boxY

gravity = 5
gravityForce = 0
maxGravity = gravity * 10
friction = 1
wallBounce = 1

inAir = True

player = GameObject(Vector2(0, 0), Vector2(0, 0), 1)
legs = list()

legs.append(GameObject(Vector2(0, 5), Vector2(0, 0), 1))
legs.append(GameObject(Vector2(5, 0), Vector2(0, 0), 1))
legs.append(GameObject(Vector2(-5, 0), Vector2(0, 0), 1))

jumpPower = 20
speed = 5
maxSpeed = 10
speedCap = 1

aDown = False
dDown = False

#-----Main Loop-----
while True:
    deltaTime = fpsClock.tick(FPS) / 1000

    DISPLAYSURFACE.fill(Color.WHITE)

    debugSurface = debugFont.render(
        f"FPS = {math.floor(fpsClock.get_fps())}, Player Position: {player.position}, Player Velocity {player.velocity}, InAir: {inAir}",
          False, Color.BLACK)
    
    DISPLAYSURFACE.blit(debugSurface, (0, 0))

    RenderBox(boxX, boxY, 1, Color.RED)

    #Render Legs
    for leg in legs:
        DrawLeg(player.position, leg.position, 2, Color.GREEN)

    #Render Player
    RenderCircle(Color.BLACK, player.position, player.radius)

    #Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: #Jump
                gravityForce = 0
                player.velocity.y = jumpPower

            if event.key == pygame.K_a: #Left
                aDown = True
                
            if event.key == pygame.K_d: #Right
                dDown = True
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                aDown = False
            if event.key == pygame.K_d:
                dDown = False

    if aDown and player.velocity.x > -maxSpeed:
        player.velocity.x -= speed
    if dDown and player.velocity.x < maxSpeed:
        player.velocity.x += speed

    #Physics

    inAir = player.position.y - player.radius >= floor
    touchingWall = player.position.x + player.radius > boxX or player.position.x - player.radius < -boxX

    if inAir: #In Air

        if gravityForce < maxGravity:
            gravityForce += gravity

        player.velocity.y -= gravityForce * deltaTime
    else: #On floor
        gravityForce = 0
        player.velocity.y = 0
        player.position.y = floor + player.radius + 0.1

        if player.velocity.x > 0:
            player.velocity.x -= friction
        elif player.velocity.x < 0:
            player.velocity.x += friction

    if touchingWall:
        player.velocity.x = player.velocity.x * -wallBounce
        if player.position.x < 0:
            player.position.x = -boxX + player.radius
        elif player.position.x > 0:
            player.position.x = boxX - player.radius

    #UpdatePostions
    player.UpdatePosition(deltaTime)

    pygame.display.update()
    fpsClock.tick(FPS)