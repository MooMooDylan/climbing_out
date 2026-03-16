import sys, random, pygame, math, audio
from classes import *

#TODO Remember to change this
version = "0.2"

pygame.init()

#Target FPS
FPS = 60
fpsClock = pygame.time.Clock()

#Create Window
WINDOWX = 1000
WINDOWY = 800
DISPLAYSURFACE = pygame.display.set_mode((WINDOWX, WINDOWY), 0, 32)
try:
    iconImage = pygame.image.load("assets/sprites/notplayer.png")
    pygame.display.set_icon(iconImage)
except:
    print("Failed to load icon image")
pygame.display.set_caption("Stretching Out")

#____Utility Functions____
def Toggle(toggle: bool):
    if toggle == True:
        toggle = False
    else:
        toggle = True
    return toggle

def FindClosestLeg(leg: list[Leg], position: Vector2): #position should be screen space
    shortestDistance = sys.float_info.max
    closestLeg = -1
    
    for i in range(len(leg)):
        distance = Vector2.Distace(leg[i].foot.position, position)
    
        if distance < shortestDistance:
            shortestDistance = distance
            closestLeg = i
    
    return closestLeg

def OnScreen(screenPosition: tuple) -> bool:
    return screenPosition[0] > -renderBuffer and screenPosition[0] < WINDOWX + renderBuffer and screenPosition[1] > -renderBuffer and screenPosition[1] < WINDOWY + renderBuffer

def ListIncludes(list, item):
    count = 0
    for i in list:
        if i == item:
            count += 1
    
    return count > 0

#__________Rendering__________
WORLDX = WINDOWX / 2
WORLDY = WINDOWY / 2
WORLDSCALE = 10 #meters

def RenderizeVector(vector: Vector2):
    return ((vector.x * mainCamera.zoom * WORLDSCALE) + WORLDX + mainCamera.position.x,
             (vector.y * mainCamera.zoom * WORLDSCALE * -1) + WORLDY + mainCamera.position.y)

def CalcMouseWorldSpace(vector: Vector2):
    return Vector2((vector.x - (WORLDX + mainCamera.position.x)) / (mainCamera.zoom * WORLDSCALE),
                    (vector.y - (WORLDY + mainCamera.position.y)) / -(mainCamera.zoom * WORLDSCALE))

def RenderCircle(color, position: Vector2, radius, width=0):
    pygame.draw.circle(DISPLAYSURFACE, color, RenderizeVector(position), radius * WORLDSCALE * mainCamera.zoom, width)

def RenderBox(sizeX, sizeY, width, spaceColor, floorColor):
    px = (sizeX * WORLDSCALE * mainCamera.zoom)
    py = (sizeY * WORLDSCALE * mainCamera.zoom) + WORLDY + mainCamera.position.y
    nx = (-sizeX * WORLDSCALE * mainCamera.zoom) + WORLDX + mainCamera.position.x
    ny = (-sizeY * WORLDSCALE * mainCamera.zoom) + WORLDY + mainCamera.position.y
    #points = [(-x, -y), (-x, y), (x, y), (x, -y)]
    
    gameArea = pygame.rect.Rect((nx, 0), (px * 2, WINDOWY))
    floor = pygame.rect.Rect((nx, py), (px * 2, WINDOWY))

    pygame.draw.rect(DISPLAYSURFACE, spaceColor, gameArea)
    pygame.draw.rect(DISPLAYSURFACE, floorColor, floor)

    #points = [(nx, ny), (nx, py), (px + WORLDX + mainCamera.position.x, py), (px+WORLDX+mainCamera.position.x, ny)]
    #pygame.draw.lines(DISPLAYSURFACE, Color.RED, False, points, width)

def DrawLeg(playerPosition: Vector2, leg: Leg, width, color):
    #RenderCircle(Color.GREEN, leg.foot.position, player.radius / 2)

    if leg.activated:
        pygame.draw.line(DISPLAYSURFACE, color, RenderizeVector(playerPosition), RenderizeVector(leg.foot.position), width)
        
    RenderSprite(sprites[1], leg.foot.position, leg.foot.radius)

def RenderSprite(sprite: pygame.surface.Surface, position: Vector2, radius=1, rotation=0):
    screenPosition = RenderizeVector(position)
    if OnScreen(screenPosition): #Check if on screen
        sprite = pygame.transform.scale(sprite, (mainCamera.zoom * WORLDSCALE * radius * 2, mainCamera.zoom * WORLDSCALE * radius * 2))
        spriteRect = sprite.get_rect()
        spriteRect.center = screenPosition
        DISPLAYSURFACE.blit(sprite, spriteRect)

#___________Physics Functions____________

def Gravity(gForce, inAir):
    
    if inAir: #In Air

        if gForce < maxGravity:
            gForce += gravity

        player.velocity.y -= gForce * gravityAcceleration * deltaTime * len(lockedOn)
    else: #On floor
        gForce = 0
        player.velocity.y = player.velocity.y * -floorBounce
        player.position.y = floor + player.radius

    return gravityForce

def LegPhysics():
    for i in range(len(legs)):
        if (legs[i].activated):
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

def Friction(inAir, object: GameObject, strength=1):
    if inAir:
        if object.velocity.x > 0:
            object.velocity.x -= airFriction * object.velocity.Magnetude() * deltaTime * strength
        elif player.velocity.x < 0:
            object.velocity.x += airFriction * object.velocity.Magnetude() * deltaTime * strength

        if player.velocity.y > 0:
            object.velocity.y -= airFriction * object.velocity.Magnetude() * deltaTime * strength
        elif player.velocity.y < 0:
            object.velocity.y += airFriction * object.velocity.Magnetude() * deltaTime * strength

    else:

        if object.velocity.x > 0:
            object.velocity.x -= groundFriction * deltaTime
        elif object.velocity.x < 0:
            object.velocity.x += groundFriction * deltaTime


#____________Debug Screen____________
showDebug = False
textSpacing = 15
debugFont = pygame.font.SysFont("Arial", textSpacing)

def DrawDebugScreen():
    debugColor = Color.WHITE
    versionText = debugFont.render("Build v" + version, False, Color.RED)

    fpsDebug = debugFont.render(
        f"FPS = {math.floor(fpsClock.get_fps())}",
          False, debugColor)
    playerDebug = debugFont.render(f"Player Position: {player.position}, Player Velocity {player.velocity}, InAir: {inAir}", 
                                   False, debugColor)
    mouseDebug = debugFont.render(f"Mouse Screen Pos: {mouseScreenPos}, World Position: {mouseWorldPos}", 
                                  False, debugColor)
    worldDebug = debugFont.render(f"Gravity = {gravity}, Ground Friction = {groundFriction}, Air Friction = {airFriction}", 
                                  False, debugColor)
    cameraDebug = debugFont.render(f"Camera Pos: {mainCamera.position}, Zoom: {mainCamera.zoom}, Zoom Speed: {zoomSpeed}, Zoom Min: {zoomMin}", 
                                   False, debugColor)
    musicDebug = debugFont.render(f"Next Track: ({song.songState}, {song.preTrack}), Queud Track: ({song.nextState}, {song.track}) ", 
                                  False, debugColor)
    objectsDebug = debugFont.render(f"Anchors: {len(legs)}, Enemies: {len(enemies)}", 
                                    False, debugColor)

    #Determined Order
    debugText = [fpsDebug, playerDebug, mouseDebug, worldDebug, cameraDebug, musicDebug, objectsDebug]

    if showDebug:
        for i in range(len(debugText)):
            DISPLAYSURFACE.blit(debugText[i], (0, i * textSpacing))

        RenderCircle(Color.BLUE, mouseWorldPos, 0.5)

        RenderCircle(Color.RED, player.position, targetDistance, 1)
    
    DISPLAYSURFACE.blit(versionText, (0, WINDOWY - textSpacing))
    #pygame.draw.lines(DISPLAYSURFACE, debugColor, False, [(0, WINDOWY), (WINDOWX, WINDOWY), (WINDOWX, 0)], 5)

#___________Enemy AI___________
def EnemyAI():
    for i in range(len(enemies)):
        
        distance = Vector2.Distace(enemies[i].position, player.position)

        direction = player.position - enemies[i].position
        direction = direction.Normal()

        if distance > targetDistance * 8:
            enemies[i].velocity = Vector2(0, 0)

        if distance > targetDistance:
            enemies[i].velocity += direction * enemySpeed
            if i in lockedOn:
                lockedOn.remove(i)
        elif distance < targetDistance:
            enemies[i].velocity = player.velocity - direction * enemySpeed
            if i not in lockedOn:
                lockedOn.append(i)
          
#___________Load Sprites___________

spritefolder = "assets/sprites/"

spriteFiles = ["player.png", "anchor.png", "enemy.png"]

sprites: list[pygame.surface.Surface] = list()

for file in spriteFiles:
    try:
        sprites.append(pygame.image.load(spritefolder + file))
    except:
     print(f"Failed to load sprite: {spritefolder + file}")
     sprites.append(pygame.surface.Surface((1, 1)))


#-----Initialize-----

gameSeed = 35

random.seed(gameSeed)

#Camera
mainCamera = Camera(Vector2(0, 0), 1)
zoomSpeed = 0.5
zoomMin = zoomSpeed
renderBuffer = 20 #pixels

#Mouse
mouseScreenPos = Vector2.TupleToVector2(pygame.mouse.get_pos())
mouseWorldPos = CalcMouseWorldSpace(mouseScreenPos)
pygame.mouse.set_visible(True)

#Box dimensions
boxX = 50
boxY = 50
floor = -boxY

#SFX
song = Music(0, 0, 0, -1, 0, False)
trackStart = pygame.time.get_ticks()
trackVolume = 0

#Gravity
gravity = 15
gravityAcceleration = 3
gravityForce = 0
maxGravity = gravity * 10

#Friction
groundFriction = 1
airFriction = 0.2

#Bounce
wallBounce = 1
floorBounce = 1

#Legs
toggleLegs = True
legStrength = 5
legLength = 2

inAir = True

#**Player**
player = GameObject(2, Vector2(0, -boxY + 2), Vector2(0, 0))

legs: list[Leg] = list()
legsActivated: list[int] = list()

#**Anchors**
#for i in range(50):
#   x = random.randint(-boxX, boxX)
#   y = random.randint(-boxY, 2000)
#
#   legs.append( Leg( 
#       GameObject(2, Vector2(x, y)), 
#       Spring(legStrength, legLength)))

sections: list[Section] = [Section(20, boxY, 500, boxX, 0)]
sectionsLoaded = list()
    
#**Enemies**
targetDistance = 20
enemySpeed = 1
enemies: list[GameObject] = list()
lockedOn: list[int] = list()
maxSpeed = 50

for i in range(10):
    x = random.randint(-boxX, boxX)
    y = random.randint(0, 500)

    enemies.append(GameObject(2, Vector2(x, y)))

#jumpPower = 20
#speed = 5
#speedCap = 1

#Input stuff
#aDown = False
#dDown = False

#-----Main Loop-----
while True:
    deltaTime = fpsClock.tick(FPS) / 1000
    currentTime = pygame.time.get_ticks()
    song.timer = (currentTime - trackStart) / 1000

    for i in range(len(sections)):
        if player.position.x > sections[i].floor and not ListIncludes(sectionsLoaded, i):

            for point in sections[0].positions:
                legs.append(Leg( 
                    GameObject(2, Vector2(point.x, point.y)), 
                    Spring(legStrength, legLength)))
                
            sectionsLoaded.append(i)

        if player.position.x >= sections[i].ceiling and ListIncludes(sectionsLoaded, i):
            legs.clear()

            sectionsLoaded.remove(i)

    DISPLAYSURFACE.fill(Color.BLACK)

    RenderBox(boxX, boxY, 1, Color.GREY, Color.BLACK)

    #Render Legs
    for i in range(len(legs)):
        DrawLeg(player.position, legs[i], 2, Color.GREEN)
        RenderCircle(Color.GREEN, legs[i].foot.position, legs[i].spring.targetDistance, 1)

    #Render Enemy
    for i in lockedOn:
        pygame.draw.line(DISPLAYSURFACE, Color.RED, RenderizeVector(player.position), RenderizeVector(enemies[i].position), 2)
    for enemy in enemies:
        RenderSprite(sprites[2], enemy.position, enemy.radius)

    #Render Player
    #RenderCircle(Color.WHITE, player.position, player.radius)
    RenderSprite(sprites[0], player.position, player.radius)

    #Render Cursor
    #pygame.draw.circle(DISPLAYSURFACE, Color.BLUE, (mouseScreenPos.x, mouseScreenPos.y), 5)
    #Moved to Debug

    DrawDebugScreen()

    if song.songState == 0 and song.track == 2: #Go from intro to main
        song.nextState = 1
    song = audio.AudioManager(song.songState, song.nextState, song.track, song.preTrack, song.timer, trackVolume)
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
#            if event.key == pygame.K_w: #Jump
#               gravityForce = 0
#               player.velocity.y = jumpPower
#
#           if event.key == pygame.K_a: #Left
#               aDown = True
#               
#           if event.key == pygame.K_d: #Right
#               dDown = True
#
            if event.key == pygame.K_UP: #Debug
                #legs[0].spring.strength += 2
                song.nextState += 1
                print(song.nextState)

            if event.key == pygame.K_DOWN: #Debug
                #legs[0].spring.strength -= 2
                song.nextState -= 1
                print(song.nextState)

            if event.key == pygame.K_SPACE:
                for i in legsActivated:
                    legs[i].activated = False

                legsActivated.clear()

            if event.key == pygame.K_p:
                showDebug = Toggle(showDebug)

            if event.key == pygame.K_m:
                if trackVolume == 1:
                    trackVolume = 0
                else:
                    trackVolume = 1
                
        #Lift Key
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                aDown = False
            if event.key == pygame.K_d:
                dDown = False

        mouseScreenPos = Vector2.TupleToVector2(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONDOWN:
            print("Mouse Down")
            if event.button == 1: #Left Click
                print("Left click")
                closestLeg = FindClosestLeg(legs, mouseWorldPos)

                if legs[closestLeg].activated:
                    legsActivated.remove(closestLeg)
                else:
                    legsActivated.append(closestLeg)
                    
                legs[closestLeg].activated = Toggle(legs[closestLeg].activated) #Find closest leg to mose and toggle activated
                


        #Mouse Wheel (camera zoom)
        if event.type == pygame.MOUSEWHEEL:
            if mainCamera.zoom != zoomMin or event.y > 0:
                mainCamera.zoom += event.y * zoomSpeed

            if mainCamera.zoom < zoomMin:
                mainCamera.zoom = zoomMin

    
    mouseWorldPos = CalcMouseWorldSpace(mouseScreenPos)

    #Physics

    inAir = player.position.y - player.radius >= floor

    gravityForce = Gravity(gravityForce, inAir)

    LegPhysics()

    WallCollisions()

    Friction(inAir, player)
    Friction(True, enemies[0])

    #AI
    EnemyAI()

    #UpdatePostions
    player.UpdatePosition(deltaTime)

    for enemy in enemies:
        enemy.UpdatePosition(deltaTime)

    mainCamera.position.x = player.position.x * WORLDSCALE * mainCamera.zoom * -1
    mainCamera.position.y = player.position.y * WORLDSCALE * mainCamera.zoom

    pygame.display.update()
    fpsClock.tick(FPS)
