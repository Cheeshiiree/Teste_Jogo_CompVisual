import pygame
import numpy as np
import cv2
import sys

# 1. Inicialização do Pygame
pygame.init()
pygame.font.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 7 - Laboratório de Filtros OpenCV")
relogio = pygame.time.Clock()

FONTE_HUD = pygame.font.SysFont("Arial", 16, bold=True)

# Cores do Cenário de Teste
COR_FUNDO = (20, 20, 20)
COR_BLOCO_OCULTO = (23, 23, 23)   # Quase idêntico ao fundo (Desafio de Contraste!)

# Estados dos Filtros (0: Normal, 1: Cinza, 2: Bordas/Sobel, 3: Contraste/Threshold)
FILTRO_ATUAL = 0 

# 2. Definição dos Botões da Interface (HUD)
# Criamos uma lista de dicionários para gerenciar os botões dinamicamente
botoes = [
    {"id": 0, "texto": "Normal", "rect": pygame.Rect(20, 20, 110, 40)},
    {"id": 1, "texto": "1. Cinza", "rect": pygame.Rect(140, 20, 110, 40)},
    {"id": 2, "texto": "2. Sobel", "rect": pygame.Rect(260, 20, 110, 40)},
    {"id": 3, "texto": "3. Contraste", "rect": pygame.Rect(380, 20, 110, 40)}
]

while True:
    pos_mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: # Clique esquerdo
                # Checa se o clique aconteceu dentro de algum botão
                for btn in botoes:
                    if btn["rect"].collidepoint(pos_mouse):
                        FILTRO_ATUAL = btn["id"]
                        print(f"Filtro alterado para o ID: {FILTRO_ATUAL}")

    # 3. RENDERIZAÇÃO DA CENA ORIGINAL (Pre-processamento)
    tela.fill(COR_FUNDO)
    
    # ELEMENTOS DE TESTE:
    # Quadrado Verde padrão
    pygame.draw.rect(tela, (0, 255, 0), (150, 250, 100, 100))
    # Círculo Rosa/Magenta para testar canais de cor
    pygame.draw.circle(tela, (255, 0, 128), (600, 300), 60)
    # Bloco Camuflado (Invisível a olho nu, mas detectável por filtros)
    pygame.draw.rect(tela, COR_BLOCO_OCULTO, (320, 400, 160, 80))
    
    # Desenha uma linha branca fina dentro do bloco oculto para testar detecção de borda
    pygame.draw.rect(tela, (25, 25, 25), (320, 400, 160, 80), width=1)

    # 4. CAPTURA DO BUFFER E FILTRAGEM VIA OPENCV
    # Só capturamos e processamos se o filtro não for o "Normal" (0)
    if FILTRO_ATUAL > 0:
        # Transforma a tela do Pygame em matriz NumPy BGR
        pixel_array = pygame.surfarray.array3d(tela)
        matriz_imagem = np.transpose(pixel_array, (1, 0, 2))
        imagem_bgr = cv2.cvtColor(matriz_imagem, cv2.COLOR_RGB2BGR)
        
        # MATRIZ DE DESTINO DO PROCESSAMENTO
        imagem_processada = imagem_bgr.copy()

        # APLICAÇÃO DOS FILTROS ACADÊMICOS
        if FILTRO_ATUAL == 1:
            # FILTRO 1: Escala de Cinza Simples
            cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
            imagem_processada = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
            
        elif FILTRO_ATUAL == 2:
            # FILTRO 2: Detecção de Bordas (Sobel)
            cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
            # Sobel no eixo X e Y
            sobel_x = cv2.Sobel(cinza, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(cinza, cv2.CV_64F, 0, 1, ksize=3)
            # Magnitude das bordas
            magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            magnitude = np.uint8(np.clip(magnitude, 0, 255))
            magnitude = np.ascontiguousarray(magnitude)
            imagem_processada = cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)
            
        elif FILTRO_ATUAL == 3:
            # FILTRO 3: Threshold / Limiarização (Realce de Contraste Extremo)
            cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
            # Tudo que for maior que o tom 21 vira branco puro (255). 
            # Como nosso bloco oculto é tom 23, ele vai virar branco e saltar na tela!
            _, threshold = cv2.threshold(cinza, 21, 255, cv2.THRESH_BINARY)
            imagem_processada = cv2.cvtColor(threshold, cv2.COLOR_GRAY2BGR)

        # Devolve a matriz processada de volta para o formato do Pygame
        imagem_rgb = cv2.cvtColor(imagem_processada, cv2.COLOR_BGR2RGB)
        pixel_array_final = np.transpose(imagem_rgb, (1, 0, 2))
        surface_filtrada = pygame.surfarray.make_surface(pixel_array_final)
        
        # Desenha a tela modificada
        tela.blit(surface_filtrada, (0, 0))

    # 5. RENDERIZAÇÃO DA HUD FIXA (Sempre por cima dos filtros)
    # Barra de fundo dos botões
    pygame.draw.rect(tela, (15, 15, 18), (0, 0, LARGURA, 80))
    pygame.draw.rect(tela, (0, 128, 255), (0, 78, LARGURA, 2))

    # Desenha cada botão da lista
    for btn in botoes:
        # Define a cor baseado no estado (Ativo, Hover ou Normal)
        if FILTRO_ATUAL == btn["id"]:
            cor_btn = (0, 128, 255)       # Azul se estiver ativo
        elif btn["rect"].collidepoint(pos_mouse):
            cor_btn = (60, 60, 70)         # Cinza claro no Hover
        else:
            cor_btn = (35, 35, 40)         # Cor padrão escura
            
        pygame.draw.rect(tela, cor_btn, btn["rect"], border_radius=5)
        pygame.draw.rect(tela, (80, 80, 90), btn["rect"], width=1, border_radius=5)
        
        # Texto do botão
        txt_surf = FONTE_HUD.render(btn["text" if "text" in btn else "texto"], True, (255, 255, 255))
        tela.blit(txt_surf, (btn["rect"].x + 12, btn["rect"].y + 10))

    pygame.display.flip()
    relogio.tick(60)