#CALAMAR


def SquidFace():
    glPushMatrix()  
    glTranslatef(Player_X, Player_Y , Player_Z)
    glRotatef(Player_Rotation + Squid_R, 0, 1, 0)  # Rotar el calamar según su orientación
    glScale(Squid_Scale,Squid_Scale,Squid_Scale)
    objetos[0].render()  
    glPopMatrix()
    
def SquidDer():
    glPushMatrix()
    glTranslatef(Player_X, Player_Y , Player_Z)
    glRotatef(Player_Rotation -SquidT, 0, 1, 0)  # Rotar el calamar según su orientación y Rota en Y para simular el movimiento de nado de lado a lado
    glScale(Squid_Scale,Squid_Scale,Squid_Scale)
    objetos[1].render()
    glPopMatrix()
    
def SquidIzq():
    glPushMatrix()
    glTranslatef(Player_X, Player_Y , Player_Z)
    glRotatef(Player_Rotation + SquidT, 0, 1, 0)  # Rotar el calamar según su orientación rotar en el sentido contrario para simular el movimiento de nado
    glScale(Squid_Scale,Squid_Scale,Squid_Scale)
    objetos[2].render()
    glPopMatrix()
    
##############################################################################

#Maquina

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