import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Cubo import Cubo

# Import obj loader
from objloader import *

screen_width = 1200
screen_height = 800
#vc para el obser.
FOVY=60.0
ZNEAR=0.01
ZFAR=900.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X = 300.0
EYE_Y = 200.0
EYE_Z = 300.0
CENTER_X = 0
CENTER_Y = 0
CENTER_Z = 0
UP_X=0
UP_Y=1
UP_Z=0
#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500
Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 200

#Variables del calamar
Player_X = 0.0
Player_Y = 0.0
Player_Z = 0.0
Player_Rotation = 0.0  # Rotación del calamar en grados
SquidT = 0.0
SquidSw = 0
SquidSwBack = 0

#variables de la maquina Wheel Loader
Maquina_X = 0.0
Maquina_Y = 0.0
Maquina_Z = 0.0
car_angle = 0.0
wheel_angle = 0.0
wheel_rotate = 0.0

objetos = []

#Variables para el control del observador
theta = 0.0
radius = 300


pygame.init()

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)


def Init():
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
        
    #glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_POSITION,  (0, 200, 0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)           
    
    #objetos.append(OBJ("Player_Squid/Squid.obj" , swapyz=True))
    objetos.append(OBJ("Player_Squid/faceSquid.obj" , swapyz=True)) #0
    objetos.append(OBJ("Player_Squid/DerSquid.obj" , swapyz=True)) #1
    objetos.append(OBJ("Player_Squid/IzqSquid.obj" , swapyz=True)) #2
    
    objetos.append(OBJ("WheelLoader/BaseMaquina.obj" , swapyz=True)) #3
    #objetos.append(OBJ("WheelLoader/ArmMaquina.obj" , swapyz=True)) #4
    objetos.append(OBJ("WheelLoader/GArmMaquina.obj" , swapyz=True)) #4

    
    #objetos.append(OBJ("WheelLoader/FWMaquina.obj" , swapyz=True))
    #objetos.append(OBJ("WheelLoader/BWMaquina.obj" , swapyz=True))
    objetos.append(OBJ("WheelLoader/GWMaquina.obj" , swapyz=True)) #5
    #objetos.append(OBJ("Excavator/Excavator.obj" , swapyz=True))
    

    
    

    for i in range(len(objetos)): 
        objetos[i].generate()

#Se mueve al observador circularmente al rededor del plano XZ a una altura fija (EYE_Y)
def lookat():
    global EYE_X
    global EYE_Z
    global radius
    EYE_X = radius * (math.cos(math.radians(theta)) + math.sin(math.radians(theta)))
    EYE_Z = radius * (-math.sin(math.radians(theta)) + math.cos(math.radians(theta)))
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    
def SquidFace():
    glPushMatrix()  
    glTranslatef(Player_X, Player_Y , Player_Z)
    glRotatef(Player_Rotation, 0, 1, 0)  # Rotar el calamar según su orientación
    #correcciones para dibujar el objeto en plano XZ
    #esto depende de cada objeto
    #glRotatef(-90.0, 1.0, 0.0, 0.0)
    #glTranslatef(0.0, 15.0, 0.0)
    glScale(20.0,20.0,20.0)
    objetos[0].render()  
    glPopMatrix()
    
def SquidDer():
    glPushMatrix()
    glTranslatef(Player_X, Player_Y , Player_Z)
    glRotatef(Player_Rotation, 0, 1, 0)  # Rotar el calamar según su orientación
    glRotatef(-SquidT, 0, 1, 0)    # Rota en Y para simular el movimiento de nado de lado a lado
    glScale(20.0,20.0,20.0)
    objetos[1].render()
    glPopMatrix()

def SquidIzq():
    glPushMatrix()
    glTranslatef(Player_X, Player_Y , Player_Z)
    glRotatef(Player_Rotation, 0, 1, 0)  # Rotar el calamar según su orientación
    glRotatef(SquidT, 0, 1, 0)   # Rota en Y en el sentido contrario para simular el movimiento de nado
    glScale(20.0,20.0,20.0)
    objetos[2].render()
    glPopMatrix()
        
        
# Dibuja la maquina Wheel Loader
def Maquina():
    glPushMatrix()
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    
    #glTranslatef(100.0, 0.0 , 100.0)
    #glRotatef(0.0, 0, 1, 0)  
    glScale(10.0,10.0,10.0)
    objetos[3].render()
    glPopMatrix()
    
def MaquinaArm():
    glPushMatrix()
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 20.0 , -10.0) #ajuste de offset
    glRotatef(arm_angle, 1.0, 0.0, 0.0)  #Elevacion del brazo
    glScale(10.0,10.0,10.0)
    objetos[4].render()
    glPopMatrix()
    
def MaquinaFW():
    glPushMatrix()
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 10.0 , -19.0) #ajuste de offset
    glRotatef(wheel_rotate, 0.0, 1.0, 0.0)  #Vuelta de las ruedas delanteras
    glRotatef(wheel_angle, 1.0, 0.0, 0.0) #giro de las ruedas
    glScale(10.0,10.0,10.0)
    objetos[5].render()
    glPopMatrix()
    
def MaquinaBW():
    glPushMatrix()
    #Mover y rotar el carrito
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 10.0 , 21.0) #ajuste de offset
    #glRotatef(wheel_rotate, 0.0, 1.0, 0.0)
    glRotatef(wheel_angle, 1.0, 0.0, 0.0) #giro de las ruedas
    glScale(10.0,10.0,10.0)
    objetos[5].render()
    glPopMatrix()
    
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
    #Se dibuja el plano gris
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()

    #Calamar
    SquidFace()
    SquidDer()
    SquidIzq()
    #Maquina
    Maquina()
    MaquinaArm()
    MaquinaFW()
    MaquinaBW()
    
    
done = False
Init()
move_speed = 1.0
turn_speed = 1.0
while not done:
    keys = pygame.key.get_pressed()
    # Controles observador (flechas)
    if keys[pygame.K_RIGHT]:
        if theta > 359.0:
            theta = 0
        else:
            theta += 1.0
        lookat()
    if keys[pygame.K_LEFT]:
        if theta < 1.0:
            theta = 360.0
        else:
            theta += -1.0
        lookat()
        
    if keys[pygame.K_UP]:
        if radius > 1.0:
            radius += -1.0
        lookat()
        
    if keys[pygame.K_DOWN]:
        if radius < 900.0:
            radius += 1.0
        lookat()

    #Controles para prueba de calamar
    # Calcular dirección de movimiento basada en la rotación del calamar
    dir_x = math.sin(math.radians(Player_Rotation))
    dir_z = math.cos(math.radians(Player_Rotation))
    
    if keys[pygame.K_w]:
        SquidSwBack = 0  #Reset animacion S
        if SquidSw == 0:  #Adelante
            SquidT += 1.5
            if SquidT >= 45:
                SquidSw = 1  #Atras
        else:
            SquidT -= 2.5
            # Movimiento hacia adelante
            Player_X -= dir_x * 0.5
            Player_Z -= dir_z * 0.5
            
            if SquidT <= -10:
                SquidSw = 0  #reset adelante

    if keys[pygame.K_s]:
        SquidSw = 0  #Reset animacion W 
        if SquidSwBack == 0:  #Atras
            SquidT -= 2.5
            if SquidT <= -10:
                SquidSwBack = 1 #adelante
        else:
            SquidT += 1.5
            # Movimiento hacia atrás
            Player_X += dir_x * 0.3
            Player_Z += dir_z * 0.3
            
            if SquidT >= 45:
                SquidSwBack = 0 #reset atras
                
    if keys[pygame.K_d]:
        # Rotar el calamar a la izquierda
        Player_Rotation -= 2.0
        if Player_Rotation < 0:
            Player_Rotation += 360

    if keys[pygame.K_a]:
        # Rotar el calamar a la derecha
        Player_Rotation += 2.0
        if Player_Rotation >= 360:
            Player_Rotation -= 360   
            
             
#Maquina
    # Controles Carro (IJKL)
    rad = math.radians(car_angle)
    dir_x = math.sin(rad)
    dir_z = math.cos(rad)
    if keys[pygame.K_k]:
        Maquina_X += dir_x * move_speed
        Maquina_Z += dir_z * move_speed
        wheel_angle += 10.0  # Incrementa el ángulo de las ruedas al retroceder
        if wheel_angle <= -360.0:
            wheel_angle += 360.0
    if keys[pygame.K_i]:
        Maquina_X -= dir_x * move_speed
        Maquina_Z -= dir_z * move_speed
        wheel_angle -= 10.0  # Incrementa el ángulo de las ruedas al avanzar
        if wheel_angle >= 360.0:
            wheel_angle -= 360.0
    if keys[pygame.K_j]:
        car_angle += turn_speed
        wheel_rotate = 12.0  #valor para el ángulo de giro de las ruedas delanteras
    if keys[pygame.K_l]:
        car_angle -= turn_speed
        wheel_rotate = -12.0  # valor para el ángulo de giro de las ruedas delanteras
    if not (keys[pygame.K_j] or keys[pygame.K_l]):
        wheel_rotate = 0.0  # Vuelve las ruedas delanteras a la posición recta si no se gira
   
   #Control del brazo de la maquina (P)
    if keys[pygame.K_p]:
        arm_angle = 45.0  #valor para el ángulo de elevación del brazo
    if not keys[pygame.K_p]:
        arm_angle = -15.0  #Vuelve el brazo a la posición baja si no se presiona P
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    display()

    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()