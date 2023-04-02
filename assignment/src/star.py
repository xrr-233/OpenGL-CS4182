from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, time
import ImportObject


class star:
    obj = 0
    displayList = 0

    posX = 0.0
    posY = 1.2
    posZ = 0.0

    sizeX = 1.0
    sizeY = 1.0
    sizeZ = 1.0

    rotationX = 55.0
    rotationY = 0
    rotationZ = 0

    def __init__(self, x, z):
        self.obj = ImportObject.ImportedObject("../objects/starR")
        self.posX = x
        self.posZ = z

    def makeDisplayLists(self):
        self.obj.loadOBJ()
        self.obj.tempID = self.obj.loadTexture("../img/starSparkle.jpg")
        self.obj.hasTex = True

        self.obj.texCoords.append([0, 0])
        self.obj.texCoords.append([1, 0])
        self.obj.texCoords.append([1, 1])
        self.obj.texCoords.append([0, 1])

        for face in self.obj.faces:
            #print face
            if not face[0] == -1:
                idx = 0
                for f in face:
                    f[1] = idx
                    idx += 1

        self.displayList = glGenLists(1)
        glNewList(self.displayList, GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, self.obj.tempID)
        self.obj.drawObject()
        glEndList()

    def draw(self):
        glPushMatrix()

        glTranslatef(self.posX, self.posY, self.posZ)
        glRotatef(self.rotationX, self.rotationY, self.rotationZ, 1.0)
        self.rotationX += 0.1
        glScalef(self.sizeX, self.sizeY, self.sizeZ)

        glCallList(self.displayList)
        glPopMatrix()



