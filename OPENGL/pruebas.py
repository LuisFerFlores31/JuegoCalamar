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
from skybox import *


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
ZFAR=5000.0
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
DimBoard = 200 #200
 
#Variables del calamar
Player_X = 0.0
Player_Y = 0.0
Player_Z = 0.0
Squid_Scale = 15.0
Player_Rotation = 0.0  # Rotación del calamar en grados
SquidT = 0.0
SquidSw = 0
SquidSwBack = 0
Squid_R = 0.0

# Instancias adicionales de calamares (4 en total, la 0 corresponde al jugador actual)
# Cada instancia tiene coordenadas y rotación independientes
NUM_SQUIDS = 4
# pacman_positions = [(10, 10), (31, 10), (10, 31), (31, 31)]
# Multiplicadas por 10 para OpenGL
squid_instances = [
    {"x": 120.0,   "y": 0.0, "z": 80.0,   "rotation": 0.0, 
    "target_x": 120.0, "target_z": 80.0,  # Coordenadas objetivo desde Julia
    "paint_trail": [], "last_trail_x": 120.0, "last_trail_z": 80.0, #0,0
    # Animacion/estado interno (por instancia)
    "squidT": 0.0, "squidSw": 0, "squidSwBack": 0, "squid_R": 0.0},  # Rastro independiente
    {"x": 80.0, "y": 0.0, "z": -80.0, "rotation": 0.0, #Azul
    "target_x": 80.0, "target_z": -80.0, # Coordenadas
    "paint_trail": [], "last_trail_x": 80.0, "last_trail_z": -80.0,
    "squidT": 0.0, "squidSw": 0, "squidSwBack": 0, "squid_R": 0.0},
    {"x": -80.0,  "y": 0.0, "z": 80.0, "rotation": 0.0, 
    "target_x": -80.0, "target_z": 80.0,
    "paint_trail": [], "last_trail_x": -80.0, "last_trail_z": 80.0,
    "squidT": 0.0, "squidSw": 0, "squidSwBack": 0, "squid_R": 0.0},
    {"x": -120.0,   "y": 0.0, "z": -120.0, "rotation": 0.0, #0,120
    "target_x": -120.0, "target_z": -120.0,
    "paint_trail": [], "last_trail_x": -120.0, "last_trail_z": -120.0,
    "squidT": 0.0, "squidSw": 0, "squidSwBack": 0, "squid_R": 0.0},
]

# Variables para el rastro de pintura del calamar controlado por teclado (instancia 0)
paint_trail = []  # Lista de puntos del rastro [(x, y, z), ...]
trail_width = 15.0  # Ancho del rastro
last_trail_x = Player_X
last_trail_z = Player_Z
min_trail_distance = 2.0  # Distancia mínima para agregar un nuevo punto al rastro

# Velocidad de movimiento suave hacia las coordenadas objetivo
squid_move_speed = 2.0  # Velocidad de interpolación (unidades por frame)
squid_rotation_speed = 5.0  # Velocidad de rotación (grados por frame)

# Velocidad de movimiento y rotación para máquinas
machine_move_speed = 1.0  # Velocidad de interpolación (unidades por frame)
machine_car_rotation_speed = 0.02  # Velocidad de rotación del cuerpo hacia las ruedas (factor)
machine_wheel_rotation_speed = 10.0  # Velocidad de rotación visual de las ruedas (grados por frame)

#variables de la maquina Wheel Loader
Maquina_X = 0.0
Maquina_Y = 0.0
Maquina_Z = 0.0
Maquina_Scale = 6.0
car_angle = 0.0
wheel_angle = 0.0
wheel_rotate = 0.0
arm_angle = -15.0  # Ángulo inicial del brazo
T_offset_y = 15.0
T_offset_z = -6.0

# Instancias adicionales de máquinas (4 en total, la 0 corresponde a la actual)
NUM_MACHINES = 4
machine_instances = [
    {"x": -180.0,   "y": 0.0, "z": -180.0,    "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0,
     "target_x": -180.0, "target_z": -180.0, "is_moving_forward": False, "is_moving_backward": False},
    {"x": 200.0, "y": 0.0, "z": -180.0,   "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0,
     "target_x": 200.0, "target_z": -180.0, "is_moving_forward": False, "is_moving_backward": False},
    {"x": -180.0,"y": 0.0, "z": 200.0,   "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0,
     "target_x": -180.0, "target_z": 200.0, "is_moving_forward": False, "is_moving_backward": False},
    {"x": 200.0,   "y": 0.0, "z": 200.0, "car_angle": 0.0, "wheel_angle": 0.0, "wheel_rotate": 0.0, "arm_angle": -15.0,
     "target_x": 200.0, "target_z": 200.0, "is_moving_forward": False, "is_moving_backward": False},
]


objetos = []

#Variables para el control del observador
theta = 0.0
radius = 300
skybox = None


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
    #Maquina
    #Maquina
    objetos.append(OBJ("WheelLoader/BaseMaquina.obj" , swapyz=True)) #3
    objetos.append(OBJ("WheelLoader/GArmMaquina.obj" , swapyz=True)) #4
    objetos.append(OBJ("WheelLoader/GWMaquina.obj" , swapyz=True)) #5
    #environment 
    objetos.append(OBJ("Envirioment/ENVPortMakrel2.obj" , swapyz=True)) #6   

    for i in range(len(objetos)): 
        objetos[i].generate()
        
    # Inicializar skybox
    global skybox
    skybox_path = "sky_10_2k/sky_10_cubemap_2k/sky_10_cubemap_2k"
    skybox = Skybox(skybox_path)

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
    m12 = x - (10.0 * st_c)
    m13 = y + 7.0
    m14 = z - (10.0 * ct_c)
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
    m12 = x + (13.0 * st)
    m13 = y + 6.0
    m14 = z + (13.0 * ct)
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

    # Animación: usar per-instance squid_R y squidT para face/arms
    squidT = inst.get("squidT", 0.0)
    squid_R_inst = inst.get("squid_R", 0.0)

    # Cara (usa rotation + squid_R)
    glPushMatrix()
    theta_rad = math.radians(rot + squid_R_inst)
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

    # Brazo derecho (animado con -squidT)
    glPushMatrix()
    theta_rad = math.radians(rot - squidT)
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

    # Brazo izquierdo (animado con +squidT)
    glPushMatrix()
    theta_rad = math.radians(rot + squidT)
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

def DrawSquidTrail(trail_points, color):
    """Dibuja el rastro de pintura de un calamar específico con un color dado"""
    if len(trail_points) < 2:
        return
    
    # Deshabilitar iluminación para el rastro
    glDisable(GL_LIGHTING)
    
    # Usar el color especificado
    glColor3f(color[0], color[1], color[2])
    
    # Dibujar el rastro como una serie de quads conectados
    glBegin(GL_QUADS)
    for i in range(len(trail_points) - 1):
        x1, y1, z1 = trail_points[i]
        x2, y2, z2 = trail_points[i + 1]
        
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
            
            y_offset = 0.8 #offset para evitar conflictos
            glVertex3f(v1_x, y1 + y_offset, v1_z)
            glVertex3f(v2_x, y1 + y_offset, v2_z)
            glVertex3f(v3_x, y2 + y_offset, v3_z)
            glVertex3f(v4_x, y2 + y_offset, v4_z)
    
    glEnd()
    
    # Rehabilitar iluminación
    glEnable(GL_LIGHTING)

def UpdateSquidSmoothMovement():
    """Actualiza el movimiento suave de todos los calamares hacia sus coordenadas objetivo"""
    global squid_move_speed
    
    for i in range(NUM_SQUIDS):
        inst = squid_instances[i]
        current_x = inst["x"]
        current_z = inst["z"]
        target_x = inst["target_x"]
        target_z = inst["target_z"]

        # Calcular distancia al objetivo
        dx = target_x - current_x
        dz = target_z - current_z
        distance = math.sqrt(dx * dx + dz * dz)

        prev_x = current_x
        prev_z = current_z
        prev_rot = inst.get("rotation", 0.0)

        # Calcular rotación objetivo hacia la dirección de movimiento
        current_rot = inst.get("rotation", 0.0)
        target_rot = current_rot  # Por defecto, mantener rotación actual
        
        if distance > 0.001:  # Solo calcular si hay movimiento
            # Calcular ángulo objetivo hacia la dirección de movimiento
            dir_x = dx / distance
            dir_z = dz / distance
            angle_rad = math.atan2(-dir_x, -dir_z)  # Negativo porque en OpenGL Z positivo es hacia atrás
            target_rot = math.degrees(angle_rad)
            if target_rot < 0:
                target_rot += 360
            
            # Calcular la diferencia de ángulo (manejar wrap-around 0-360)
            rot_diff = ((target_rot - current_rot + 180) % 360) - 180
            
            # Rotar gradualmente hacia el objetivo
            if abs(rot_diff) > 0.1:  # Si hay diferencia significativa
                if rot_diff > 0:
                    # Rotar en sentido horario (derecha)
                    new_rot = current_rot + min(squid_rotation_speed, rot_diff)
                else:
                    # Rotar en sentido antihorario (izquierda)
                    new_rot = current_rot + max(-squid_rotation_speed, rot_diff)
                
                # Normalizar a rango 0-360
                if new_rot >= 360:
                    new_rot -= 360
                elif new_rot < 0:
                    new_rot += 360
                
                inst["rotation"] = new_rot
            else:
                # Ya está orientado correctamente
                inst["rotation"] = target_rot
        
        # Si está cerca del objetivo, mover directamente
        if distance <= squid_move_speed:
            inst["x"] = target_x
            inst["z"] = target_z
        else:
            # Mover hacia el objetivo con velocidad constante
            dir_x = dx / distance
            dir_z = dz / distance
            inst["x"] += dir_x * squid_move_speed
            inst["z"] += dir_z * squid_move_speed

        # --- Animacion por instancia (simula hold de teclas) ---
        moved_x = inst["x"] - prev_x
        moved_z = inst["z"] - prev_z
        move_dist = math.hypot(moved_x, moved_z)

        # Direccion local del squid (forward vector)
        rad_rot = math.radians(inst.get("rotation", 0.0))
        fdx = math.sin(rad_rot)
        fdz = math.cos(rad_rot)

        # Componente forward/backward: producto punto
        forward_comp = moved_x * fdx + moved_z * fdz

        # Referencias a variables de animacion por instancia
        squidT = inst.get("squidT", 0.0)
        squidSw = inst.get("squidSw", 0)
        squidSwBack = inst.get("squidSwBack", 0)
        squid_R = inst.get("squid_R", 0.0)

        # Ajuste por rotacion (simula presionar A/D) - PRIORIDAD ALTA
        # Calcular la diferencia de rotación actual vs objetivo para determinar dirección
        rot_delta = ((inst.get("rotation", 0.0) - prev_rot + 540) % 360) - 180
        is_rotating = abs(rot_delta) > 0.1
        
        if is_rotating:
            # Está rotando: actualizar squid_R basado en la dirección de rotación
            if rot_delta > 0:
                # rotacion aumentó (girando a la derecha) -> similar a 'a' en tu control original
                if squid_R < 25:
                    squid_R += 4.0
            else:
                # rotacion disminuyó (girando a la izquierda) -> similar a 'd'
                if squid_R > -25:
                    squid_R -= 4.0

        # Movimiento hacia adelante (nota: en tu control original forward producia delta negativo
        # al comparar con dir; aqui usamos forward_comp: si es negativo significa que la posicion
        # cambió en sentido -fd (recordar signos), pero para seguridad empleamos umbrales)
        if move_dist > 0.001 and forward_comp < 0:
            squidSwBack = 0
            # Solo ajustar squid_R si no está rotando (la rotación tiene prioridad)
            if not is_rotating:
                if squid_R > 0:
                    squid_R -= 2.5
                if squid_R < 0:
                    squid_R += 2.5
            if squidSw == 0:
                squidT += 4.0
                if squidT >= 45:
                    squidSw = 1
            else:
                squidT -= 6.0
                if squidT <= -10:
                    squidSw = 0

        # Movimiento hacia atras
        elif move_dist > 0.001 and forward_comp > 0:
            squidSw = 0
            # Solo ajustar squid_R si no está rotando (la rotación tiene prioridad)
            if not is_rotating:
                if squid_R < 0:
                    squid_R += 4.0
            if squidSwBack == 0:
                squidT -= 6.0
                if squidT <= -10:
                    squidSwBack = 1
            else:
                squidT += 4.0
                if squidT >= 45:
                    squidSwBack = 0

        else:
            # Si no se movió, intentar devolver squidT hacia 0 lentamente
            if squidT > 0.5:
                squidT -= 1.0
            elif squidT < -0.5:
                squidT += 1.0
            else:
                squidT = 0.0
            
            # Si no está rotando ni moviéndose, devolver squid_R hacia 0 gradualmente
            if not is_rotating:
                if squid_R > 0.5:
                    squid_R -= 1.0
                elif squid_R < -0.5:
                    squid_R += 1.0
                else:
                    squid_R = 0.0

        # Guardar valores actualizados
        inst["squidT"] = squidT
        inst["squidSw"] = squidSw
        inst["squidSwBack"] = squidSwBack
        inst["squid_R"] = squid_R

def UpdateSquidTrails():
    """Actualiza los rastros de pintura de todos los calamares"""
    for i in range(NUM_SQUIDS):
        inst = squid_instances[i]
        trail = inst["paint_trail"]
        current_x = inst["x"]
        current_z = inst["z"]
        last_x = inst["last_trail_x"]
        last_z = inst["last_trail_z"]
        
        # Calcular distancia desde el último punto del rastro
        dx = current_x - last_x
        dz = current_z - last_z
        distance = math.sqrt(dx * dx + dz * dz)
        
        # Si el calamar se ha movido suficiente, agregar un nuevo punto al rastro
        if distance >= min_trail_distance:
            trail.append((current_x, inst["y"], current_z))
            inst["last_trail_x"] = current_x
            inst["last_trail_z"] = current_z
            
            # Limitar el tamaño del rastro para evitar problemas de rendimiento
            max_trail_points = 3500
            if len(trail) > max_trail_points:
                trail.pop(0)  # Eliminar el punto más antiguo

def UpdateMachineSmoothMovement():
    global machine_move_speed, machine_car_rotation_speed, machine_wheel_rotation_speed

    for i in range(NUM_MACHINES):
        inst = machine_instances[i]
        current_x = inst.get("x", 0.0)
        current_z = inst.get("z", 0.0)
        target_x = inst.get("target_x", current_x)
        target_z = inst.get("target_z", current_z)

        # Posición: mover suavemente hacia target
        dx = target_x - current_x
        dz = target_z - current_z
        distance = math.hypot(dx, dz)

        prev_x = current_x
        prev_z = current_z

        if distance > 0.001:
            # Normalizar dirección
            dir_x = dx / distance
            dir_z = dz / distance
            # Mover con velocidad constante (no sobrepasar el target)
            step = min(machine_move_speed, distance)
            current_x += dir_x * step
            current_z += dir_z * step
            inst["x"] = current_x
            inst["z"] = current_z
            inst["is_moving_forward"] = True
            inst["is_moving_backward"] = False
        else:
            # Ya en objetivo
            inst["x"] = target_x
            inst["z"] = target_z
            inst["is_moving_forward"] = False
            inst["is_moving_backward"] = False

        # Rotación del chasis: orientar hacia la dirección del movimiento (si se mueve)
        car_ang = inst.get("car_angle", 0.0)
        if distance > 0.001:
            # Ángulo objetivo hacia la dirección de movimiento
            # Nota: usamos atan2(-dir_x, -dir_z) para el mismo sistema que los calamares
            angle_rad = math.atan2(-dir_x, -dir_z)
            target_rot = math.degrees(angle_rad)
            if target_rot < 0:
                target_rot += 360
            # Diferencia con wrap-around
            rot_diff = ((target_rot - car_ang + 180) % 360) - 180
            # Girar gradualmente (grados por frame). machine_car_rotation_speed es un factor pequeño
            max_rot_step = max(1.0, machine_car_rotation_speed * 180.0)  # escala para hacerlo visible
            if abs(rot_diff) > 0.1:
                if rot_diff > 0:
                    car_ang = car_ang + min(max_rot_step, rot_diff)
                else:
                    car_ang = car_ang + max(-max_rot_step, rot_diff)
            else:
                car_ang = target_rot
        else:
            # Si no hay movimiento, el chasis puede alinear parcialmente con wheel_rotate
            # Mantener car_ang pero dejar espacio para que venga del backend
            car_ang = inst.get("car_angle", car_ang)

        # Si el backend propone wheel_rotate (dirección de ruedas), aplicar un pequeño efecto
        wh_rot = inst.get("wheel_rotate", 0.0)
        # Simular que el cuerpo se endereza ligeramente hacia el giro de las ruedas cuando hay movimiento
        if inst.get("is_moving_forward", False) or inst.get("is_moving_backward", False):
            # Aplicar fracción del wheel_rotate al cuerpo (no permanente)
            car_ang += -wh_rot * machine_car_rotation_speed * 50.0

        # Normalizar car_ang
        car_ang = car_ang % 360.0
        inst["car_angle"] = car_ang

        # Rotación visual de las ruedas (wheel_angle) según el movimiento hacia adelante/atrás
        moved_x = inst.get("x", 0.0) - prev_x
        moved_z = inst.get("z", 0.0) - prev_z
        moved_dist = math.hypot(moved_x, moved_z)

        wh_angle = inst.get("wheel_angle", 0.0)
        if moved_dist > 1e-4:
            # Detectar si el movimiento es hacia adelante o atrás respecto al chasis
            rad_rot = math.radians(inst.get("car_angle", 0.0))
            fdx = math.sin(rad_rot)
            fdz = math.cos(rad_rot)
            forward_comp = moved_x * fdx + moved_z * fdz
            if forward_comp < 0:
                # Avanza (forward vector has negative sign in this coordinate convention)
                wh_angle -= machine_wheel_rotation_speed
                inst["is_moving_forward"] = True
                inst["is_moving_backward"] = False
            else:
                # Retrocede
                wh_angle += machine_wheel_rotation_speed
                inst["is_moving_forward"] = False
                inst["is_moving_backward"] = True
        else:
            # No hay movimiento: frenar/decay del ángulo visual de las ruedas
            if wh_angle > 0.5:
                wh_angle -= machine_wheel_rotation_speed * 0.2
            elif wh_angle < -0.5:
                wh_angle += machine_wheel_rotation_speed * 0.2
            else:
                wh_angle = 0.0

        # Normalizar wheel visual angle
        if wh_angle <= -360.0:
            wh_angle += 360.0
        if wh_angle >= 360.0:
            wh_angle -= 360.0
        inst["wheel_angle"] = wh_angle

        # Mantener wheel_rotate y arm_angle propuestos por backend (si existen)
        inst["wheel_rotate"] = inst.get("wheel_rotate", 0.0)
        inst["arm_angle"] = inst.get("arm_angle", inst.get("arm_angle", -15.0))

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
        max_trail_points = 2500
        if len(paint_trail) > max_trail_points:
            paint_trail.pop(0)  # Eliminar el punto más antiguo
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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    if skybox:
        skybox.render(EYE_X, EYE_Y, EYE_Z)
        
    Axis()
    #Dibujo del plano gris
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, -2, -DimBoard)
    glVertex3d(-DimBoard, -2, DimBoard)
    glVertex3d(DimBoard, -2, DimBoard)
    glVertex3d(DimBoard, -2, -DimBoard)
    glEnd()

    #Dibujo de evironment
    glPushMatrix()
    glScale(1.2,1.2,1.2) #Este Scale ya no es necesario
    objetos[6].render()
    glPopMatrix()

    DrawPaintTrail()
    
    # Rastros de todos los calamares controlados por Julia (instancias 0, 1, 2, 3)
    # Colores diferentes para cada calamar
    squid_colors = [
        (1.0, 0.2, 0.8),  # Rosa (instancia 0)
        (0.2, 0.8, 1.0),  # Cyan (instancia 1)
        (1.0, 0.8, 0.2),  # Amarillo (instancia 2)
        (0.8, 0.2, 1.0),  # Púrpura (instancia 3)
    ]
    
    # Dibujar rastros de todas las instancias (incluyendo 0 cuando es controlada por Julia)
    # La instancia 0 también tiene su rastro independiente que se actualiza cuando es controlada por Julia
    for i in range(NUM_SQUIDS):
        if len(squid_instances[i]["paint_trail"]) > 0:
            DrawSquidTrail(squid_instances[i]["paint_trail"], squid_colors[i])
    
    if cached_data is not None:
        with data_lock:
            data = cached_data
            # Ahora controla las 4 instancias (0, 1, 2, 3) desde Julia
            # Actualiza las coordenadas OBJETIVO (target) para movimiento suave
            for i in range(min(4, len(data.get('pacmans', [])))):
                pacman = data['pacmans'][i]  # pacmans[0] → squid_instances[0]
                                            # pacmans[1] → squid_instances[1]
                                            # pacmans[2] → squid_instances[2]
                                            # pacmans[3] → squid_instances[3]
                matrix_size = 40
                board_size = DimBoard
                # Actualizar coordenadas objetivo (no las coordenadas actuales directamente)
                squid_instances[i]["target_x"] = (pacman['pos'][0] / matrix_size) * board_size * 2 - board_size
                squid_instances[i]["target_z"] = (pacman['pos'][1] / matrix_size) * board_size * 2 - board_size
                # Actualizar rotación si está disponible en los datos
                if 'rotation' in pacman:
                    squid_instances[i]["rotation"] = pacman['rotation']
                elif 'dir' in pacman:
                    # Calcular rotación desde dirección si está disponible
                    dir_val = pacman['dir']
                    if dir_val == 0:  # Arriba
                        squid_instances[i]["rotation"] = 0.0
                    elif dir_val == 1:  # Derecha
                        squid_instances[i]["rotation"] = 90.0
                    elif dir_val == 2:  # Abajo
                        squid_instances[i]["rotation"] = 180.0
                    elif dir_val == 3:  # Izquierda
                        squid_instances[i]["rotation"] = 270.0

            # Cada ghost del array actualiza una máquina diferente
            # Ahora controla las 4 instancias (0, 1, 2, 3) desde Julia
            # Actualiza las coordenadas OBJETIVO (target) para movimiento suave
            for i in range(min(4, len(data.get('ghosts', [])))):
                ghost = data['ghosts'][i]  # ghosts[0] → machine_instances[0]
                                        # ghosts[1] → machine_instances[1]
                                        # ghosts[2] → machine_instances[2]
                                        # ghosts[3] → machine_instances[3]
                matrix_size = 40
                board_size = DimBoard
                # Actualizar coordenadas objetivo (no las coordenadas actuales directamente)
                machine_instances[i]["target_x"] = (ghost['pos'][0] / matrix_size) * board_size * 2 - board_size
                machine_instances[i]["target_z"] = (ghost['pos'][1] / matrix_size) * board_size * 2 - board_size
                # Actualizar wheel_rotate si está disponible (controla la dirección de giro)
                if 'wheel_rotate' in ghost:
                    machine_instances[i]["wheel_rotate"] = ghost['wheel_rotate']
                # Animación automática del brazo cuando captura un pacman
                captured = ghost.get('captured_pacman', False)
                current_arm = machine_instances[i]["arm_angle"]
                
                if captured:
                    # Levantar brazo (como si presionara P)
                    if current_arm < 45.0:
                        machine_instances[i]["arm_angle"] = min(45.0, current_arm + 2.0)
                else:
                    # Bajar brazo (cuando suelta P)
                    if current_arm > -15.0:
                        machine_instances[i]["arm_angle"] = max(-15.0, current_arm - 2.0)
                
                # Actualizar arm_angle si viene explícitamente desde Julia (override)
                if 'arm_angle' in ghost:
                    machine_instances[i]["arm_angle"] = ghost['arm_angle']
                # Nota: car_angle y wheel_angle se actualizan automáticamente en UpdateMachineSmoothMovement()
                # basándose en el movimiento y wheel_rotate


    # Renderizar todos los calamares usando DrawSquidInstance (incluyendo instancia 0)
    # Ahora todas las instancias (0-3) pueden ser controladas por Julia
    for i in range(NUM_SQUIDS):
        DrawSquidInstance(squid_instances[i])
 
    for i in range(NUM_MACHINES):
        DrawMachineInstance(machine_instances[i])
    
    
done = False
Init()
# Actualizacion background
update_thread = threading.Thread(target=fetch_data_background, daemon=True)
update_thread.start()
try:
    res = requests.get("http://localhost:8000/run", timeout=2)
    cached_data = res.json()
except Exception as e:
    print(f"Error inicial: {e}")
# Inicializar el rastro con la posición inicial del calamar controlado por teclado
paint_trail.append((Player_X, Player_Y, Player_Z))
last_trail_x = Player_X
last_trail_z = Player_Z

# Inicializar los rastros de todas las instancias de calamares
for i in range(NUM_SQUIDS):
    inst = squid_instances[i]
    inst["paint_trail"].append((inst["x"], inst["y"], inst["z"]))
    inst["last_trail_x"] = inst["x"]
    inst["last_trail_z"] = inst["z"]

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

    # Calamares: control por Julia (targets). Animación por instancia se gestiona
    # desde UpdateSquidSmoothMovement, por lo que no se usan controles W/A/S/D manuales.
    
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
            arm_angle += 6.0  # Gradually increase
    else:  # When P is not pressed
        if arm_angle > -15.0:  # Minimum angle limit
            arm_angle -= 3.0  # Gradually decrease
    
    # Actualizar el rastro de pintura del calamar (solo para instancia 0 controlada por teclado)
    UpdatePaintTrail()
    
    keys_pressed = any([
        keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d],
        keys[pygame.K_k], keys[pygame.K_i], keys[pygame.K_j], keys[pygame.K_l], keys[pygame.K_p]
    ])
    
    if keys_pressed:
        # Si se presionan teclas, el control manual tiene prioridad para la instancia 0
        # Actualizar tanto las coordenadas actuales como las objetivo para movimiento inmediato
        squid_instances[0]["x"] = Player_X
        squid_instances[0]["y"] = Player_Y
        squid_instances[0]["z"] = Player_Z
        squid_instances[0]["target_x"] = Player_X
        squid_instances[0]["target_z"] = Player_Z
        squid_instances[0]["rotation"] = Player_Rotation
        # Sincronizar el rastro de la instancia 0 con el rastro del teclado
        squid_instances[0]["paint_trail"] = paint_trail.copy()
        squid_instances[0]["last_trail_x"] = last_trail_x
        squid_instances[0]["last_trail_z"] = last_trail_z

        machine_instances[0]["x"] = Maquina_X
        machine_instances[0]["y"] = Maquina_Y
        machine_instances[0]["z"] = Maquina_Z
        machine_instances[0]["target_x"] = Maquina_X
        machine_instances[0]["target_z"] = Maquina_Z
        machine_instances[0]["car_angle"] = car_angle
        machine_instances[0]["wheel_angle"] = wheel_angle
        machine_instances[0]["wheel_rotate"] = wheel_rotate
        machine_instances[0]["arm_angle"] = arm_angle
    
    # Actualizar movimiento suave de todos los calamares hacia sus coordenadas objetivo
    UpdateSquidSmoothMovement()
    UpdateSquidTrails()
    
    UpdateMachineSmoothMovement()
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()