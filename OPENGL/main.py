import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
#Librerias para la conexion
import time
import threading
import math
import requests

# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
# Import obj loader
from objloader import *

screen_width = 1200
screen_height = 800
#Manejo de peticiones de Julia
last_update_time = 0
update_interval = 0.1
cached_data = None  
data_lock = threading.Lock()
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
Squid_Scale = 20.0
Player_Rotation = 0.0  # Rotación del calamar en grados
SquidT = 0.0
SquidSw = 0
SquidSwBack = 0
Squid_R = 0.0

# Instancias adicionales de calamares (4 en total, la 0 corresponde al jugador actual)
# Cada instancia tiene coordenadas y rotación independientes
NUM_SQUIDS = 4
squid_instances = [
    {"x": 0.0,   "y": 0.0, "z": 0.0,   "rotation": 0.0},
    {"x": -80.0, "y": 0.0, "z": -80.0, "rotation": 0.0},
    {"x": 80.0,  "y": 0.0, "z": -80.0, "rotation": 0.0},
    {"x": 0.0,   "y": 0.0, "z": 120.0, "rotation": 0.0},
]

# Variables para el rastro de pintura
paint_trail = []  # Lista de puntos del rastro [(x, y, z), ...]
trail_width = 15.0  # Ancho del rastro
last_trail_x = Player_X
last_trail_z = Player_Z
min_trail_distance = 2.0  # Distancia mínima para agregar un nuevo punto al rastro

#variables de la maquina Wheel Loader
Maquina_X = 0.0
Maquina_Y = 0.0
Maquina_Z = 0.0
Maquina_Scale = 10.0
car_angle = 0.0
wheel_angle = 0.0
wheel_rotate = 0.0
arm_angle = -15.0  # Ángulo inicial del brazo
T_offset_y = 20.0
T_offset_z = -10.0

# Instancias adicionales de máquinas (4 en total, la 0 corresponde a la actual)
NUM_MACHINES = 4
machine_instances = [
    {"x": 0.0,   "y": 0.0, "z": 0.0,    "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0},
    {"x": 120.0, "y": 0.0, "z": 60.0,   "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0},
    {"x": -120.0,"y": 0.0, "z": 60.0,   "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0},
    {"x": 0.0,   "y": 0.0, "z": -140.0, "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0},
]


objetos = []

#Variables para el control del observador
theta = 0.0
radius = 300

# Helpers para actualizar instancias desde scripts externos (e.g., Julia)
def set_squid_instance(index, x=None, y=None, z=None, rotation=None):
    if index < 0 or index >= NUM_SQUIDS:
        return
    inst = squid_instances[index]
    if x is not None:
        inst["x"] = float(x)
    if y is not None:
        inst["y"] = float(y)
    if z is not None:
        inst["z"] = float(z)
    if rotation is not None:
        inst["rotation"] = float(rotation)

def set_machine_instance(index, x=None, y=None, z=None, car_angle=None, wheel_angle=None, wheel_rotate=None, arm_angle=None):
    if index < 0 or index >= NUM_MACHINES:
        return
    inst = machine_instances[index]
    if x is not None:
        inst["x"] = float(x)
    if y is not None:
        inst["y"] = float(y)
    if z is not None:
        inst["z"] = float(z)
    if car_angle is not None:
        inst["car_angle"] = float(car_angle)
    if wheel_angle is not None:
        inst["wheel_angle"] = float(wheel_angle)
    if wheel_rotate is not None:
        inst["wheel_rotate"] = float(wheel_rotate)
    if arm_angle is not None:
        inst["arm_angle"] = float(arm_angle)


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
    #environment 
    objetos.append(OBJ("Envirioment/ENVPortMakrel2.obj" , swapyz=True)) #6   

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
    #Calculo trigonometrico para la matriz de transformacion
    theta_rad = math.radians(Player_Rotation + Squid_R)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
        
    # Elementos de la columna 0
    m0 = cos_theta * Squid_Scale
    m2 = -sin_theta * Squid_Scale
    
    # Elementos de la columna 1
    m5 = Squid_Scale
    
    # Elementos de la columna 2
    m8 = sin_theta * Squid_Scale
    m10 = cos_theta * Squid_Scale
    
    # Elementos de la columna 3 (Traslación)
    m12 = Player_X
    m13 = Player_Y
    m14 = Player_Z

    # La lista final almacena referencias a los valores
    squid_matrix = [
        m0, 0.0, m2, 0.0,  # Columna 0
        0.0, m5, 0.0, 0.0,  # Columna 1
        m8, 0.0, m10, 0.0, # Columna 2
        m12, m13, m14, 1.0 # Columna 3
    ]
    glMultMatrixf(squid_matrix)
    objetos[0].render()
    glPopMatrix()

def SquidDer():
    glPushMatrix()
    
    # Calculo trigonometrico para la matriz de transformacion
    theta_rad = math.radians(Player_Rotation - SquidT)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
        
    # Elementos de la columna 0
    m0 = cos_theta * Squid_Scale
    m2 = -sin_theta * Squid_Scale
    
    # Elementos de la columna 1
    m5 = Squid_Scale
    
    # Elementos de la columna 2
    m8 = sin_theta * Squid_Scale
    m10 = cos_theta * Squid_Scale
    
    # Elementos de la columna 3 (Traslación)
    m12 = Player_X
    m13 = Player_Y
    m14 = Player_Z

    squid_matrix = [
        m0, 0.0, m2, 0.0,  # Columna 0
        0.0, m5, 0.0, 0.0,  # Columna 1
        m8, 0.0, m10, 0.0, # Columna 2
        m12, m13, m14, 1.0  # Columna 3
    ]
    
    glMultMatrixf(squid_matrix)
    objetos[1].render() 
    glPopMatrix() 

def SquidIzq():
    glPushMatrix()
    # El ángulo es (Player_Rotation + SquidT)
    theta_rad = math.radians(Player_Rotation + SquidT)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
            
    # Elementos de la columna 0
    m0 = cos_theta * Squid_Scale
    m2 = -sin_theta * Squid_Scale
    
    # Elementos de la columna 1
    m5 = Squid_Scale
    
    # Elementos de la columna 2
    m8 = sin_theta * Squid_Scale
    m10 = cos_theta * Squid_Scale
    
    # Elementos de la columna 3 (Traslación)
    m12 = Player_X
    m13 = Player_Y
    m14 = Player_Z

    squid_matrix = [
        m0, 0.0, m2, 0.0,  # Columna 0
        0.0, m5, 0.0, 0.0,  # Columna 1
        m8, 0.0, m10, 0.0, # Columna 2
        m12, m13, m14, 1.0  # Columna 3
    ]
    glMultMatrixf(squid_matrix)
    objetos[2].render()
    glPopMatrix()
     
        
# Dibuja la maquina Wheel Loader
def Maquina():
    glPushMatrix()   
    # (Rotación en Y)
    theta_rad = math.radians(car_angle)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    # (Resultado T * Ry * S)
    
    # Elementos de la columna 0
    m0 = cos_theta * Maquina_Scale
    m2 = -sin_theta * Maquina_Scale
    
    # Elementos de la columna 1
    m5 = Maquina_Scale
    
    # Elementos de la columna 2
    m8 = sin_theta * Maquina_Scale
    m10 = cos_theta * Maquina_Scale
    
    # Elementos de la columna 3 (Traslación)
    m12 = Maquina_X
    m13 = Maquina_Y
    m14 = Maquina_Z

    maquina_matrix = [
        m0, 0.0, m2, 0.0,  # Columna 0
        0.0, m5, 0.0, 0.0,  # Columna 1
        m8, 0.0, m10, 0.0, # Columna 2
        m12, m13, m14, 1.0  # Columna 3
    ]
    
    glMultMatrixf(maquina_matrix)
    objetos[3].render()
    glPopMatrix()
    
def MaquinaArm():
    glPushMatrix()
    Sc = Maquina_Scale # Alias corto para la escala
    # Ángulo del chasis (Rotación en Y)
    rad_car = math.radians(car_angle)
    ct = math.cos(rad_car) # cos(theta)
    st = math.sin(rad_car) # sin(theta)
    
    # Ángulo del brazo (Rotación en X)
    rad_arm = math.radians(arm_angle)
    ca = math.cos(rad_arm) # cos(alpha)
    sa = math.sin(rad_arm) # sin(alpha)
    
    # Esta es la parte de Rotación (Ry * Rx) y Escala (S)
    # Elementos de la columna 0 (Ry * Rx * S)[Col 0]
    m0 = ct * Sc
    m2 = -st * Sc  # (Estándar GL)
    
    # Elementos de la columna 1 (Ry * Rx * S)[Col 1]
    m4 = st * sa * Sc
    m5 = ca * Sc
    m6 = ct * sa * Sc
    
    # Elementos de la columna 2 (Ry * Rx * S)[Col 2]
    m8 = st * ca * Sc
    m9 = -sa * Sc
    m10 = ct * ca * Sc
    
    m12 = Maquina_X - (T_offset_z * st) # Maquina_X + (-10.0 * st)
    
    m12 = Maquina_X + (T_offset_z * st)
    m13 = Maquina_Y + T_offset_y
    m14 = Maquina_Z + (T_offset_z * ct)

    # --- 4. Definir la matriz (formato Column-Major) ---
    maquina_arm_matrix = [
        m0, 0.0, m2, 0.0,   # Columna 0
        m4, m5, m6, 0.0,   # Columna 1
        m8, m9, m10, 0.0,  # Columna 2
        m12, m13, m14, 1.0   # Columna 3
    ]
    glMultMatrixf(maquina_arm_matrix)
    objetos[4].render()
    glPopMatrix()
    
def MaquinaFW():
    glPushMatrix()
    Sc = Maquina_Scale # Alias corto para la escala
    rad_car = math.radians(car_angle)
    ct_c = math.cos(rad_car) # cos(theta) del chasis
    st_c = math.sin(rad_car) # sin(theta) del chasis

    #Trig para la ROTACIÓN 
    # A. Ángulo combinado Ry(car_angle) * Ry(wheel_rotate) = Ry(car_angle + wheel_rotate)
    rad_combo = math.radians(car_angle + wheel_rotate)
    ct_r = math.cos(rad_combo) # cos(theta) rotación combinada
    st_r = math.sin(rad_combo) # sin(theta) rotación combinada
    
    # B. Ángulo del giro (Rx)
    rad_wheel_x = math.radians(wheel_angle)
    ca_w = math.cos(rad_wheel_x) # cos(alpha) de la rueda
    sa_w = math.sin(rad_wheel_x) # sin(alpha) de la rueda
    
    m12 = Maquina_X - (19.0 * st_c)
    m13 = Maquina_Y + 10.0
    m14 = Maquina_Z - (19.0 * ct_c)

    # R_final = Ry(combo) * Rx(wheel) * S
    # Elementos de la columna 0
    m0 = ct_r * Sc
    m2 = -st_r * Sc
    
    # Elementos de la columna 1
    m4 = st_r * sa_w * Sc
    m5 = ca_w * Sc
    m6 = ct_r * sa_w * Sc
    
    # Elementos de la columna 2
    m8 = st_r * ca_w * Sc
    m9 = -sa_w * Sc
    m10 = ct_r * ca_w * Sc

    # --- 5. Definir la matriz (formato Column-Major) ---
    maquina_fw_matrix = [
        m0, 0.0, m2, 0.0,   # Columna 0
        m4, m5, m6, 0.0,   # Columna 1
        m8, m9, m10, 0.0,  # Columna 2
        m12, m13, m14, 1.0   # Columna 3
    ]
    
    glMultMatrixf(maquina_fw_matrix)
    objetos[5].render()
    glPopMatrix()
    
def MaquinaBW():
    glPushMatrix()
    Sc = Maquina_Scale # Alias corto para la escala
    # --- 1. Trig para la TRASLACIÓN y ROTACIÓN Ry ---
    # (Depende de car_angle)
    rad_car = math.radians(car_angle)
    ct = math.cos(rad_car) # cos(theta) chasis
    st = math.sin(rad_car) # sin(theta) chasis

    #Trig para la ROTACIÓN Rx
    # (Depende de wheel_angle)
    rad_wheel = math.radians(wheel_angle)
    ca_w = math.cos(rad_wheel) # cos(alpha) rueda
    sa_w = math.sin(rad_wheel) # sin(alpha) rueda
    
    m12 = Maquina_X + (21.0 * st)
    m13 = Maquina_Y + 10.0
    m14 = Maquina_Z + (21.0 * ct)
    
    # Elementos de la columna 0
    m0 = ct * Sc
    m2 = -st * Sc
    
    # Elementos de la columna 1
    m4 = st * sa_w * Sc
    m5 = ca_w * Sc
    m6 = ct * sa_w * Sc
    
    # Elementos de la columna 2
    m8 = st * ca_w * Sc
    m9 = -sa_w * Sc
    m10 = ct * ca_w * Sc

    # (Usando 0.0 y 1.0 directamente para ahorrar variables)
    maquina_bw_matrix = [
        m0, 0.0, m2, 0.0,   # Columna 0
        m4, m5, m6, 0.0,   # Columna 1
        m8, m9, m10, 0.0,  # Columna 2
        m12, m13, m14, 1.0   # Columna 3
    ]
    glMultMatrixf(maquina_bw_matrix)
    objetos[5].render()
    glPopMatrix()

def DrawMachineInstance(inst):
    # Dibuja una instancia completa de la máquina (base, brazo, ruedas) con sus propias coordenadas
    x = inst.get("x", 0.0)
    y = inst.get("y", 0.0)
    z = inst.get("z", 0.0)
    car_ang = inst.get("car_angle", 0.0)
    wh_ang = inst.get("wheel_angle", 0.0)
    wh_rot = inst.get("wheel_rotate", 0.0)
    arm_ang = inst.get("arm_angle", -15.0)

    # Base
    glPushMatrix()
    theta_rad = math.radians(car_ang)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    m0 = cos_theta * Maquina_Scale
    m2 = -sin_theta * Maquina_Scale
    m5 = Maquina_Scale
    m8 = sin_theta * Maquina_Scale
    m10 = cos_theta * Maquina_Scale
    m12 = x
    m13 = y
    m14 = z
    maquina_matrix = [
        m0, 0.0, m2, 0.0,
        0.0, m5, 0.0, 0.0,
        m8, 0.0, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(maquina_matrix)
    objetos[3].render()
    glPopMatrix()

    # Brazo
    glPushMatrix()
    Sc = Maquina_Scale
    rad_car = math.radians(car_ang)
    ct = math.cos(rad_car)
    st = math.sin(rad_car)
    rad_arm = math.radians(arm_ang)
    ca = math.cos(rad_arm)
    sa = math.sin(rad_arm)
    m0 = ct * Sc
    m2 = -st * Sc
    m4 = st * sa * Sc
    m5 = ca * Sc
    m6 = ct * sa * Sc
    m8 = st * ca * Sc
    m9 = -sa * Sc
    m10 = ct * ca * Sc
    m12 = x + (T_offset_z * st)
    m13 = y + T_offset_y
    m14 = z + (T_offset_z * ct)
    maquina_arm_matrix = [
        m0, 0.0, m2, 0.0,
        m4, m5, m6, 0.0,
        m8, m9, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(maquina_arm_matrix)
    objetos[4].render()
    glPopMatrix()

    # Ruedas delanteras
    glPushMatrix()
    Sc = Maquina_Scale
    rad_combo = math.radians(car_ang + wh_rot)
    ct_r = math.cos(rad_combo)
    st_r = math.sin(rad_combo)
    rad_wheel_x = math.radians(wh_ang)
    ca_w = math.cos(rad_wheel_x)
    sa_w = math.sin(rad_wheel_x)
    rad_car = math.radians(car_ang)
    ct_c = math.cos(rad_car)
    st_c = math.sin(rad_car)
    m12 = x - (19.0 * st_c)
    m13 = y + 10.0
    m14 = z - (19.0 * ct_c)
    m0 = ct_r * Sc
    m2 = -st_r * Sc
    m4 = st_r * sa_w * Sc
    m5 = ca_w * Sc
    m6 = ct_r * sa_w * Sc
    m8 = st_r * ca_w * Sc
    m9 = -sa_w * Sc
    m10 = ct_r * ca_w * Sc
    maquina_fw_matrix = [
        m0, 0.0, m2, 0.0,
        m4, m5, m6, 0.0,
        m8, m9, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(maquina_fw_matrix)
    objetos[5].render()
    glPopMatrix()

    # Ruedas traseras
    glPushMatrix()
    Sc = Maquina_Scale
    rad_car = math.radians(car_ang)
    ct = math.cos(rad_car)
    st = math.sin(rad_car)
    rad_wheel = math.radians(wh_ang)
    ca_w = math.cos(rad_wheel)
    sa_w = math.sin(rad_wheel)
    m12 = x + (21.0 * st)
    m13 = y + 10.0
    m14 = z + (21.0 * ct)
    m0 = ct * Sc
    m2 = -st * Sc
    m4 = st * sa_w * Sc
    m5 = ca_w * Sc
    m6 = ct * sa_w * Sc
    m8 = st * ca_w * Sc
    m9 = -sa_w * Sc
    m10 = ct * ca_w * Sc
    maquina_bw_matrix = [
        m0, 0.0, m2, 0.0,
        m4, m5, m6, 0.0,
        m8, m9, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(maquina_bw_matrix)
    objetos[5].render()
    glPopMatrix()

def DrawSquidInstance(inst):
    # Dibuja una instancia de calamar completa (cara, brazo der, brazo izq) con sus propias coordenadas
    # Usa la misma escala global pero rotación/posición independientes
    x = inst.get("x", 0.0)
    y = inst.get("y", 0.0)
    z = inst.get("z", 0.0)
    rot = inst.get("rotation", 0.0)

    # Cara
    glPushMatrix()
    theta_rad = math.radians(rot)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    m0 = cos_theta * Squid_Scale
    m2 = -sin_theta * Squid_Scale
    m5 = Squid_Scale
    m8 = sin_theta * Squid_Scale
    m10 = cos_theta * Squid_Scale
    m12 = x
    m13 = y
    m14 = z
    squid_matrix = [
        m0, 0.0, m2, 0.0,
        0.0, m5, 0.0, 0.0,
        m8, 0.0, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(squid_matrix)
    objetos[0].render()
    glPopMatrix()

    # Brazo derecho (sin animación, usando leve offset angular)
    glPushMatrix()
    theta_rad = math.radians(rot - 5.0)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    m0 = cos_theta * Squid_Scale
    m2 = -sin_theta * Squid_Scale
    m5 = Squid_Scale
    m8 = sin_theta * Squid_Scale
    m10 = cos_theta * Squid_Scale
    m12 = x
    m13 = y
    m14 = z
    squid_matrix = [
        m0, 0.0, m2, 0.0,
        0.0, m5, 0.0, 0.0,
        m8, 0.0, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(squid_matrix)
    objetos[1].render()
    glPopMatrix()

    # Brazo izquierdo (sin animación, usando leve offset angular)
    glPushMatrix()
    theta_rad = math.radians(rot + 5.0)
    cos_theta = math.cos(theta_rad)
    sin_theta = math.sin(theta_rad)
    m0 = cos_theta * Squid_Scale
    m2 = -sin_theta * Squid_Scale
    m5 = Squid_Scale
    m8 = sin_theta * Squid_Scale
    m10 = cos_theta * Squid_Scale
    m12 = x
    m13 = y
    m14 = z
    squid_matrix = [
        m0, 0.0, m2, 0.0,
        0.0, m5, 0.0, 0.0,
        m8, 0.0, m10, 0.0,
        m12, m13, m14, 1.0
    ]
    glMultMatrixf(squid_matrix)
    objetos[2].render()
    glPopMatrix()

def DrawPaintTrail():
    """Dibuja el rastro de pintura del calamar en el suelo"""
    if len(paint_trail) < 2:
        return
    
    # Deshabilitar iluminación para el rastro (opcional, para mejor visibilidad)
    glDisable(GL_LIGHTING)
    
    # Color del rastro (magenta/rosa estilo Splatoon)
    glColor3f(1.0, 0.2, 0.8)  # Rosa brillante
    
    # Dibujar el rastro como una serie de quads conectados
    glBegin(GL_QUADS)
    for i in range(len(paint_trail) - 1):
        x1, y1, z1 = paint_trail[i]
        x2, y2, z2 = paint_trail[i + 1]
        
        # Calcular dirección perpendicular al segmento
        dx = x2 - x1
        dz = z2 - z1
        length = math.sqrt(dx * dx + dz * dz)
        if length > 0:
            # Vector perpendicular normalizado
            perp_x = -dz / length
            perp_z = dx / length
            
            # Calcular los 4 vértices del quad
            half_width = trail_width / 2.0
            v1_x = x1 + perp_x * half_width
            v1_z = z1 + perp_z * half_width
            v2_x = x1 - perp_x * half_width
            v2_z = z1 - perp_z * half_width
            v3_x = x2 - perp_x * half_width
            v3_z = z2 - perp_z * half_width
            v4_x = x2 + perp_x * half_width
            v4_z = z2 + perp_z * half_width
            
            y_offset = 0.5 #offset para evitar conflictos
            glVertex3f(v1_x, y1 + y_offset, v1_z)
            glVertex3f(v2_x, y1 + y_offset, v2_z)
            glVertex3f(v3_x, y2 + y_offset, v3_z)
            glVertex3f(v4_x, y2 + y_offset, v4_z)
    
    glEnd()
    
    # Rehabilitar iluminación
    glEnable(GL_LIGHTING)

def UpdatePaintTrail():
    """Actualiza el rastro de pintura agregando un nuevo punto si el calamar se ha movido suficiente"""
    global last_trail_x, last_trail_z, paint_trail
    
    # Calcular distancia desde el último punto del rastro
    dx = Player_X - last_trail_x
    dz = Player_Z - last_trail_z
    distance = math.sqrt(dx * dx + dz * dz)
    
    # Si el calamar se ha movido suficiente, agregar un nuevo punto al rastro
    if distance >= min_trail_distance:
        paint_trail.append((Player_X, Player_Y, Player_Z))
        last_trail_x = Player_X
        last_trail_z = Player_Z
        
        # Limitar el tamaño del rastro para evitar problemas de rendimiento
        max_trail_points = 500
        if len(paint_trail) > max_trail_points:
            paint_trail.pop(0)  # Eliminar el punto más antiguo
    
# MUY IMPORTANTE CABRON -  aqui se maneja las peticiones a julia pero a segundo plano, la puedes modificar para que se reduzcan o aumenten las peticiones
def fetch_data_background():
    global cached_data, last_update_time
    
    while not done:
        try:
            current_time = time.time()
            if current_time - last_update_time >= update_interval:
                res = requests.get("http://localhost:8000/run", timeout=1)
                data = res.json()
                
                # Guardar datos
                with data_lock:
                    cached_data = data
                    last_update_time = current_time
        except Exception as e:
            print(f"Error en background: {e}")
        
        time.sleep(0.05)  

def display():
    global Player_X, Player_Z, Maquina_X, Maquina_Z, cached_data

    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
    
    #Dibujo del plano gris
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()

    DrawPaintTrail()

    #Calamar (jugador/controlado)
    SquidFace()
    SquidDer()
    SquidIzq()
    # Calamares adicionales (instancias 1..N)
    for i in range(1, NUM_SQUIDS):
        DrawSquidInstance(squid_instances[i])

    #Maquina (controlada)
    Maquina()
    MaquinaArm()
    MaquinaFW()
    MaquinaBW()
    # Máquinas adicionales (instancias 1..N)
    for i in range(1, NUM_MACHINES):
        DrawMachineInstance(machine_instances[i])
    
    
done = False
Init()

# Actualizacion background
update_thread = threading.Thread(target=fetch_data_background, daemon=True)
update_thread.start()

#Se jalan los datos iniciales: El Json basicamente, este esta en el wepapi de Julia
try:
    res = requests.get("http://localhost:8000/run", timeout=2)
    cached_data = res.json()
except Exception as e:
    print(f"Error inicial: {e}")

# Inicializar el rastro
paint_trail.append((Player_X, Player_Y, Player_Z))
last_trail_x = Player_X
last_trail_z = Player_Z
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
        if Squid_R > 0:
            Squid_R -= 2.5  # Doble velocidad de recuperación de rotación
        if Squid_R < 0:
            Squid_R += 2.5
        if SquidSw == 0:  #Adelante
            SquidT += 4.0  # Animacion más rápida
            if SquidT >= 45:
                SquidSw = 1  #Atras
        else:
            SquidT -= 6.0  # Animacion más rápida
            # Movimiento hacia adelante
            Player_X -= dir_x * 1.5  # Más rápido
            Player_Z -= dir_z * 1.5
            
            if SquidT <= -10:
                SquidSw = 0  #reset adelante

    if keys[pygame.K_s]:
        SquidSw = 0  #Reset animacion W 
        if Squid_R < 0:
            Squid_R += 4.0  # Doble velocidad de recuperación de rotación
        if SquidSwBack == 0:  #Atras
            SquidT -= 6.0  # Animacion más rápida
            if SquidT <= -10:
                SquidSwBack = 1 #adelante
        else:
            SquidT += 4.0  # Animacion más rápida
            # Movimiento hacia atrás
            Player_X += dir_x * 1.0  # Más rápido que antes
            Player_Z += dir_z * 1.0
            
            if SquidT >= 45:
                SquidSwBack = 0 #reset atras
                
    if keys[pygame.K_d]:
        if Squid_R > -25:
            Squid_R -= 2.0
            
        # Rotar el calamar a la izquierda
        Player_Rotation -= 2.0
        if Player_Rotation < 0:
            Player_Rotation += 360

    if keys[pygame.K_a]:
        if Squid_R < 25:
            Squid_R += 2.0
        # Rotar el calamar a la derecha
        Player_Rotation += 2.0
        if Player_Rotation >= 360:
            Player_Rotation -= 360   
            
             
    #Control de la maquina Wheel Loader
    heading = car_angle + wheel_rotate
    rad_h = math.radians(heading)
    dir_x = math.sin(rad_h)
    dir_z = math.cos(rad_h)

    if keys[pygame.K_k]:
        Maquina_X += dir_x * move_speed
        Maquina_Z += dir_z * move_speed
        # Girar lentamente el cuerpo del carro hacia la dirección de las ruedas
        car_angle -= (wheel_rotate) * 0.02
        # Rotación de las ruedas (visual)
        wheel_angle += 10.0
        if wheel_angle <= -360.0:
            wheel_angle += 360.0

    if keys[pygame.K_i]:
        Maquina_X -= dir_x * move_speed
        Maquina_Z -= dir_z * move_speed
        # Al ir en reversa, el carro gira en sentido contrario respecto al giro de las ruedas
        car_angle += (wheel_rotate) * 0.02
        wheel_angle -= 10.0
        if wheel_angle >= 360.0:
            wheel_angle -= 360.0
    if keys[pygame.K_j]:
        #car_angle += turn_speed
        if wheel_rotate < 15.0:  # Limita el ángulo de giro máximo
            wheel_rotate += turn_speed  #valor para el ángulo de giro de las ruedas delanteras
    if keys[pygame.K_l]:
        #car_angle -= turn_speed
        if wheel_rotate > -15.0:  # Limita el ángulo de giro máximo
            wheel_rotate -= turn_speed  #valor para el ángulo de giro de las ruedas delanteras  
           
                
    if keys[pygame.K_p]:
        if arm_angle < 45.0:  # Maximum angle limit
            arm_angle += 2.0  # Gradually increase
    else:  # When P is not pressed
        if arm_angle > -15.0:  # Minimum angle limit
            arm_angle -= 2.0  # Gradually decrease
   
   #Control del brazo de la maquina (P)
   # if keys[pygame.K_p]:
   #     arm_angle = 45.0  #valor para el ángulo de elevación del brazo
   # if not keys[pygame.K_p]:
   #     arm_angle = -15.0  #Vuelve el brazo a la posición baja si no se presiona P
    
    # Actualizar el rastro de pintura del calamar
    UpdatePaintTrail()
    
    # Sincroniza la instancia 0 con el calamar/máquina controlados por teclado
    squid_instances[0]["x"] = Player_X
    squid_instances[0]["y"] = Player_Y
    squid_instances[0]["z"] = Player_Z
    squid_instances[0]["rotation"] = Player_Rotation

    machine_instances[0]["x"] = Maquina_X
    machine_instances[0]["y"] = Maquina_Y
    machine_instances[0]["z"] = Maquina_Z
    machine_instances[0]["car_angle"] = car_angle
    machine_instances[0]["wheel_angle"] = wheel_angle
    machine_instances[0]["wheel_rotate"] = wheel_rotate
    machine_instances[0]["arm_angle"] = arm_angle
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()