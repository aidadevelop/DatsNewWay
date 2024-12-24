import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

class SnakeVisualizer:
    def __init__(self, width=1024, height=768):
        pygame.init()
        pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Snake Game")
        
        # Настройка OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Настройка света
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 10, 10, 1))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))
        
        gluPerspective(45, (width/height), 0.1, 150.0)
        glTranslatef(0.0, -10.0, -50)
        
        self.camera_rot_x = 30
        self.camera_rot_y = 45
        self.camera_distance = 50
        self.our_snake_ids = []
        
        # Создаем сферу для отрисовки
        self.sphere = gluNewQuadric()
        
    def set_our_snake_ids(self, snake_ids):
        """Устанавливает ID наших змеек"""
        self.our_snake_ids = snake_ids
        
    def handle_camera_movement(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.camera_rot_y += 2
        if keys[pygame.K_RIGHT]:
            self.camera_rot_y -= 2
        if keys[pygame.K_UP]:
            self.camera_rot_x += 2
        if keys[pygame.K_DOWN]:
            self.camera_rot_x -= 2
            
        if keys[pygame.K_w]:
            self.camera_distance -= 1.0
        if keys[pygame.K_s]:
            self.camera_distance += 1.0
            
        self.camera_distance = max(20, min(100, self.camera_distance))
        
    def draw_sphere(self, position, radius, color):
        glPushMatrix()
        glTranslatef(*position)
        glColor3f(*color)
        gluSphere(self.sphere, radius, 16, 16)
        glPopMatrix()
        
    def draw_snake(self, geometry, color):
        if not geometry:
            return
            
        # Рисуем сегменты тела
        for i in range(len(geometry)-1):
            start = geometry[i]
            end = geometry[i+1]
            
            # Рисуем сферу в каждой точке сегмента
            self.draw_sphere(start, 0.4, color)
            
            # Рисуем линию между сферами
            glColor3f(*color)
            glLineWidth(3.0)
            glBegin(GL_LINES)
            glVertex3f(*start)
            glVertex3f(*end)
            glEnd()
            
        # Рисуем последнюю сферу
        if geometry:
            self.draw_sphere(geometry[-1], 0.4, color)
            
        # Рисуем голову змейки большей сферой
        if geometry:
            head_color = (0.8, 1.0, 0.8) if color == (0.0, 1.0, 0.0) else (1.0, 0.8, 0.8)
            self.draw_sphere(geometry[0], 0.6, head_color)
        
    def render(self, game_state):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Настройка камеры
        glTranslatef(0, -10, -self.camera_distance)
        glRotatef(self.camera_rot_x, 1, 0, 0)
        glRotatef(self.camera_rot_y, 0, 1, 0)
        
        # Рисуем змеек
        for snake in game_state.get('snakes', []):
            if snake['status'] == 'alive':
                # Зеленый цвет для наших змеек, красный для чужих
                color = (0.0, 1.0, 0.0) if snake['id'] in self.our_snake_ids else (1.0, 0.0, 0.0)
                self.draw_snake(snake['geometry'], color)
        
        # Рисуем еду
        for food in game_state.get('food', []):
            position = food.get('position', food.get('c', [0, 0, 0]))
            if food.get('golden', False):
                # Золотая мандаринка - желтый цвет
                self.draw_sphere(position, 0.5, (1.0, 1.0, 0.0))
            else:
                # Обычная мандаринка - оранжевый цвет
                self.draw_sphere(position, 0.3, (1.0, 0.5, 0.0))
        
        # Рисуем препятствия (если они есть)
        for obstacle in game_state.get('obstacles', []):
            position = obstacle.get('position', [0, 0, 0])
            # Препятствия - серый цвет
            self.draw_sphere(position, 0.4, (0.5, 0.5, 0.5))
            
        pygame.display.flip()
        
    def process_events(self, game_state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
        self.handle_camera_movement()
        return True
