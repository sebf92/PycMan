# https://blubberquark.tumblr.com/post/185013752945/using-moderngl-for-post-processing-shaders-with

import pygame
from pygame.locals import *
import struct

import moderngl
import glcontext # import necessaire pour pyinstaller


class CRTShader:
    pygame.init()
    WIDTH = 800
    HEIGHT = 600

    VIRTUAL_RES=(int(WIDTH/2), int(HEIGHT/2))
    REAL_RES=(WIDTH, HEIGHT)

    def __init__(self, infullscreen = False, enableeffect = True):
        if(enableeffect):
            CRTShader.VIRTUAL_RES=(int(CRTShader.WIDTH/2), int(CRTShader.HEIGHT/2))
        else:
            CRTShader.VIRTUAL_RES=(int(CRTShader.WIDTH), int(CRTShader.HEIGHT))

        self.memoryscreen = pygame.Surface(CRTShader.REAL_RES).convert((255, 255<<8, 255<<16, 0))
        self.screen = pygame.Surface(CRTShader.VIRTUAL_RES).convert((255, 255<<8, 255<<16, 0))
        if(infullscreen):
            pygame.display.set_mode(CRTShader.REAL_RES, DOUBLEBUF|OPENGL|FULLSCREEN) #, vsync=1
        else:
            pygame.display.set_mode(CRTShader.REAL_RES, DOUBLEBUF|OPENGL)

        self.ctx = moderngl.create_context()

        self.texture_coordinates = [0, 1,  1, 1,
                            0, 0,  1, 0]

        self.world_coordinates = [-1, -1,  1, -1,
                            -1,  1,  1,  1]

        self.render_indices = [0, 1, 2,
                        1, 2, 3]

        if(enableeffect):
            self.prog = self.ctx.program(
                vertex_shader='''
            #version 300 es
            in vec2 vert;
            in vec2 in_text;
            out vec2 v_text;
            void main() {
            gl_Position = vec4(vert, 0.0, 1.0);
            v_text = in_text;
            }
            ''',

                fragment_shader='''
            #version 300 es
            precision mediump float;
            uniform sampler2D Texture;

            out vec4 color;
            in vec2 v_text;
            void main() {
            vec2 center = vec2(0.5, 0.5);
            vec2 off_center = v_text - center;

            off_center *= 1.0 + 0.8 * pow(abs(off_center.yx), vec2(3.5));

            vec2 v_text2 = center+off_center;

            if (v_text2.x > 1.0 || v_text2.x < 0.0 ||
                v_text2.y > 1.0 || v_text2.y < 0.0){
                color=vec4(0.0, 0.0, 0.0, 1.0);
            } else {
                color = vec4(texture(Texture, v_text2).rgb, 1.0);
                float fv = fract(0.75 * v_text2.y * float(textureSize(Texture,0).y));
                fv=min(1.0, 0.8+0.5*min(fv, 1.0-fv));
                color.rgb*=fv;
            }
            }
            ''')
        else:
            self.prog = self.ctx.program(
                vertex_shader='''
            #version 300 es
            in vec2 vert;
            in vec2 in_text;
            out vec2 v_text;
            void main() {
            gl_Position = vec4(vert, 0.0, 1.0);
            v_text = in_text;
            }
            ''',

                fragment_shader='''
            #version 300 es
            precision mediump float;
            uniform sampler2D Texture;
            in vec2 v_text;

            out vec3 f_color;
            void main() {
            f_color = texture(Texture,v_text).rgb;
            }
            ''')

        self.screen_texture = self.ctx.texture(
            CRTShader.VIRTUAL_RES, 3,
            pygame.image.tostring(self.screen, "RGB", 1))

        self.screen_texture.repeat_x = False
        self.screen_texture.repeat_y = False

        self.vbo = self.ctx.buffer(struct.pack('8f', *self.world_coordinates))
        self.uvmap = self.ctx.buffer(struct.pack('8f', *self.texture_coordinates))
        self.ibo= self.ctx.buffer(struct.pack('6I', *self.render_indices))

        self.vao_content = [
            (self.vbo, '2f', 'vert'),
            (self.uvmap, '2f', 'in_text')
        ]

        self.vao = self.ctx.vertex_array(self.prog, self.vao_content, self.ibo)

    def getScreen(self):
        return self.memoryscreen

    def render(self):
        # on retaille l'image pour la mettre à la taille de l'écran virtuel
        virtualimage = pygame.transform.smoothscale(self.memoryscreen, CRTShader.VIRTUAL_RES)
        texture_data = virtualimage.get_view('1')
        # on la map sur l'ecran
        self.screen_texture.write(texture_data)
        self.ctx.clear(14/255,40/255,66/255)
        self.screen_texture.use()
        self.vao.render()
        # on met a jour l'affichage
        pygame.display.flip()

