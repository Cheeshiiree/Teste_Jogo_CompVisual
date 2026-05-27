import pygame
from pygame.locals import * # type: ignore
from OpenGL.GL import * # type: ignore
from OpenGL.GLU import * # type: ignore
# from pygame.locals import DOUBLEBUF, OPENGL, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, QUIT
# from OpenGL.GL import (
#     GL_TRIANGLES, glBegin, glColor3fv, glScalef, glVertex3fv, glEnd,
#     glEnable, GL_DEPTH_TEST, glTranslatef,
#     glRotatef, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
#     glPushMatrix, glPopMatrix, GL_QUADS
# )
# from OpenGL.GLU import gluPerspective
import numpy as np
import sys
import math

# 1. Definições Geométricas do Cubo 3D
vertices_cubo = (
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, -1, 1),  (1, 1, 1),  (-1, -1, 1),  (-1, 1, 1)
)
faces_cubo = (
    (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
    (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
)
cores_faces = (
    (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)
)

# 2. Definições do Item Coletável (Uma pequena pirâmide amarela)
vertices_item = (
    (0, 0, 0.4),      # Topo da pirâmide (apontando para fora da face)
    (0.2, -0.2, 0),   # Base inferior direita
    (0.2, 0.2, 0),    # Base superior direita
    (-0.2, 0.2, 0),   # Base superior esquerda
    (-0.2, -0.2, 0)   # Base inferior esquerda
)
faces_item = (
    (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1), (1, 4, 3, 2)
)

pygame.font.init()  # Inicializa o sistema de fontes do Pygame para exibir texto na tela
fonte_coletado = pygame.font.SysFont("Arial", 24)

def DesenharCubo():
    glBegin(GL_QUADS)
    for i, face in enumerate(faces_cubo):
        glColor3fv(cores_faces[i])
        for vertice in face:
            glVertex3fv(vertices_cubo[vertice])
    glEnd()

def DesenharItem(coletado, escala_item):
    """Desenha o item. Se for coletado, ele muda de cor (fica verde) e usa a escala aumentada."""
    glPushMatrix()
    # Posiciona o item exatamente no centro da face de trás (Z = -1)
    # E rotaciona 180 graus para ele ficar virado para fora
    glTranslatef(0.0, 0.0, -1.0)
    glRotatef(180, 0, 1, 0)
    
    # Aplica o efeito visual de escala ao coletar
    glScalef(escala_item, escala_item, escala_item)
    
    glBegin(GL_TRIANGLES)
    for face in faces_item[:4]:
        if coletado:
            glColor3fv((0, 1, 0)) # Fica Verde se coletado
        else:
            glColor3fv((1, 0.8, 0)) # Amarelo Ouro original
        for vertice in face:
            glVertex3fv(vertices_item[vertice])
    glEnd()
    glPopMatrix()

def CalcularPosicaoTela(rot_x, rot_y, largura, altura):
    """Calcula matematicamente onde o item 3D está projetado na sua tela 2D (X, Y)"""
    # Posição inicial do item no espaço do cubo
    x, y, z = 0.0, 0.0, -1.0
    
    # Aplica as rotações baseadas nos ângulos do cubo (Matriz de Rotação Espacial)
    rad_x = math.radians(rot_x)
    rad_y = math.radians(rot_y)
    
    # Rotação no eixo Y
    x_rot = x * math.cos(rad_y) + z * math.sin(rad_y)
    z_rot = -x * math.sin(rad_y) + z * math.cos(rad_y)
    
    # Rotação no eixo X
    y_final = y * math.cos(rad_x) - z_rot * math.sin(rad_x)
    z_final = y * math.sin(rad_x) + z_rot * math.cos(rad_x)
    x_final = x_rot
    
    # Translação da câmera (afastamos -6.0 em Z no gluPerspective)
    z_final -= 6.0
    
    # Projeção Perspectiva Simples para coordenadas da tela
    fov_fator = 1.0 / math.tan(math.radians(45) / 2.0)
    proj_x = (x_final * fov_fator) / -z_final
    proj_y = (y_final * fov_fator) / -z_final
    
    # Ajusta o aspecto ratio da tela
    aspect = largura / altura
    proj_x /= aspect
    
    # Converte de coordenadas normalizadas (-1 a 1) para pixels da janela (0 a Largura/Altura)
    tela_x = int((proj_x + 1.0) * largura / 2.0)
    tela_y = int((1.0 - proj_y) * altura / 2.0) # Inverte o eixo Y para o padrão Pygame
    
    return tela_x, tela_y, z_final

# 3. Inicialização Principal
pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Greyboxing 5 - Coletar Item na Face do Cubo")
relogio = pygame.time.Clock()

gluPerspective(45, (LARGURA / ALTURA), 0.1, 50.0)
glTranslatef(0.0, 0.0, -6.0)
glEnable(GL_DEPTH_TEST)

# Variáveis de Estado da Mecânica
rotacao_x,rotacao_y = 0, 0
rotacao_y = 0
clicando_arrastando = False
ultima_pos_mouse = (0, 0)

item_coletado = False
escala_item = 1.0

while True:
    pos_mouse_atual = pygame.mouse.get_pos()
    
    # Calcula a posição 2D do item para checar a colisão do clique
    item_tela_x, item_tela_y, item_profundidade = CalcularPosicaoTela(rotacao_x, rotacao_y, LARGURA, ALTURA)
    item_tela_x, item_tela_y, item_z_mundo = CalcularPosicaoTela(rotacao_x, rotacao_y, LARGURA, ALTURA)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1: # Clique Esquerdo
                # 1. Verifica se foi um CLIQUE SIMPLES no item
                # Calcula a distância em pixels entre o clique do mouse e o item projetado
                distancia = math.hypot(pos_mouse_atual[0] - item_tela_x, pos_mouse_atual[1] - item_tela_y)
                
                # Se a distância for menor que 40 pixels e o item estiver virado para a frente (Z do mundo mais próximo)
                if distancia < 40 and item_z_mundo > -6.0:
                    item_coletado = True
                    print("Item Coletado com sucesso!")
                    
                    # texto = fonte.render("Item Coletado!", True, (255, 255, 255))
                    # tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 20))
                else:
                    # Se não clicou no item, ativa o modo de arrastar para girar o cubo
                    clicando_arrastando = True
                    ultima_pos_mouse = pos_mouse_atual

        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                clicando_arrastando = False

        if evento.type == MOUSEMOTION and clicando_arrastando:
            dx = pos_mouse_atual[0] - ultima_pos_mouse[0]
            dy = pos_mouse_atual[1] - ultima_pos_mouse[1]
            rotacao_y += dx * 0.5
            rotacao_x += dy * 0.5
            ultima_pos_mouse = pos_mouse_atual

    # Animação suave de aumento de tamanho ao coletar
    if item_coletado and escala_item < 2.5:
        escala_item += 0.1  # Faz o item crescer gradativamente até 2.5x        

    # 4. Renderização
    glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))

    glPushMatrix()
    glRotatef(rotacao_x, 1, 0, 0)
    glRotatef(rotacao_y, 0, 1, 0)

    # Desenha os dois objetos grudados utilizando o mesmo sistema de coordenadas
    DesenharCubo()
    DesenharItem(item_coletado, escala_item)

    glPopMatrix()

    # 5. Exibição de Texto na Tela (Feedback Visual)
    if item_coletado:
        texto_surface = fonte_coletado.render("Item Coletado!", True, (255, 255, 255))
        
        # 1. ATIVA O BLENDING (O segredo para a transparência funcionar)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Define a posição do texto na tela
        glWindowPos2d(LARGURA // 2 - texto_surface.get_width() // 2, ALTURA - 50)
        
        # Transforma a imagem do texto para string de pixels em formato RGBA
        dados_texto = pygame.image.tostring(texto_surface, "RGBA", True)
        
        # Desenha os pixels na tela
        glDrawPixels(texto_surface.get_width(), texto_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, dados_texto)
        
        # 2. DESATIVA O BLENDING (Sempre desative para não bagunçar o desenho do cubo 3D no próximo frame)
        glDisable(GL_BLEND)

    pygame.display.flip()
    relogio.tick(60)