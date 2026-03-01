import sys, pygame, math
from physics import Vector2

#Classes
class Color:
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)
    RED =   (255,   0,   0)
    GREEN = (  0, 255,   0)
    BLUE =  (  0,   0, 255)

class GameObject:
    def __init__(self, initPosition: Vector2, initVelocity: Vector2):
        self.position = initPosition
        self.velocity = initVelocity

    def UpdatePosition(self):
        self.position += self.velocity * deltaTime

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
CAMX = WINDOWX / 2
CAMY = WINDOWY / 2
WORLDSCALE = 10 #meters

mainCamera = Camera(Vector2(0, 0), 1)

def RenderizeVector(vector: Vector2):
    return ((vector.x * mainCamera.zoom * WORLDSCALE) + CAMX + mainCamera.position.x,
             (vector.y * mainCamera.zoom * WORLDSCALE * -1) + CAMY + mainCamera.position.y)

def RenderCircle(color, position: Vector2, radius, width=0):
    pygame.draw.circle(DISPLAYSURFACE, color, RenderizeVector(position), radius * WORLDSCALE, width)

#Debug Screen
debugFont = pygame.font.SysFont("Arial", 15)
debugSurface = debugFont.render(f"FPS = {0}", False, Color.WHITE)

#-----Initialize-----

floor = -10
print(floor)

gravity = 20
player = GameObject(Vector2(0, 0), Vector2(0, 0))

jumpPower = 20
speed = 1
speedCap = 1

#-----Main Loop-----
while True:
    deltaTime = fpsClock.tick(FPS) / 1000

    DISPLAYSURFACE.fill(Color.WHITE)

    debugSurface = debugFont.render(
        f"FPS = {math.floor(fpsClock.get_fps())}, Player Position: {player.position}, Player Velocity {player.velocity}",
          False, Color.BLACK)
    DISPLAYSURFACE.blit(debugSurface, (0, 0))

    RenderCircle(Color.BLACK, player.position, 1)

    #Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.velocity.y = jumpPower
            if event.key == pygame.K_a:
                player.velocity.x -= speed
            if event.key == pygame.K_d:
                player.velocity.x += speed
        elif event.type == pygame.KEYUP:
            print("No inputs set")

    #Gravity
    if player.position.y >= floor:
        player.velocity.y -= gravity * deltaTime
    else:
        player.velocity.y = 0
        player.position.y = floor + 0.1

    #UpdatePostions
    player.UpdatePosition()

    pygame.display.update()
    fpsClock.tick(FPS)