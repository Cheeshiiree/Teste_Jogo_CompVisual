import pygame
from pygame.locals import DOUBLEBUF, OPENGL, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, QUIT
from OpenGL.GL import (
    glBegin, glColor3fv, glVertex3fv, glEnd,
    glEnable, GL_DEPTH_TEST, glTranslatef,
    glRotatef, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    glPushMatrix, glPopMatrix, GL_QUADS
)
from OpenGL.GLU import gluPerspective
import sys

# 1. Definição das coordenadas dos vértices e das faces de um Cubo 3D
vertices = (
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, -1, 1),  (1, 1, 1),  (-1, -1, 1),  (-1, 1, 1)
)

faces = (
    (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
    (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
)

# Cores para cada face do cubo para conseguirmos ver a rotação nitidamente
cores_faces = (
    (1, 0, 0),   # Vermelho
    (0, 1, 0),   # Verde
    (0, 0, 1),   # Azul
    (1, 1, 0),   # Amarelo
    (1, 0, 1),   # Magenta
    (0, 1, 1)    # Ciano
)

def DesenharCubo():
    """Função que renderiza as faces coloridas do cubo usando OpenGL"""
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glColor3fv(cores_faces[i])
        for vertice in face:
            glVertex3fv(vertices[vertice])
    glEnd()

# 2. Inicialização do Pygame e Contexto PyOpenGL
pygame.init()
LARGURA, ALTURA = 800, 600
# Ativamos os buffers de exibição dupla (DOUBLEBUF) e o motor OpenGL
tela = pygame.display.set_mode((LARGURA, ALTURA), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Greyboxing 4 - Inspeção de Objeto 3D com Mouse")
relogio = pygame.time.Clock()

# Configuração da Câmera Virtual (Projeção Perspectiva)
# Campo de visão: 45°, Aspect Ratio, Distância Mínima: 0.1, Distância Máxima: 50.0
gluPerspective(45, (LARGURA / ALTURA), 0.1, 50.0)
# Afasta a câmera em Z para conseguirmos enxergar o cubo no centro (0,0,0)
glTranslatef(0.0, 0.0, -6.0)

# Habilita o teste de profundidade (evita que faces de trás apareçam na frente)
glEnable(GL_DEPTH_TEST)

# Variáveis para controle de rotação com o mouse
rotacao_x, rotacao_y = 0, 0
clicando = False
ultima_pos_mouse = (0, 0)

# Loop principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Detecta quando o botão do mouse é pressionado
        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:  # Botão esquerdo
                clicando = True
                ultima_pos_mouse = pygame.mouse.get_pos()

        # Detecta quando o botão do mouse é solto
        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                clicando = False

        # Verifica o arrasto do mouse para calcular a rotação
        if evento.type == MOUSEMOTION and clicando:
            mouse_atual = pygame.mouse.get_pos()
            # Calcula a variação de movimento do mouse (Delta X e Delta Y)
            dx = mouse_atual[0] - ultima_pos_mouse[0]
            dy = mouse_atual[1] - ultima_pos_mouse[1]

            # Atualiza os ângulos de rotação baseado no arrasto
            rotacao_y += dx * 0.5  # Movimento horizontal gira no eixo Y
            rotacao_x += dy * 0.5  # Movimento vertical gira no eixo X

            ultima_pos_mouse = mouse_atual

    # 3. RENDERIZAÇÃO DO ESPAÇO 3D
    # Limpa os buffers de cor e de profundidade para desenhar o frame limpo
    glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))

    # Salvamos a matriz atual antes de aplicar as transformações geométricas do frame
    glPushMatrix()
    
    # Aplica as transformações geométricas baseadas no mouse (Diretriz Obrigatória!)
    glRotatef(rotacao_x, 1, 0, 0) # Rotação no eixo X
    glRotatef(rotacao_y, 0, 1, 0) # Rotação no eixo Y

    # Desenha o objeto geométrico
    DesenharCubo()

    # Restaura a matriz para o próximo loop
    glPopMatrix()

    # Atualiza a tela (Troca de buffers) e limita a taxa de atualização
    pygame.display.flip()
    relogio.tick(60)