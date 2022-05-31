import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math,sys,numpy,random,ctypes

pygame.init()
display = (1500, 900)
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption("Phantom World")

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_BLEND)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
glTranslatef(0,-8,0)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

# init mouse movement and center mouse on screen
displayCenter = [screen.get_size()[i] // 2 for i in range(2)]
mouseMove = [0, 0]
pygame.mouse.set_pos(displayCenter)
pygame.mouse.set_visible(False)

cmddown = False
person_count = 1 #6
up_down_angle = 0.0
camera_pos = (0,0,0)
paused = False
run = True
#xzy = xyz

#Functions & Classes
def InverseMat44(mat):
    m = [mat[i][j] for i in range(4) for j in range(4)]
    inv = [0]*16

    inv[0]  =  m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] + m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10]
    inv[4]  = -m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] - m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10]
    inv[8]  =  m[4] * m[9]  * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] + m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9]
    inv[12] = -m[4] * m[9]  * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] - m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9]
    inv[1]  = -m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] - m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10]
    inv[5]  =  m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] + m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10]
    inv[9]  = -m[0] * m[9]  * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] - m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9]
    inv[13] =  m[0] * m[9]  * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] + m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9]
    inv[2]  =  m[1] * m[6]  * m[15] - m[1] * m[7]  * m[14] - m[5] * m[2] * m[15] + m[5] * m[3] * m[14] + m[13] * m[2] * m[7]  - m[13] * m[3] * m[6]
    inv[6]  = -m[0] * m[6]  * m[15] + m[0] * m[7]  * m[14] + m[4] * m[2] * m[15] - m[4] * m[3] * m[14] - m[12] * m[2] * m[7]  + m[12] * m[3] * m[6]
    inv[10] =  m[0] * m[5]  * m[15] - m[0] * m[7]  * m[13] - m[4] * m[1] * m[15] + m[4] * m[3] * m[13] + m[12] * m[1] * m[7]  - m[12] * m[3] * m[5]
    inv[14] = -m[0] * m[5]  * m[14] + m[0] * m[6]  * m[13] + m[4] * m[1] * m[14] - m[4] * m[2] * m[13] - m[12] * m[1] * m[6]  + m[12] * m[2] * m[5]
    inv[3]  = -m[1] * m[6]  * m[11] + m[1] * m[7]  * m[10] + m[5] * m[2] * m[11] - m[5] * m[3] * m[10] - m[9]  * m[2] * m[7]  + m[9]  * m[3] * m[6]
    inv[7]  =  m[0] * m[6]  * m[11] - m[0] * m[7]  * m[10] - m[4] * m[2] * m[11] + m[4] * m[3] * m[10] + m[8]  * m[2] * m[7]  - m[8]  * m[3] * m[6]
    inv[11] = -m[0] * m[5]  * m[11] + m[0] * m[7]  * m[9]  + m[4] * m[1] * m[11] - m[4] * m[3] * m[9]  - m[8]  * m[1] * m[7]  + m[8]  * m[3] * m[5]
    inv[15] =  m[0] * m[5]  * m[10] - m[0] * m[6]  * m[9]  - m[4] * m[1] * m[10] + m[4] * m[2] * m[9]  + m[8]  * m[1] * m[6]  - m[8]  * m[2] * m[5]

    det = m[0] * inv[0] + m[1] * inv[4] + m[2] * inv[8] + m[3] * inv[12]
    for i in range(16):
        inv[i] /= det
    return inv

def touched(tar_x,tar_y,tar_z,tar_x1,tar_y1,tar_z1,dis):
    centerPt = pygame.math.Vector3(tar_x,tar_y,tar_z)
    point2 = pygame.math.Vector3(tar_x1, tar_y1, tar_z1)
    distance = centerPt.distance_to(point2)
    return dis > distance

def follower(x,y,z,x1,y1,z1,speed):
    dir_x, dir_y = (x1-x, y1-y)
    distance = math.hypot(dir_x, dir_y)
    dir_x, dir_y = (dir_x/distance, dir_y/distance)
    angle = math.degrees(math.atan2(dir_y, dir_x))
    return (dir_x*speed, dir_y*speed, 0, angle)

def random_pos(max_distance):
    x_value_change = random.randrange(-max_distance + 2,max_distance + 2)
    y_value_change = random.randrange(-max_distance + 2,max_distance + 2)
    z_value_change = 0
    return (x_value_change, y_value_change, z_value_change)

def blit_text(x,y,font,text,r,g,b):
    blending = False
    if glIsEnabled(GL_BLEND) :
        blending = True
    glColor3f(r,g,b)
    glWindowPos2f(x,y)
    for ch in text :
        glutBitmapCharacter(font,ctypes.c_int(ord(ch)))
    if not blending :
        glDisable(GL_BLEND)

class Ground:
    def __init__(self,mul=1):
        self.vertices = [
        [-20,20,-1],
        [20,20,-1],
        [-20,-300,-1],
        [20,-300,-1]
        ]

    def draw(self):
        glBegin(GL_QUADS) #Begin fill
        for vertex in self.vertices:
            glColor3f(0,0.5,0.5)
            glVertex3fv(vertex)
        glEnd()

class Person:
    def __init__(self):
        self.vertices = [
            [-1,0,1],
            [-1,0,-1],
            [1,0,-1],
            [1,0,1],
            [-1,1,1],
            [-1,1,-1],
            [1,1,-1],
            [1,1,1]
        ]

        self.vertices = list(numpy.multiply(numpy.array(self.vertices),1))
        self.edges = (
            (0,1),
            (0,3),
            (0,4),
            (1,2),
            (1,5),
            (2,3),
            (2,6),
            (3,7),
            (4,5),
            (4,7),
            (5,6),
            (6,7)
            )
        self.surfaces = (
            (0,1,2,3),
            (0,1,5,4),
            (4,5,6,7),
            (1,2,6,5),
            (0,3,7,4),
            (2,3,7,6)
            )
        self.x = self.vertices[1][0]
        self.y = self.vertices[1][2]
        self.z = self.vertices[1][1]
        self.pos = (self.x,self.y,self.z)
        self.rot = 0
        self.health = 100
        self.damage = random.randint(0,5)
        self.level = 1

    def draw(self):
        glTranslated(self.pos[0], self.pos[1], self.pos[2])
        glRotated(self.rot,0,0,1)

        glBegin(GL_QUADS) #Begin fill
        for surface in self.surfaces:
            for vertex in surface:
                glColor3f(0,1,0)
                glVertex3fv(self.vertices[vertex])
        glEnd()
        glLineWidth(5) #Set width of the line
        glBegin(GL_LINES) #Begin outline
        for edge in self.edges:
            for vertex in edge:
                glColor3f(1,1,0)
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def move(self,x,y,z):
        self.pos = (self.pos[0]+x,self.pos[1]+y,self.pos[2]+z)

glutInit()
persons = [Person() for person in range(person_count)]
ground = Ground()
for person in persons:
    person.pos = random_pos(12)
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_p:
                paused = not paused
        if not paused:
            if event.type == pygame.MOUSEMOTION:
                mouseMove = [event.pos[i] - displayCenter[i] for i in range(2)]
                pygame.mouse.set_pos(displayCenter)

    pygame.mouse.set_visible(False)
    if not paused:
        #Get keys
        keypress = pygame.key.get_pressed()

        #Init model view matrix
        glLoadIdentity()

        #------------------------View------------------------
        #Apply the look up and down (with 90� angle limit)
        if up_down_angle < -90:
            if mouseMove[1] > 0:
                up_down_angle += mouseMove[1]*0.1
        elif up_down_angle > 90:
            if mouseMove[1] < 0:
                up_down_angle += mouseMove[1]*0.1
        else:
            up_down_angle += mouseMove[1]*0.1
        glRotatef(up_down_angle, 1.0, 0.0, 0.0)

        #Init the view matrix
        glPushMatrix()
        glLoadIdentity()

        #Apply the movement
        if keypress[pygame.K_w]:
            glTranslatef(0,0,0.1)
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-0.1)
        if keypress[pygame.K_d]:
            glTranslatef(-0.1,0,0)
        if keypress[pygame.K_a]:
            glTranslatef(0.1,0,0)

        #Apply the look left and right
        glRotatef(mouseMove[0]*0.1, 0.0, 1.0, 0.0)
        #------------------------View------------------------
        #------------------------Draw------------------------
        #Multiply the current matrix by the new view matrix and store the final view matrix
        glMultMatrixf(viewMatrix)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        invVM = InverseMat44(viewMatrix)
        camera_pos = (invVM[12],invVM[13],invVM[14])

        #print(camera_pos, " <- ", person.pos)

        #Follower
        for person in persons:
            if not (touched(person.pos[0],person.pos[1],person.pos[2],camera_pos[0],camera_pos[1],camera_pos[2],4)):
                freturn = follower(person.pos[0],person.pos[1],person.pos[2],camera_pos[0],camera_pos[1],camera_pos[2],0.02)
                xchange,ychange,zchange = freturn[0],freturn[1],freturn[2]
                person.rot = freturn[3]
                person.move(xchange,ychange,zchange)
            if (touched(person.pos[0],person.pos[1],person.pos[2],camera_pos[0],camera_pos[1],camera_pos[2],5)):
                crosshair_color = (1,0,0)
            else:
                crosshair_color = (1,1,1)

        #Apply view matrix
        glPopMatrix()
        glMultMatrixf(viewMatrix)

        glLightfv(GL_LIGHT0, GL_POSITION, [1, -1, 1, 0])

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        #Draw crosshair
        blit_text(displayCenter[0] - 5,displayCenter[1] - 5,GLUT_BITMAP_TIMES_ROMAN_24,"+",crosshair_color[0],crosshair_color[1],crosshair_color[2])

        glPushMatrix()

        glColor4f(0.2, 0.2, 0.5, 1)
        for person in persons:
            glPushMatrix()
            person.draw()
            glPopMatrix()

        ground.draw()
        #glutSwapBuffers()
        glPopMatrix()
        #------------------------Draw------------------------

        pygame.display.flip()
        pygame.time.wait(10)

pygame.quit()
sys.exit()