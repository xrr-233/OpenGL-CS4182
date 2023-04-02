#!/usr/bin/env python
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time, random, csv, datetime
import ImportObject
import PIL.Image as Image
import jeep, cone, star, diamond

windowSize = 600
helpWindow = False
helpWin = 0
mainWin = 0
centered = False

beginTime = 0
countTime = 0
score = 0
finalScore = 0
canStart = False
overReason = ""

# for wheel spinning
tickTime = 0

# creating objects
objectArray = []
jeep1Obj = jeep.jeep('p')
jeep2Obj = jeep.jeep('g')
jeep3Obj = jeep.jeep('r')

allJeeps = [jeep1Obj, jeep2Obj, jeep3Obj]
jeepNum = 0
jeepObj = allJeeps[jeepNum]
# personObj = person.person(10.0,10.0)

# concerned with camera
eyeX = 0.0
eyeY = 2.0
eyeZ = 10.0
midDown = False
topView = False
behindView = False
window_size = False
window_full = False

# concerned with panning
nowX = 0.0
nowY = 0.0

angle = 0.0
radius = 10.0
phi = 0.0

vel = 0

# concerned with scene development
land = 20
gameEnlarge = 10

# concerned with obstacles (cones) & rewards (stars)
coneAmount = 15
starAmount = 5  # val = -10 pts
diamondAmount = 1  # val = deducts entire by 1/2
diamondObj = diamond.diamond(random.randint(-land, land), random.randint(10.0, land * gameEnlarge))
usedDiamond = False

allcones = []
allstars = []
obstacleCoord = []
rewardCoord = []
ckSense = 5.0

# concerned with lighting#########################!!!!!!!!!!!!!!!!##########
applyLighting = False

fov = 30.0
attenuation = 1.0

ambientLight = [0.1, 0.1, 0.1, 1.0]
diffuseLight = [0.9, 0.9, 0.9, 1.0]
specularLight = [1.0, 1.0, 1.0, 1.0]

ambientLightEnabled = True
diffuseLightEnabled = True
specularLightEnabled = True
isPosition1 = True
pointLightEnabled = False
directionalLightEnabled = False
spotLightEnabled = False

light0_Position = [0.0, 1.0, 1.0, 1.0]
light0_Intensity = [0.75, 0.75, 0.75, 0.25]

light1_Direction = [0.0, 1.0, 1.0, 0.0]
light1_Intensity = [0.25, 0.25, 0.25, 0.25]

light2_Direction = [0.0, 1.0, 1.0]
light2_Intensity = [0.75, 0.75, 0.75, 0.25]

pointPosition1 = [0.0, 1.0, 1.0, 1.0]
pointPosition2 = [0.0, -10.0, 0.0, 1.0]

matAmbient = [1.0, 1.0, 1.0, 1.0]
matDiffuse = [0.5, 0.5, 0.5, 1.0]
matSpecular = [0.5, 0.5, 0.5, 1.0]
matShininess = 100.0

move_status = {
    'up': False,
    'down': False,
    'left': False,
    'right': False
}


# --------------------------------------developing scene---------------
class Scene:
    axisColor = (0.5, 0.5, 0.5, 0.5)
    axisLength = 50  # Extends to positive and negative on all axes
    landColor = (.47, .53, .6, 0.5)  # Light Slate Grey
    landLength = land  # Extends to positive and negative on x and y axis
    landW = 1.0
    landH = 0.0
    cont = gameEnlarge

    def draw(self):
        self.drawAxis()
        self.drawLand()

    def drawAxis(self):
        glColor4f(self.axisColor[0], self.axisColor[1], self.axisColor[2], self.axisColor[3])
        glBegin(GL_LINES)
        glVertex(-self.axisLength, 0, 0)
        glVertex(self.axisLength, 0, 0)
        glVertex(0, -self.axisLength, 0)
        glVertex(0, self.axisLength, 0)
        glVertex(0, 0, -self.axisLength)
        glVertex(0, 0, self.axisLength)
        glEnd()

    def drawLand(self):
        glEnable(GL_TEXTURE_2D)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, roadTextureID)

        glBegin(GL_POLYGON)

        glTexCoord2f(self.landH, self.landH)
        glVertex3f(self.landLength, 0, self.cont * self.landLength)

        glTexCoord2f(self.landH, self.landW)
        glVertex3f(self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landW)
        glVertex3f(-self.landLength, 0, -self.landLength)

        glTexCoord2f(self.landW, self.landH)
        glVertex3f(-self.landLength, 0, self.cont * self.landLength)
        glEnd()

        glDisable(GL_TEXTURE_2D)


# --------------------------------------populating scene----------------
def staticObjects():
    global objectArray
    objectArray.append(Scene())
    print("scene appended")


def display():
    global jeepObj, canStart, score, beginTime, countTime
    global vel
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if (applyLighting == True):
        glPushMatrix()
        glLoadIdentity()
        gluLookAt(0.0, 3.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        if (pointLightEnabled == True):
            glEnable(GL_LIGHT3)
            glDisable(GL_LIGHT1)
            glDisable(GL_LIGHT2)
            glDisable(GL_LIGHT0)
            glLightfv(GL_LIGHT3, GL_POSITION, light0_Position)
            if (ambientLightEnabled == True):
                glLightfv(GL_LIGHT3, GL_AMBIENT, ambientLight)
            else:
                glLightfv(GL_LIGHT3, GL_AMBIENT, [0.0, 0.0, 0.0, 0.0])
            if (diffuseLightEnabled == True):
                glLightfv(GL_LIGHT3, GL_DIFFUSE, diffuseLight)
            else:
                glLightfv(GL_LIGHT3, GL_DIFFUSE, [0.0, 0.0, 0.0, 0.0])
            if (specularLightEnabled == True):
                glLightfv(GL_LIGHT3, GL_SPECULAR, specularLight)
            else:
                glLightfv(GL_LIGHT3, GL_SPECULAR, [0.0, 0.0, 0.0, 0.0])
        elif (directionalLightEnabled == True):
            glEnable(GL_LIGHT1)
            glDisable(GL_LIGHT3)
            glDisable(GL_LIGHT2)
            glDisable(GL_LIGHT0)
            glLightfv(GL_LIGHT1, GL_POSITION, light1_Direction)
            if (ambientLightEnabled == True):
                glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLight)
            else:
                glLightfv(GL_LIGHT1, GL_AMBIENT, [0.0, 0.0, 0.0, 0.0])
            if (diffuseLightEnabled == True):
                glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuseLight)
            else:
                glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.0, 0.0, 0.0, 0.0])
            if (specularLightEnabled == True):
                glLightfv(GL_LIGHT1, GL_SPECULAR, specularLight)
            else:
                glLightfv(GL_LIGHT1, GL_SPECULAR, [0.0, 0.0, 0.0, 0.0])
        elif (spotLightEnabled == True):
            glEnable(GL_LIGHT2)
            glDisable(GL_LIGHT3)
            glDisable(GL_LIGHT1)
            glDisable(GL_LIGHT0)
            glLightfv(GL_LIGHT2, GL_POSITION, light0_Position)
            glLightfv(GL_LIGHT2, GL_SPOT_DIRECTION, light2_Direction);
            glLightfv(GL_LIGHT2, GL_SPOT_CUTOFF, 45.0);
            if (ambientLightEnabled == True):
                glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLight)
            else:
                glLightfv(GL_LIGHT2, GL_AMBIENT, [0.0, 0.0, 0.0, 0.0])
            if (diffuseLightEnabled == True):
                glLightfv(GL_LIGHT2, GL_DIFFUSE, diffuseLight)
            else:
                glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.0, 0.0, 0.0, 0.0])
            if (specularLightEnabled == True):
                glLightfv(GL_LIGHT2, GL_SPECULAR, specularLight)
            else:
                glLightfv(GL_LIGHT2, GL_SPECULAR, [0.0, 0.0, 0.0, 0.0])
        else:
            glDisable(GL_LIGHT3)
            glDisable(GL_LIGHT1)
            glDisable(GL_LIGHT2)
            glEnable(GL_LIGHT0)

        glColor3f(light0_Intensity[0], light0_Intensity[1], light0_Intensity[2])

        # BIAO JI light0 DE WEI ZHI
        glTranslatef(light0_Position[0], light0_Position[1], light0_Position[2])
        glutSolidSphere(0.25, 36, 24)
        glTranslatef(-light0_Position[0], -light0_Position[1], -light0_Position[2])

        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT, matAmbient)
        for x in range(1, 4):
            for z in range(1, 4):
                matDiffuse = [float(x) * 0.3, float(x) * 0.3, float(x) * 0.3, 1.0]
                matSpecular = [float(z) * 0.3, float(z) * 0.3, float(z) * 0.3, 1.0]
                matShininess = float(z * z) * 10.0
                ## Set the material diffuse values for the polygon front faces.
                glMaterialfv(GL_FRONT, GL_DIFFUSE, matDiffuse)

                ## Set the material specular values for the polygon front faces.
                glMaterialfv(GL_FRONT, GL_SPECULAR, matSpecular)

                ## Set the material shininess value for the polygon front faces.
                glMaterialfv(GL_FRONT, GL_SHININESS, matShininess)

                ## Draw a glut solid sphere with inputs radius, slices, and stacks
                glutSolidSphere(0.25, 72, 64)
                glTranslatef(1.0, 0.0, 0.0)

            glTranslatef(-3.0, 0.0, 1.0)
        ''' for testing
        glLoadIdentity()
        glTranslatef(0.0, 1.0, 10.0)
        glutSolidSphere(2, 72, 64)
        glTranslatef(0.0, 0.0, -20.0)
        glutSolidSphere(2, 72, 64)
        glTranslatef(10.0, 0.0, 10.0)
        glutSolidSphere(2, 72, 64)
        glTranslatef(-20.0, 0.0, 1.0)
        glutSolidSphere(2, 72, 64)
        '''
        glPopMatrix()
    else:
        glDisable(GL_LIGHTING)

    beginTime = 6 - score
    countTime = score - 6
    if (score <= 5):
        canStart = False
        glColor3f(1.0, 0.0, 1.0)
        text3d("Begins in: " + str(beginTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    elif (score == 6):
        canStart = True
        glColor(1.0, 0.0, 1.0)
        text3d("GO!", jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)
    else:
        canStart = True
        glColor3f(0.0, 1.0, 1.0)
        text3d("Scoring: " + str(countTime), jeepObj.posX, jeepObj.posY + 3.0, jeepObj.posZ)

    for obj in objectArray:
        obj.draw()
    for cone in allcones:
        cone.draw()
    for star in allstars:
        star.draw()
    if (usedDiamond == False):
        diamondObj.draw()

    if (move_status['up']):
        if (canStart == True and vel < 0.5):
            vel += 0.1
    if (move_status['down']):
        if (canStart == True and vel > -0.5):
            vel -= 0.1
    if (move_status['left']):
        if (canStart == True):
            jeepObj.rotation += 1
    if (move_status['right']):
        if (canStart == True):
            jeepObj.rotation -= 1

    if (vel > 0):
        jeepObj.wheelDir = 'fwd'
        vel -= 0.01
        if (vel < 0):
            vel = 0
    elif (vel < 0):
        jeepObj.wheelDir = 'back'
        vel += 0.01
        if (vel > 0):
            vel = 0
    else:
        jeepObj.wheelDir = 'stop'
        vel = 0
    jeepObj.move(False, vel)

    if centered == True:
        setObjView()

    jeepObj.draw()
    jeepObj.drawW1()
    jeepObj.drawW2()
    jeepObj.drawLight()
    # personObj.draw()
    glutSwapBuffers()


def idle():  # --------------with more complex display items like turning wheel---
    global tickTime, prevTime, score
    jeepObj.rotateWheel(-0.1 * tickTime)
    glutPostRedisplay()
    # print tickTime, prevTime, jeepObj.wheelTurn

    curTime = glutGet(GLUT_ELAPSED_TIME)
    tickTime = curTime - prevTime
    prevTime = curTime
    score = curTime / 1000


# ---------------------------------setting camera----------------------------
def setView():
    global eyeX, eyeY, eyeZ, jeepObj
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.1, 100)
    if (topView == True):
        gluLookAt(0, 100, land * gameEnlarge / 2, 0, jeepObj.posY, land * gameEnlarge / 2 - 1, 0, -1,
                  0)  # will not be displayed if the Z axis is the same
    elif (behindView == True):
        gluLookAt(jeepObj.posX, jeepObj.posY + 10.0, jeepObj.posZ - 10.0, jeepObj.posX, jeepObj.posY, jeepObj.posZ, 0,
                  1, 0)
    else:
        gluLookAt(eyeX, eyeY, eyeZ, 0, 0, 0, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)

    glutPostRedisplay()


def setObjView():
    # things to do
    # realize a view following the jeep
    # refer to setview
    global eyeX, eyeY, eyeZ, jeepObj
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90, 1, 0.1, 100)
    if (topView == True):
        gluLookAt(jeepObj.posX, 100, jeepObj.posZ, jeepObj.posX, jeepObj.posY, jeepObj.posZ - 1, 0, -1, 0)
    elif (behindView == True):
        gluLookAt(jeepObj.posX - 10 * math.sin(math.radians(jeepObj.rotation)), jeepObj.posY + 10.0,
                  jeepObj.posZ - 10.0 * math.cos(math.radians(jeepObj.rotation)), jeepObj.posX, jeepObj.posY,
                  jeepObj.posZ, 0, 1, 0)
    else:
        gluLookAt(jeepObj.posX + eyeX, jeepObj.posY + eyeY, jeepObj.posZ + eyeZ, jeepObj.posX, jeepObj.posY,
                  jeepObj.posZ, 0, 1, 0)
    glMatrixMode(GL_MODELVIEW)

    glutPostRedisplay()


# -------------------------------------------user inputs------------------
def mouseHandle(button, state, x, y):
    global midDown
    if (button == GLUT_MIDDLE_BUTTON and state == GLUT_DOWN):
        midDown = True
        print("getting pushed")
    else:
        midDown = False


def motionHandle(x, y):
    global nowX, nowY, angle, eyeX, eyeY, eyeZ, phi
    if (midDown == True):
        pastX = nowX
        pastY = nowY
        nowX = x
        nowY = y
        if (nowX - pastX > 0):
            angle -= 0.25
        elif (nowX - pastX < 0):
            angle += 0.25
        # elif (nowY - pastY > 0): look into looking over and under object...
        # phi += 1.0
        # elif (nowX - pastY <0):
        # phi -= 1.0
        eyeX = radius * math.sin(angle)
        eyeZ = radius * math.cos(angle)
        # eyeY = radius * math.sin(phi)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()
    # print eyeX, eyeY, eyeZ, nowX, nowY, radius, angle
    # print "getting handled"


def mouseWheel(button, dir, x, y):
    global eyeX, eyeY, eyeZ, radius
    if (dir > 0):  # zoom in
        radius -= 1
        # setView()
        # print "zoom in!"
    elif (dir < 0):  # zoom out
        radius += 1
        # setView()
        # print "zoom out!"
    eyeX = radius * math.sin(angle)
    eyeZ = radius * math.cos(angle)
    if centered == False:
        setView()
    elif centered == True:
        setObjView()


def specialKeys(keypress, mX, mY):
    # things to do
    # this is the function to move the car
    global window_size, window_full, move_status
    if keypress == GLUT_KEY_UP:
        move_status['up'] = True
    if keypress == GLUT_KEY_DOWN:
        move_status['down'] = True
    if keypress == GLUT_KEY_LEFT:
        move_status['left'] = True
    if keypress == GLUT_KEY_RIGHT:
        move_status['right'] = True
    if keypress == GLUT_KEY_F11:
        if (window_full == False):
            glutFullScreen()
            window_full = True
        else:
            if (window_size == True):
                noReshape(300, 300)
            else:
                noReshape(windowSize, windowSize)
            window_full = False


def specialKeysUp(keypress, mX, mY):
    # things to do
    # this is the function to move the car
    global move_status
    if keypress == GLUT_KEY_UP:
        move_status['up'] = False
    if keypress == GLUT_KEY_DOWN:
        move_status['down'] = False
    if keypress == GLUT_KEY_LEFT:
        move_status['left'] = False
    if keypress == GLUT_KEY_RIGHT:
        move_status['right'] = False


def myKeyboard(key, mX, mY):
    global eyeX, eyeY, eyeZ, angle, radius, helpWindow, centered, helpWin, overReason, topView, behindView, window_size
    global jeepObj

    if key == "h":
        print("h pushed " + str(helpWindow))
        winNum = glutGetWindow()
        if helpWindow == False:
            helpWindow = True
            glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
            glutInitWindowSize(500, 300)
            glutInitWindowPosition(600, 0)
            helpWin = glutCreateWindow('Help Guide')
            glutDisplayFunc(showHelp)
            glutKeyboardFunc(myKeyboard)
            glutMainLoop()
        elif helpWindow == True and winNum != 1:
            helpWindow = False
            print(glutGetWindow())
            glutHideWindow()
            glutMainLoop()
    elif key == "r":
        print(eyeX, eyeY, eyeZ, angle, radius)
        eyeX = 0.0
        eyeY = 2.0
        eyeZ = 10.0
        angle = 0.0
        radius = 10.0
        if centered == False:
            setView()
        elif centered == True:
            setObjView()
    elif key == "l":
        print("light triggered!")
        if jeepObj.lightOn == True:
            jeepObj.lightOn = False
        elif jeepObj.lightOn == False:
            jeepObj.lightOn = True
        glutPostRedisplay()
    elif key == "c":
        if centered == True:
            centered = False
            print("non-centered view")
        elif centered == False:
            centered = True
            print("centered view")
    elif key == "t":  # top view, like a map ####################!!!!!!
        if (topView == True):
            topView = False
        elif (topView == False):
            topView = True
        if centered == False:
            setView()
        elif centered == True:
            setObjView()
    elif key == "b":  # behind the wheel
        if (behindView == True):
            behindView = False
        elif (behindView == False):
            behindView = True
        setView()
    elif key == "m":
        if (window_size == False):
            noReshape(300, 300)
            window_size = True
        else:
            noReshape(windowSize, windowSize)
            window_size = False
    elif key == "q" and canStart == True:
        overReason = "You decided to quit!"
        gameOver()


# -------------------------------------------------tools----------------------
def drawTextBitmap(string, x, y):  # for writing text to display
    glRasterPos2f(x, y)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


def text3d(string, x, y, z):
    glRasterPos3f(x, y, z)
    for char in string:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


def dist(pt1, pt2):
    a = pt1[0]
    b = pt1[1]
    x = pt2[0]
    y = pt2[1]
    return math.sqrt((a - x) ** 2 + (b - y) ** 2)


def noReshape(newX, newY):  # used to ensure program works correctly when resized
    glutReshapeWindow(newX, newY)


def mymenu(value):
    global ambientLightEnabled, diffuseLightEnabled, specularLightEnabled, pointLightEnabled, directionalLightEnabled, spotLightEnabled
    global isPosition1, light0_Position, applyLighting

    if value == 1:
        if (ambientLightEnabled == True):
            ambientLightEnabled = False
            print("Ambient Light: Off")
        elif (ambientLightEnabled == False):
            ambientLightEnabled = True
            print("Ambient Light: On")
    elif value == 2:
        if (diffuseLightEnabled == True):
            diffuseLightEnabled = False
            print("Diffuse Light: Off")
        elif (diffuseLightEnabled == False):
            diffuseLightEnabled = True
            print("Diffuse Light: On")
    elif value == 3:
        if (specularLightEnabled == True):
            specularLightEnabled = False
            print("Specular Light: Off")
        elif (specularLightEnabled == False):
            specularLightEnabled = True
            print("Specular Light: On")
    elif value == 4:
        if (isPosition1 == True):
            light0_Position = pointPosition2
            isPosition1 = False
            print("Position changed to Position 2.")
        else:
            light0_Position = pointPosition1
            isPosition1 = True
            print("Position changed to Position 1.")
    elif value == 5:
        if (pointLightEnabled == True):
            pointLightEnabled = False
            applyLighting = False
            print("Mode: Default")
        elif (pointLightEnabled == False):
            pointLightEnabled = True
            directionalLightEnabled = False
            spotLightEnabled = False
            applyLighting = True
            print("Mode: Point Light")
    elif value == 6:
        if (directionalLightEnabled == True):
            directionalLightEnabled = False
            applyLighting = False
            print("Mode: Default")
        elif (directionalLightEnabled == False):
            directionalLightEnabled = True
            pointLightEnabled = False
            spotLightEnabled = False
            applyLighting = True
            print("Mode: Directional Light")
    elif value == 7:
        if (spotLightEnabled == True):
            spotLightEnabled = False
            applyLighting = False
            print("Mode: Default")
        elif (spotLightEnabled == False):
            spotLightEnabled = True
            pointLightEnabled = False
            directionalLightEnabled = False
            applyLighting = True
            print("Mode: Spot Light")
    return 0


# --------------------------------------------making game more complex--------
def addCone(x, z):
    allcones.append(cone.cone(x, z))
    obstacleCoord.append((x, z))


def addStar(x, z):
    allstars.append(star.star(x, z))
    rewardCoord.append((x, z))


def collisionCheck():
    global overReason, score, usedDiamond, countTime
    for obstacle in obstacleCoord:
        if dist((jeepObj.posX, jeepObj.posZ), obstacle) <= ckSense:
            overReason = "You hit an obstacle!"
            gameOver()
    if (jeepObj.posX >= land or jeepObj.posX <= -land):
        overReason = "You ran off the road!"
        gameOver()
    for reward in rewardCoord:
        if dist((jeepObj.posX, jeepObj.posZ), reward) <= ckSense:
            print("Star bonus!")
            allstars.pop(rewardCoord.index(reward))
            rewardCoord.remove(reward)
            countTime -= 10
    if (dist((jeepObj.posX, jeepObj.posZ), (diamondObj.posX, diamondObj.posZ)) <= ckSense and usedDiamond == False):
        print("Diamond bonus!")
        countTime /= 2
        usedDiamond = True
    if (jeepObj.posZ >= land * gameEnlarge):
        gameSuccess()


# ----------------------------------multiplayer dev (using tracker)-----------
def recordGame():
    with open('results.csv', 'wt') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(st)
        spamwriter.writerow([st] + [finalScore])


# -------------------------------------developing additional windows/options----
def gameOver():
    global finalScore
    print("Game completed!")
    finalScore = score - 6
    # recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200, 200)
    glutInitWindowPosition(600, 100)
    overWin = glutCreateWindow("Game Over!")
    glutDisplayFunc(overScreen)
    glutMainLoop()


def gameSuccess():
    global finalScore
    print("Game success!")
    finalScore = score - 6
    # recordGame() #add to excel
    glutHideWindow()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(200, 200)
    glutInitWindowPosition(600, 100)
    overWin = glutCreateWindow("Complete!")
    glutDisplayFunc(winScreen)
    glutMainLoop()


def winScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(0.0, 1.0, 0.0)
    drawTextBitmap("Completed Trial!", -0.6, 0.85)
    glColor3f(0.0, 1.0, 0.0)
    drawTextBitmap("Your score is: ", -1.0, 0.0)
    glColor3f(1.0, 1.0, 1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()


def overScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0, 0.0, 1.0)
    drawTextBitmap("Incomplete Trial", -0.6, 0.85)
    glColor3f(0.0, 1.0, 0.0)
    drawTextBitmap("Because you...", -1.0, 0.5)
    glColor3f(1.0, 1.0, 1.0)
    drawTextBitmap(overReason, -1.0, 0.35)
    glColor3f(0.0, 1.0, 0.0)
    drawTextBitmap("Your score stopped at: ", -1.0, 0.0)
    glColor3f(1.0, 1.0, 1.0)
    drawTextBitmap(str(finalScore), -1.0, -0.15)
    glutSwapBuffers()


def showHelp():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0, 0.0, 0.0)
    drawTextBitmap("Help Guide", -0.2, 0.85)
    glColor3f(0.0, 0.0, 1.0)
    drawTextBitmap("describe your control strategy.", -1.0, 0.7)
    glutSwapBuffers()


# ----------------------------------------------texture development-----------
def loadTexture(imageName):
    texturedImage = Image.open(imageName)
    try:
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw", "RGBX", 0, -1)  # tostring("raw", "RGBX", 0, -1)
    except Exception as e:
        print("Error:", e)
        print("Switching to RGBA mode.")
        imgX = texturedImage.size[0]
        imgY = texturedImage.size[1]
        img = texturedImage.tobytes("raw", "RGB", 0, -1)  # tostring("raw", "RGBA", 0, -1)

    tempID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tempID)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, imgX, imgY, 0, GL_RGBA, GL_UNSIGNED_BYTE, img)
    return tempID


def loadSceneTextures():
    global roadTextureID
    roadTextureID = loadTexture("../img/road2.png")


# -----------------------------------------------lighting work--------------
def initializeLight():
    glEnable(GL_LIGHTING)
    # glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glClearColor(0.1, 0.1, 0.1, 0.0)


# ~~~~~~~~~~~~~~~~~~~~~~~~~the finale!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    glutInit()

    global prevTime, mainWin
    prevTime = glutGet(GLUT_ELAPSED_TIME)

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    # things to do
    # change the window resolution in the game
    glutInitWindowSize(windowSize, windowSize)

    glutInitWindowPosition(0, 0)
    mainWin = glutCreateWindow('CS4182')
    glutDisplayFunc(display)
    glutIdleFunc(idle)  # wheel turn

    setView()
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)

    glutMouseFunc(mouseHandle)
    glutMotionFunc(motionHandle)
    glutMouseWheelFunc(mouseWheel)
    glutSpecialFunc(specialKeys)  # handle special keys
    glutSpecialUpFunc(specialKeysUp)
    glutKeyboardFunc(myKeyboard)  # handle general keys
    # glutReshapeFunc(noReshape)

    # things to do
    # add a menu
    glutCreateMenu(mymenu)
    glutAddMenuEntry("Switch Ambient Light", 1)
    glutAddMenuEntry("Switch Diffuse Light", 2)
    glutAddMenuEntry("Switch Specular Light", 3)
    glutAddMenuEntry("Switch Position", 4)
    glutAddMenuEntry("Switch Point Light", 5)
    glutAddMenuEntry("Switch Directional Light", 6)
    glutAddMenuEntry("Switch Spot Light", 7)
    glutAttachMenu(GLUT_RIGHT_BUTTON)

    loadSceneTextures()

    jeep1Obj.makeDisplayLists()
    jeep2Obj.makeDisplayLists()
    jeep3Obj.makeDisplayLists()
    # personObj.makeDisplayLists()

    # things to do
    # add an automatic object
    for i in range(
            coneAmount):  # create cones randomly for obstacles, making sure to give a little lag time in beginning by adding 10.0 buffer
        addCone(random.randint(-land, land), random.randint(10.0, land * gameEnlarge))

    for i in range(
            starAmount):  # create cones randomly for obstacles, making sure to give a little lag time in beginning by adding 10.0 buffer
        addStar(random.randint(-land, land), random.randint(10.0, land * gameEnlarge))

    # things to do
    # add stars
    for cone in allcones:
        cone.makeDisplayLists()

    for star in allstars:
        star.makeDisplayLists()

    diamondObj.makeDisplayLists()

    staticObjects()
    if (applyLighting == True):
        initializeLight()
    glutMainLoop()


if __name__ == "__main__":
    main()
