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

#__________Rendering__________
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

def DrawLeg(playerPosition: Vector2, leg: Leg, width, color):
    RenderCircle(Color.GREEN, leg.foot.position, player.radius / 2)
    if toggleLegs:
        pygame.draw.line(DISPLAYSURFACE, color, RenderizeVector(playerPosition), RenderizeVector(leg.foot.position), width)

#___________Physics Functions______________

def Gravity(gForce, inAir):
    
    if inAir: #In Air

        if gForce < maxGravity:
            gForce += gravity

        player.velocity.y -= gForce * gravityAcceleration * deltaTime
    else: #On floor
        gForce = 0
        player.velocity.y = 0
        player.position.y = floor + player.radius + 0.1

    return gravityForce

def LegPhysics():
    for i in range(len(legs)):
        #F = -fx Hookes Law
        distance = Vector2.Distace(legs[i].foot.position, player.position)
        displacement = legs[i].spring.targetDistance - distance
        force = displacement * legs[i].spring.strength

        direction = Vector2.Displacement(legs[i].foot.position, player.position).Normal()

        player.velocity += direction * force * deltaTime

def WallCollisions():
    touchingWall = player.position.x + player.radius > boxX or player.position.x - player.radius < -boxX

    if touchingWall:
        player.velocity.x = player.velocity.x * -wallBounce
        if player.position.x < 0:
            player.position.x = -boxX + player.radius
        elif player.position.x > 0:
            player.position.x = boxX - player.radius

def Friction(inAir):
    if inAir:
        if player.velocity.x > 0:
            player.velocity.x -= airFriction * player.velocity.Magnetude() * deltaTime
        elif player.velocity.x < 0:
            player.velocity.x += airFriction * player.velocity.Magnetude() * deltaTime

        if player.velocity.y > 0:
            player.velocity.y -= airFriction * player.velocity.Magnetude() * deltaTime
        elif player.velocity.y < 0:
            player.velocity.y += airFriction * player.velocity.Magnetude() * deltaTime

    else:

        if player.velocity.x > 0:
            player.velocity.x -= groundFriction * deltaTime
        elif player.velocity.x < 0:
            player.velocity.x += groundFriction * deltaTime


#Debug Screen
debugFont = pygame.font.SysFont("Arial", 15)
def DrawDebugScreen():
    fpsDebug = debugFont.render(
        f"FPS = {math.floor(fpsClock.get_fps())}",
          False, Color.BLACK)
    playerDebug = debugFont.render(f"Player Position: {player.position}, Player Velocity {player.velocity}, InAir: {inAir}", 
                                   False, Color.BLACK)
    worldDebug = debugFont.render(f"Gravidy = {gravity}, Ground Friction = {groundFriction}, Air Friction = {airFriction}", 
                                  False, Color.BLACK)
    
    DISPLAYSURFACE.blit(fpsDebug, (0, 0))
    DISPLAYSURFACE.blit(playerDebug, (0, 15))
    DISPLAYSURFACE.blit(worldDebug, (0, 30))

#-----Initialize-----

boxX = 20
boxY = 20
floor = -boxY

gravity = 10
gravityAcceleration = 2
gravityForce = 0
maxGravity = gravity * 10
groundFriction = 1
airFriction = 0.5
wallBounce = 1

toggleLegs = True
legStrength = 5
legLength = 2

inAir = True

player = GameObject(1, Vector2(0, 0), Vector2(0, 0))
legs: list[Leg] = list()

legs.append( Leg( 
    GameObject(1, Vector2(-5, 0)), 
    Spring(legStrength, legLength)))
legs.append( Leg( 
    GameObject(1, Vector2(5, 0)), 
    Spring(legStrength, legLength)))

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

    DrawDebugScreen()

    RenderBox(boxX, boxY, 1, Color.RED)

    #Render Legs
    for i in range(len(legs)):
        DrawLeg(player.position, legs[i], 2, Color.GREEN)
        RenderCircle(Color.GREEN, legs[i].foot.position, legs[i].spring.targetDistance, 1)

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

            if event.key == pygame.K_UP:
                #legs[0].spring.strength += 2
                airFriction += 0.1

            if event.key == pygame.K_DOWN:
                #legs[0].spring.strength -= 2
                airFriction -= 0.1

            if event.key == pygame.K_l:
                if toggleLegs == True:
                    toggleLegs = False
                else:
                    toggleLegs = True
                
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

    gravityForce = Gravity(gravityForce, inAir)

    if toggleLegs:
        LegPhysics()

    WallCollisions()

    Friction(inAir)

    #UpdatePostions
    player.UpdatePosition(deltaTime)

    pygame.display.update()
    fpsClock.tick(FPS)
