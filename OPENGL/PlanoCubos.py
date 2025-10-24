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
Player_X = 0.0
Player_Y = 0.0
Player_Z = 0.0
# Ángulo de rotación del carrito
car_angle = 0.0
CENTER_X = 0
CENTER_Y = 0
CENTER_Z = 0
UP_X=0
UP_Y=1
UP_Z=0
# Variable para el ángulo de las ruedas
wheel_angle = 0.0
wheel_rotate = 0.0

#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500
Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 200

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
    pygame.display.set_caption("OpenGL: Carro")

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
    #objetos.append(OBJ("Chevrolet_Camaro_SS_Low.obj", swapyz=True))
    objetos.append(OBJ("Player_Squid/Squid.obj", swapyz=True)) #Necesario
    #objetos.append(OBJ("Llantas_tr90.obj", swapyz=True)) #Necesario
    #objetos.append(OBJ("Llantas_ad90.obj", swapyz=True)) #Test
    #objetos.append(OBJ("Llantas_ad_der.obj", swapyz=True))
    #objetos.append(OBJ("Llanta_ad_iz.obj", swapyz=True))

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
    
# Dibujado de Chasis con una matriz
#def displayChasis():
#    glPushMatrix()
#    glTranslatef(Player_X, Player_Y + 15.0, Player_Z)
#    #glTranslatef(0.0, 15.0, 0.0) #Ajusta la altura del chasis
#    glRotatef(car_angle, 0.0, 1.0, 0.0)
#    #glRotatef(-90.0, 1.0, 0.0, 0.0) #Rotar el chasis para que quede en plano XZ (Solo necesario para el chasis original)
#    glScale(10.0,10.0,10.0)
#    objetos[0].render()
#    glPopMatrix()

def displayChasis():
    glPushMatrix()
    theta_rad = math.radians(car_angle)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    # Resultado algebraico de: T · Ry · S
    chasis_matrix = [
        10.0 * cos_theta,          
        0.0,                         
        -10.0 * sin_theta,          
        0.0,                         
        
        0.0,                         
        10.0,                        
        0.0,                         
        0.0,                         
        
        10.0 * sin_theta,           
        0.0,                         
        10.0 * cos_theta,           
        0.0,                        
        
        Player_X,                   
        Player_Y + 15.0,            
        Player_Z,                  
        1.0                          
    ]
    glMultMatrixf(chasis_matrix)
    objetos[0].render()
    glPopMatrix() 
    
    
# def displayLlantas_tr():
#     glPushMatrix()
#     # Mover y rotar el carrito
#     glTranslatef(Player_X, Player_Y + 15.0, Player_Z)
#     glRotatef(car_angle, 0.0, 1.0, 0.0)
#     # Corrección para dibujar el objeto en plano XZ
#     #glRotatef(-90.0, 1.0, 0.0, 0.0)
#     #glTranslatef(0.0, 0.0, 15.0)
#     glScale(10.0,10.0,10.0)
#     #Ajuste para rotar las llantas traseras sobre su eje
#     glTranslatef(0.0, -0.66, 2.56) #Ajusta al nuevo punto de referencia
#     glRotatef(wheel_angle, 1.0, 0.0, 0.0)
#     glTranslatef(0.0, 0.66, -2.56)# Regresa al origen
#     objetos[1].render()
#     glPopMatrix()


def displayLlantas_tr():
    glPushMatrix()
    theta = math.radians(car_angle)      # rotación del carro alrededor de Y
    phi   = math.radians(wheel_angle)    # rotación de la rueda alrededor de X

    c = math.cos(theta)
    s = math.sin(theta)
    C = math.cos(phi)
    S = math.sin(phi)

    # 3x3 = 10 * (R_y(theta) * R_x(phi))
    # R_y * R_x = [[ c,   s*S,   s*C],
    #              [ 0,    C,    -S ],
    #              [-s,  c*S,   c*C ]]
    m00 = 10.0 * c
    m10 = 0.0
    m20 = -10.0 * s
    m30 = 0.0

    m01 = 10.0 * (s * S)
    m11 = 10.0 * C
    m21 = 10.0 * (c * S)
    m31 = 0.0

    m02 = 10.0 * (s * C)
    m12 = -10.0 * S
    m22 = 10.0 * (c * C)
    m32 = 0.0

    tx_offset = s * (25.6 + 6.6 * S - 25.6 * C)
    ty_offset = 6.6 * (C - 1.0) + 25.6 * S
    tz_offset = c * (25.6 + 6.6 * S - 25.6 * C)

    tx = Player_X + tx_offset
    ty = Player_Y + 15.0 + ty_offset
    tz = Player_Z + tz_offset

    # Colocar en orden column-major para glMultMatrixf
    llanta_tr_matrix = [
        m00, m10, m20, m30,
        m01, m11, m21, m31,
        m02, m12, m22, m32,
        tx,  ty,  tz,  1.0
    ]
    glMultMatrixf(llanta_tr_matrix)
    objetos[1].render()
    glPopMatrix()

#Maquinas de llantas delanteras
#def displayADder():
#    glPushMatrix()
#    glTranslatef(Player_X, Player_Y + 15.0, Player_Z) #15 es la altura del chasis
#    glRotatef(car_angle, 0.0, 1.0, 0.0)
#    glTranslatef(0.0, 0.0, -15.0)  # Ajuste al nuevo origen
#    glRotatef(wheel_rotate, 0.0, 1.0, 0.0)  # Giro de dirección en eje X
#    glTranslatef(0.0, 0.0, 15.0)  # Ajuste al nuevo origen
#    glTranslatef(0.0, -7.2, -32.2)  # Ajuste al nuevo origen
#    glRotatef(wheel_angle, 1.0, 0.0, 0.0)  # Rotación de la llanta sobre su eje
#    glTranslatef(0.0, 7.2, 32.2)   # Regresa al origen
#    glScale(10.0,10.0,10.0)
#    objetos[2].render()
#    objetos[3].render()
#    glPopMatrix()

def displayLlantas_ad():
    glPushMatrix()
    # ángulos en radianes
    th_car = math.radians(car_angle)        # orientación del carro
    th_wr  = math.radians(wheel_rotate)     # giro de dirección (volante)
    th_ws  = math.radians(wheel_angle)      # giro de la rueda (spin)

    # cos / sin auxiliares
    c_car = math.cos(th_car)
    s_car = math.sin(th_car)

    c_wr = math.cos(th_wr)
    s_wr = math.sin(th_wr)

    c_ws = math.cos(th_ws)
    s_ws = math.sin(th_ws)

    # suma de ángulos car + wheel_rotate
    th_sum = th_car + th_wr
    c_sum = math.cos(th_sum)   # cos(car + wheel_rotate)
    s_sum = math.sin(th_sum)   # sin(car + wheel_rotate)

    # Componentes de la matriz
    m00 = 10.0 * c_sum
    m10 = 0.0
    m20 = -10.0 * s_sum
    m30 = 0.0

    m01 = 10.0 * s_ws * s_sum
    m11 = 10.0 * c_ws
    m21 = 10.0 * s_ws * c_sum
    m31 = 0.0

    m02 = 10.0 * c_ws * s_sum
    m12 = -10.0 * s_ws
    m22 = 10.0 * c_ws * c_sum
    m32 = 0.0

    # Traslación resultante (Player_Y +15)
    # derivada algebraicamente de:
    # T(player) * R_y(car) * T(0,0,-15) * R_y(wheel_rotate) * T(0,0,15)
    # * T(0,-7.2,-32.2) * R_x(wheel_angle) * T(0,7.2,32.2) * S(10)
    t0 = (Player_X
          + 32.2 * c_ws * s_sum
          + 7.2  * s_sum * s_ws
          - 17.2 * s_sum
          - 15.0 * s_car)

    # equivalente a Player_Y + 7.8 + 7.2*c_ws - 32.2*s_ws
    t1 = (Player_Y
          + 7.8
          + 7.2 * c_ws
          - 32.2 * s_ws)

    t2 = (Player_Z
          + 32.2 * c_sum * c_ws
          + 7.2  * c_sum * s_ws
          - 17.2 * c_sum
          - 15.0 * c_car)

    m03 = t0
    m13 = t1
    m23 = t2
    m33 = 1.0

    wheel_matrix = [
        m00, m10, m20, m30,
        m01, m11, m21, m31,
        m02, m12, m22, m32,
        m03, m13, m23, m33
    ]

    glMultMatrixf(wheel_matrix)
    objetos[2].render()
    objetos[3].render()
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
    
    #Displays de los objetos
    displayChasis()
    displayLlantas_tr()
    displayLlantas_ad()
    
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

    # Controles Carro (WASD)
    rad = math.radians(car_angle)
    dir_x = math.sin(rad)
    dir_z = math.cos(rad)
    if keys[pygame.K_s]:
        Player_X += dir_x * move_speed
        Player_Z += dir_z * move_speed
        wheel_angle += 10.0  # Incrementa el ángulo de las ruedas al retroceder
        if wheel_angle <= -360.0:
            wheel_angle += 360.0
    if keys[pygame.K_w]:
        Player_X -= dir_x * move_speed
        Player_Z -= dir_z * move_speed
        wheel_angle -= 10.0  # Incrementa el ángulo de las ruedas al avanzar
        if wheel_angle >= 360.0:
            wheel_angle -= 360.0
    if keys[pygame.K_a]:
        car_angle += turn_speed
        wheel_rotate = 5.0  # Ajusta este valor para el ángulo de giro de las ruedas delanteras
    if keys[pygame.K_d]:
        car_angle -= turn_speed
        wheel_rotate = -5.0  # Ajusta este valor para el ángulo de giro de las ruedas delanteras
    if not (keys[pygame.K_a] or keys[pygame.K_d]):
        wheel_rotate = 0.0  # Vuelve las ruedas delanteras a la posición recta si no se gira

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()