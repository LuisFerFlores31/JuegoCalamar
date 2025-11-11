from OpenGL.GL import *
from OpenGL.GLU import *
import os


class Skybox:
    def __init__(self, textures_path):
        """
        Inicializa el Skybox.
        textures_path: ruta a la carpeta que contiene las imágenes del cubemap
        Espera: px.png, nx.png, py.png, ny.png, pz.png, nz.png
        """
        self.texture_ids = {}
        self.gl_list = 0
        self.load_textures(textures_path)
        self.generate()

    def load_textures(self, path):
        """Carga las 6 texturas del cubemap."""
        import pygame
        
        faces = {
            'px': GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            'nx': GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            'py': GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            'ny': GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            'pz': GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            'nz': GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        }

        # Generar textura cubemap
        self.cubemap_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubemap_id)

        # Parámetros de textura
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        # Cargar cada cara del cubemap
        for name, target in faces.items():
            filename = os.path.join(path, f"{name}.png")
            if os.path.exists(filename):
                surf = pygame.image.load(filename)
                image = pygame.image.tostring(surf, 'RGBA', 1)
                ix, iy = surf.get_rect().size
                glTexImage2D(target, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
            else:
                print(f"⚠️ Textura no encontrada: {filename}")

        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)

    def generate(self):
        """Genera la lista de display para el skybox."""
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        size = 500.0  # Tamaño del skybox

        glEnable(GL_TEXTURE_CUBE_MAP)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubemap_id)

        glBegin(GL_QUADS)

        # Face positiva X
        glTexCoord3f(1.0, -1.0, -1.0)
        glVertex3f(size, -size, -size)
        glTexCoord3f(1.0, -1.0, 1.0)
        glVertex3f(size, -size, size)
        glTexCoord3f(1.0, 1.0, 1.0)
        glVertex3f(size, size, size)
        glTexCoord3f(1.0, 1.0, -1.0)
        glVertex3f(size, size, -size)

        # Face negativa X
        glTexCoord3f(-1.0, -1.0, 1.0)
        glVertex3f(-size, -size, size)
        glTexCoord3f(-1.0, -1.0, -1.0)
        glVertex3f(-size, -size, -size)
        glTexCoord3f(-1.0, 1.0, -1.0)
        glVertex3f(-size, size, -size)
        glTexCoord3f(-1.0, 1.0, 1.0)
        glVertex3f(-size, size, size)

        # Face positiva Y
        glTexCoord3f(-1.0, 1.0, 1.0)
        glVertex3f(-size, size, size)
        glTexCoord3f(1.0, 1.0, 1.0)
        glVertex3f(size, size, size)
        glTexCoord3f(1.0, 1.0, -1.0)
        glVertex3f(size, size, -size)
        glTexCoord3f(-1.0, 1.0, -1.0)
        glVertex3f(-size, size, -size)

        # Face negativa Y
        glTexCoord3f(-1.0, -1.0, -1.0)
        glVertex3f(-size, -size, -size)
        glTexCoord3f(1.0, -1.0, -1.0)
        glVertex3f(size, -size, -size)
        glTexCoord3f(1.0, -1.0, 1.0)
        glVertex3f(size, -size, size)
        glTexCoord3f(-1.0, -1.0, 1.0)
        glVertex3f(-size, -size, size)

        # Face positiva Z
        glTexCoord3f(-1.0, -1.0, 1.0)
        glVertex3f(-size, -size, size)
        glTexCoord3f(1.0, -1.0, 1.0)
        glVertex3f(size, -size, size)
        glTexCoord3f(1.0, 1.0, 1.0)
        glVertex3f(size, size, size)
        glTexCoord3f(-1.0, 1.0, 1.0)
        glVertex3f(-size, size, size)

        # Face negativa Z
        glTexCoord3f(1.0, -1.0, -1.0)
        glVertex3f(size, -size, -size)
        glTexCoord3f(-1.0, -1.0, -1.0)
        glVertex3f(-size, -size, -size)
        glTexCoord3f(-1.0, 1.0, -1.0)
        glVertex3f(-size, size, -size)
        glTexCoord3f(1.0, 1.0, -1.0)
        glVertex3f(size, size, -size)

        glEnd()
        glDisable(GL_TEXTURE_CUBE_MAP)
        glEndList()

    def render(self, camera_x, camera_y, camera_z):
        """Renderiza el skybox centrado en la posición de la cámara."""
        glPushMatrix()
        glTranslatef(camera_x, camera_y, camera_z)
        glCallList(self.gl_list)
        glPopMatrix()

    def free(self):
        """Libera los recursos del skybox."""
        glDeleteLists([self.gl_list])
        glDeleteTextures([self.cubemap_id])
