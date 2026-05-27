import pygame
import numpy as np
import cv2
import sys

# 1. Inicialização do Pygame
pygame.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 1 - Teste de Mouse e Filtro Local")
relogio = pygame.time.Clock()

# Cores de teste
COR_FUNDO = (20, 20, 20)
COR_BLOCO_OCULTO = (30, 30, 30)
COR_PLAYER_TESTE = (0, 255, 0)     # Quadrado Verde
COR_CUBO_TESTE2 = (255, 0, 128)    # Cubo Rosa/Magenta para testar os canais de cor

# Posições dos objetos
player_x, player_y = 100, 450
player_velocidade = 5

cubo2_x, cubo2_y = 550, 400

# Configuração da Lupa (Filtro Local)
RAIO_LUPA = 80

while True:
    # Captura a posição atual do mouse (X, Y) a cada frame
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Movimentação do player no teclado
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        player_x -= player_velocidade
    if teclas[pygame.K_RIGHT]:
        player_x += player_velocidade

    # Verifica se o botão ESQUERDO do mouse está sendo pressionado/segurado
    # pygame.mouse.get_pressed() retorna (Botao1, Botao2, Botao3)
    mouse_pressionado = pygame.mouse.get_pressed()
    clique_esquerdo = mouse_pressionado[0] 

    # 3. RENDERIZAÇÃO DA CENA ORIGINAL
    tela.fill(COR_FUNDO)
    
    # Desenha o bloco camuflado de antes
    pygame.draw.rect(tela, COR_BLOCO_OCULTO, (300, 430, 200, 100))
    
    # Desenha o Player 1 (Verde)
    pygame.draw.rect(tela, COR_PLAYER_TESTE, (player_x, player_y, 40, 40))
    
    # NOVO: Desenha o Player 2/Cubo de Teste (Rosa) para validar o canal de cor
    pygame.draw.rect(tela, COR_CUBO_TESTE2, (cubo2_x, cubo2_y, 60, 60))

    # 4. PROCESSAMENTO VISUAL (Se o clique do mouse estiver segurado)
    if clique_esquerdo:
        # Captura a tela atual do Pygame
        pixel_array = pygame.surfarray.array3d(tela)
        matriz_imagem = np.transpose(pixel_array, (1, 0, 2))
        imagem_bgr = cv2.cvtColor(matriz_imagem, cv2.COLOR_RGB2BGR)
        
        # Cria uma máscara preta do mesmo tamanho da tela
        mascara = np.zeros(imagem_bgr.shape[:2], dtype=np.uint8)
        # Desenha um círculo branco na máscara EXATAMENTE onde o mouse está
        cv2.circle(mascara, (mouse_x, mouse_y), RAIO_LUPA, 255, -1)
        
        # Aplica o filtro de tons de cinza na imagem cheia
        imagem_cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
        imagem_cinza_bgr = cv2.cvtColor(imagem_cinza, cv2.COLOR_GRAY2BGR)
        
        # JUNTANDO AS IMAGENS: Onde a máscara é branca fica cinza, onde é preta fica colorido
        imagem_final_bgr = np.where(mascara[:, :, None] == 255, imagem_cinza_bgr, imagem_bgr)
        
        # Devolve para o Pygame
        imagem_final_rgb = cv2.cvtColor(imagem_final_bgr, cv2.COLOR_BGR2RGB)
        pixel_array_final = np.transpose(imagem_final_rgb, (1, 0, 2))
        surface_filtrada = pygame.surfarray.make_surface(pixel_array_final)
        
        tela.blit(surface_filtrada, (0, 0))

    # Desenha uma linha de contorno para a lupa para o jogador ver onde ela está
    # (Usamos uma cor que contrasta bem para guiar o mouse)
    pygame.draw.circle(tela, (255, 255, 255), (mouse_x, mouse_y), RAIO_LUPA, 2)

    pygame.display.flip()
    relogio.tick(60)