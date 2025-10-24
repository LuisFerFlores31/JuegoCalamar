import os
import pygame
from OpenGL.GL import *


class OBJ:
    generate_on_init = True

    @classmethod
    def loadTexture(cls, imagefile):
        surf = pygame.image.load(imagefile)
        image = pygame.image.tostring(surf, 'RGBA', 1)
        ix, iy = surf.get_rect().size
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        return texid

    @classmethod
    def loadMaterial(cls, filename):
        contents = {}
        mtl = None
        dirname = os.path.dirname(filename)

        for line in open(filename, "r"):
            if line.startswith('#'):
                continue
            values = line.strip().split()
            if not values:
                continue

            if values[0] == 'newmtl':
                mtl = contents[values[1]] = {}
            elif mtl is None:
                raise ValueError("El archivo MTL no empieza con 'newmtl'")
            elif values[0] == 'Kd':
                mtl['Kd'] = list(map(float, values[1:4]))
            elif values[0] == 'map_Kd':
                texture_file = os.path.join(dirname, values[1])
                if os.path.exists(texture_file):
                    mtl['map_Kd'] = values[1]
                    mtl['texture_Kd'] = cls.loadTexture(texture_file)
                else:
                    print("⚠️ Textura no encontrada:", texture_file)
            else:
                # guarda otros valores pero sin intentar convertir todo
                try:
                    mtl[values[0]] = list(map(float, values[1:]))
                except ValueError:
                    mtl[values[0]] = values[1:]

        return contents

    def __init__(self, filename, swapyz=False):
        """Carga un archivo Wavefront OBJ."""
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
        self.gl_list = 0
        dirname = os.path.dirname(filename)

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = (v[0], v[2], v[1])
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = (v[0], v[2], v[1])
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(list(map(float, values[1:3])))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = self.loadMaterial(os.path.join(dirname, values[1]))
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    texcoords.append(int(w[1]) if len(w) >= 2 and w[1] else 0)
                    norms.append(int(w[2]) if len(w) >= 3 and w[2] else 0)
                self.faces.append((face, norms, texcoords, material))

        if self.generate_on_init:
            self.generate()

    def generate(self):
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glEnable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)

        for face in self.faces:
            vertices, normals, texture_coords, material = face
            mtl = self.mtl.get(material, {})

            # Aplica textura o color base
            if 'texture_Kd' in mtl:
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
                glColor3f(1.0, 1.0, 1.0)
            elif 'Kd' in mtl:
                glColor3fv(mtl['Kd'])
                glBindTexture(GL_TEXTURE_2D, 0)
            else:
                glColor3f(0.8, 0.8, 0.8)
                glBindTexture(GL_TEXTURE_2D, 0)

            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0 and texture_coords[i] <= len(self.texcoords):
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()

        glDisable(GL_TEXTURE_2D)
        glEndList()

    def render(self):
        glCallList(self.gl_list)

    def free(self):
        glDeleteLists([self.gl_list])
