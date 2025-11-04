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