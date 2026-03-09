import sys, pygame, math, audio
from classes import *

#TODO Remember to change this
version = "0.2"

pygame.init()

#Target FPS
FPS = 60
fpsClock = pygame.time.Clock()

#Create Window
WINDOWX = 800
WINDOWY = 600
DISPLAYSURFACE = pygame.display.set_mode((WINDOWX, WINDOWY), 0, 32)
pygame.display.set_caption("Bad Ideas Jam")

#____Utility Functions____
def Toggle(toggle: bool):
    if toggle == True:
        toggle = False
    else:
        toggle = True
    return toggle

#__________Rendering__________
WORLDX = WINDOWX / 2
WORLDY = WINDOWY / 2
WORLDSCALE = 10 #meters

def RenderizeVector(vector: Vector2):
    return ((vector.x * mainCamera.zoom * WORLDSCALE) + WORLDX + mainCamera.position.x,
             (vector.y * mainCamera.zoom * WORLDSCALE * -1) + WORLDY + mainCamera.position.y)

def CalcMouseWorldSpace(vector: Vector2):
    if vector.x != 0 and vector.y != 0:
        return Vector2((vector.x / WORLDSCALE) - WORLDX - mainCamera.position.x, 
                       (vector.y / WORLDSCALE * -1) - WORLDY - mainCamera.position.y)
    
    if vector.x == 0 and vector.y == 0:
        return Vector2(0 - WORLDX - mainCamera.position.x, 
                       0 - WORLDY - mainCamera.position.y)
    elif vector.x == 0:
        return Vector2(0 - WORLDX - mainCamera.position.x, 
                       (vector.y / mainCamera.zoom / WORLDSCALE) - WORLDY - mainCamera.position.y)
    else:
        return Vector2((vector.x / mainCamera.zoom / WORLDSCALE) - WORLDX - mainCamera.position.x, 
                       0 - WORLDY - mainCamera.position.y)

def RenderCircle(color, position: Vector2, radius, width=0):
    pygame.draw.circle(DISPLAYSURFACE, color, RenderizeVector(position), radius * WORLDSCALE * mainCamera.zoom, width)

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

#___________Physics Functions____________

def Gravity(gForce, inAir):
    
    if inAir: #In Air

        if gForce < maxGravity:
            gForce += gravity

        player.velocity.y -= gForce * gravityAcceleration * deltaTime
    else: #On floor
        gForce = 0
        player.velocity.y = player.velocity.y * -floorBounce
        player.position.y = floor + player.radius

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


#____________Debug Screen____________
showDebug = False
textSpacing = 15
debugFont = pygame.font.SysFont("Arial", textSpacing)

def DrawDebugScreen():
    versionText = debugFont.render("Build v" + version, False, Color.RED)

    fpsDebug = debugFont.render(
        f"FPS = {math.floor(fpsClock.get_fps())}",
          False, Color.BLACK)
    playerDebug = debugFont.render(f"Player Position: {player.position}, Player Velocity {player.velocity}, InAir: {inAir}", 
                                   False, Color.BLACK)
    mouseDebug = debugFont.render(f"Mouse Screen Pos: {mouseScreenPos}", 
                                  False, Color.BLACK)
    worldDebug = debugFont.render(f"Gravity = {gravity}, Ground Friction = {groundFriction}, Air Friction = {airFriction}", 
                                  False, Color.BLACK)
    cameraDebug = debugFont.render(f"Camera Pos: {mainCamera.position}, Zoom: {mainCamera.zoom}, Zoom Speed: {zoomSpeed}, Zoom Min: {zoomMin}", 
                                   False, Color.BLACK)
    musicDebug = debugFont.render(f"Current Track: ({song.songState}, {song.preTrack}), Queud Track: ({song.nextState}, {song.track}) ", 
                                  False, Color.BLACK)

    #Determined Order
    debugText = [fpsDebug, playerDebug, mouseDebug, worldDebug, cameraDebug, musicDebug]

    if showDebug:
        for i in range(len(debugText)):
            DISPLAYSURFACE.blit(debugText[i], (0, i * textSpacing))
    
    DISPLAYSURFACE.blit(versionText, (0, WINDOWY - textSpacing))

#-----Initialize-----

#Camera
mainCamera = Camera(Vector2(0, 0), 1)
zoomSpeed = 0.5
zoomMin = zoomSpeed

#Mouse
mouseScreenPos = Vector2.TupleToVector2(pygame.mouse.get_pos())
pygame.mouse.set_visible(False)

#Box dimensions
boxX = 50
boxY = 50
floor = -boxY

#SFX
song = Music(0, 0, 0, -1, 0, False)
trackStart = pygame.time.get_ticks()

#Gravity
gravity = 10
gravityAcceleration = 2
gravityForce = 0
maxGravity = gravity * 10

#Friction
groundFriction = 1
airFriction = 0.25

#Bounce
wallBounce = 1
floorBounce = 1

#Legs
toggleLegs = True
legStrength = 5
legLength = 2

inAir = True

#Player
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

#Input stuff
aDown = False
dDown = False

#-----Main Loop-----
while True:
    deltaTime = fpsClock.tick(FPS) / 1000
    currentTime = pygame.time.get_ticks()
    song.timer = (currentTime - trackStart) / 1000

    DISPLAYSURFACE.fill(Color.WHITE)
    
    DrawDebugScreen()

    RenderBox(boxX, boxY, 1, Color.RED)

    #Render Legs
    for i in range(len(legs)):
        DrawLeg(player.position, legs[i], 2, Color.GREEN)
        RenderCircle(Color.GREEN, legs[i].foot.position, legs[i].spring.targetDistance, 1)

    #Render Player
    RenderCircle(Color.BLACK, player.position, player.radius)

    #Render Cursor
    pygame.draw.circle(DISPLAYSURFACE, Color.BLUE, (mouseScreenPos.x, mouseScreenPos.y), 5)

    song = audio.AudioManager(song.songState, song.nextState, song.track, song.preTrack, song.timer)
    if song.changedTrack:
        trackStart = pygame.time.get_ticks()

    #Events
    for event in pygame.event.get():
        #Quit Game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        #Key pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w: #Jump
                gravityForce = 0
                player.velocity.y = jumpPower

            if event.key == pygame.K_a: #Left
                aDown = True
                
            if event.key == pygame.K_d: #Right
                dDown = True

            if event.key == pygame.K_UP: #Debug
                #legs[0].spring.strength += 2
                song.nextState += 1
                print(song.nextState)

            if event.key == pygame.K_DOWN: #Debug
                #legs[0].spring.strength -= 2
                song.nextState -= 1
                print(song.nextState)

            if event.key == pygame.K_SPACE:
                toggleLegs = Toggle(toggleLegs)

            if event.key == pygame.K_p:
                showDebug = Toggle(showDebug)
                
        #Lift Key
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                aDown = False
            if event.key == pygame.K_d:
                dDown = False

        mouseScreenPos = Vector2.TupleToVector2(pygame.mouse.get_pos())
        mouseWorldPos = CalcMouseWorldSpace(mouseScreenPos)

        #Mouse Wheel (camera zoom)
        if event.type == pygame.MOUSEWHEEL:
            if mainCamera.zoom != zoomMin or event.y > 0:
                mainCamera.zoom += event.y * zoomSpeed

            if mainCamera.zoom < zoomMin:
                mainCamera.zoom = zoomMin

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

    mainCamera.position.x = player.position.x * WORLDSCALE * mainCamera.zoom * -1
    mainCamera.position.y = player.position.y * WORLDSCALE * mainCamera.zoom

    pygame.display.update()
    fpsClock.tick(FPS)
