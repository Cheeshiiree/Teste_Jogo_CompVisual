import pygame
import cv2
import numpy as np

# Inicialização padrão do Pygame
pygame.init()
tela = pygame.display.set_mode((800, 600))

# ... dentro do seu loop principal do jogo ...
# 1. Desenhe seu personagem e blocos de teste normalmente
# tela.blit(sprite_player, (pos_x, pos_y)) 
# Personagem generico gerado com geometria simples para teste
pygame.draw.rect(tela, (255, 0, 0), (100, 100, 50, 50))  # Desenha um quadrado vermelho como personagem
pygame.draw.rect(tela, (0, 255, 0), (200, 200, 50, 50))  # Desenha um quadrado verde como bloco de teste
pygame.display.flip()  # Atualiza a tela para mostrar as mudanças

# 2. CAPTURA: Transforma a tela do jogo em uma matriz NumPy (RGB)
view = pygame.surfarray.array3d(tela)
# O Pygame usa eixos invertidos (X, Y), precisamos transpor para o padrão de imagem (Y, X)
matriz_imagem = np.transpose(view, (1, 0, 2))

# 3. TESTE OPENCV: Converter para tons de cinza só para testar a integração
imagem_cinza = cv2.cvtColor(matriz_imagem, cv2.COLOR_RGB2GRAY)