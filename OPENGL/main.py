import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
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
#Manejo de peticiones
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
zero = 0.0
one = 1.0

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
    #m1 = zero
    m2 = -sin_theta * Squid_Scale
    #m3 = zero
    
    # Elementos de la columna 1
    #m4 = zero
    m5 = Squid_Scale
    #m6 = zero
    #m7 = zero
    
    # Elementos de la columna 2
    m8 = sin_theta * Squid_Scale
    #m9 = zero
    m10 = cos_theta * Squid_Scale
    #m11 = zero
    
    # Elementos de la columna 3 (Traslación)
    m12 = Player_X
    m13 = Player_Y
    m14 = Player_Z
    #m15 = one

    # La lista final almacena referencias a los valores
    squid_matrix = [
        m0, zero, m2, zero,  # Columna 0
        zero, m5, zero, zero,  # Columna 1
        m8, zero, m10, zero, # Columna 2
        m12, m13, m14, one # Columna 3
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
        m0, zero, m2, zero,  # Columna 0
        zero, m5, zero, zero,  # Columna 1
        m8, zero, m10, zero, # Columna 2
        m12, m13, m14, one  # Columna 3
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
        m0, zero, m2, zero,  # Columna 0
        zero, m5, zero, zero,  # Columna 1
        m8, zero, m10, zero, # Columna 2
        m12, m13, m14, one  # Columna 3
    ]
    glMultMatrixf(squid_matrix)
    objetos[2].render()
    glPopMatrix()
     
        
# Dibuja la maquina Wheel Loader
def Maquina():
    glPushMatrix()
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    glScale(Maquina_Scale,Maquina_Scale,Maquina_Scale)
    objetos[3].render()
    glPopMatrix()
    
def MaquinaArm():
    glPushMatrix()
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 20.0 , -10.0) #ajuste de offset
    glRotatef(arm_angle, 1.0, 0.0, 0.0)  #Elevacion del brazo
    glScale(Maquina_Scale,Maquina_Scale,Maquina_Scale)
    objetos[4].render()
    glPopMatrix()
    
def MaquinaFW():
    glPushMatrix()
    glTranslatef(Maquina_X, Maquina_Y, Maquina_Z)
    glRotatef(car_angle, 0.0, 1.0, 0.0)
    glTranslatef(0.0, 10.0 , -19.0) #ajuste de offset
    glRotatef(wheel_rotate, 0.0, 1.0, 0.0)  #Vuelta de las ruedas delanteras
    glRotatef(wheel_angle, 1.0, 0.0, 0.0) #giro de las ruedas
    glScale(Maquina_Scale,Maquina_Scale,Maquina_Scale)
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
    glScale(Maquina_Scale,Maquina_Scale,Maquina_Scale)
    objetos[5].render()
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
        
        time.sleep(0.05)  # Pequeña pausa

def display():
    global Player_X, Player_Z, cached_data
    
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

    # Usar los datos cacheados (NO bloquea)
    if cached_data is not None:
        with data_lock:
            data = cached_data
        
        pacman = next((p for p in data['pacmans'] if p['id'] == 4), None)
        
        if pacman:
            matrix_size = 200
            board_size = DimBoard
            
            Player_X = (pacman['pos'][0] / matrix_size) * board_size * 2 - board_size
            Player_Z = (pacman['pos'][1] / matrix_size) * board_size * 2 - board_size
    
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

# Iniciar thread de actualización en background
update_thread = threading.Thread(target=fetch_data_background, daemon=True)
update_thread.start()

# Obtener datos iniciales
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
    
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()