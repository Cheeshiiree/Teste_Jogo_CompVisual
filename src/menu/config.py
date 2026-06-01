# Configurações do Menu
import pygame
import sys
import ctypes
import os

# Configurações para centralizar a janela do jogo na tela
os.environ['SDL_VIDEO_CENTERED'] = '1'
ctypes.windll.user32.SetProcessDPIAware() # Para evitar que o Windows aplique escalonamento automático em telas de alta resolução

# Configurações Iniciais do Pygame
pygame.init()
pygame.font.init()

LARGURA, ALTURA = 1280, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))