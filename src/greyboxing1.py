import pygame
import numpy as np
import cv2
import sys

# 1. Inicialização do Pygame
pygame.init()

# Configurações da janela de teste
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 1 - Teste de Captura e Filtro")
relogio = pygame.time.Clock()

# 2. Criação de Elementos Gráficos Simples para o Teste
# Um fundo escuro e um bloco camuflado (baixo contraste) para simular o Desafio 1
COR_FUNDO = (20, 20, 20)
COR_BLOCO_OCULTO = (20, 20, 20)  # Quase invisível no fundo escuro
COR_PLAYER_TESTE = (0, 255, 0)     # Quadrado verde para o player
QUADRADO_VERMELHO = (255, 0, 0)            # Quadrado vermelho para teste de contraste

# Posição inicial do player de teste
player_x, player_y = 100, 450
player_velocidade = 5

# Controle de estado do filtro de teste
aplicar_filtro_cinza = False

# Loop principal do jogo de teste
while True:
    # Gerenciamento de eventos (Teclado e Fechamento de janela)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Tecla ESPAÇO ativa/desativa o modo de teste do OpenCV
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                aplicar_filtro_cinza = not aplicar_filtro_cinza
                print(# Ativar/Desativar Filtro
                    f"Modo Processamento de Imagem: {aplicar_filtro_cinza}"
                )

    # Movimentação super básica do player para testar se a tela atualiza
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        player_x -= player_velocidade
    if teclas[pygame.K_RIGHT]:
        player_x += player_velocidade

    # 3. RENDERIZAÇÃO DA CENA ORIGINAL (Pre-processamento)
    tela.fill(COR_FUNDO)
    
    # Desenha um "bloco secreto" no chão (Greyboxing do desafio de contraste)
    pygame.draw.rect(tela, COR_BLOCO_OCULTO, (300, 400, 200, 100))
    
    # Desenha o bloco vermelho para teste de contraste
    pygame.draw.rect(tela, QUADRADO_VERMELHO, (300, 50, 100, 100)) # Posição X, Y, Largura, Altura

    # Desenha o player (quadrado verde)
    pygame.draw.rect(tela, COR_PLAYER_TESTE, (player_x, player_y, 40, 40))

    # 4. O PULO DO GATO: Captura do Buffer da Tela para Computação Visual
    if aplicar_filtro_cinza:
        # Captura os pixels da tela do Pygame como uma matriz 3D (X, Y, RGB)
        pixel_array = pygame.surfarray.array3d(tela)
        
        # Transpõe os eixos para o padrão de imagem que o OpenCV/NumPy usam (Y, X, RGB)
        matriz_imagem = np.transpose(pixel_array, (1, 0, 2))
        
        # OpenCV trabalha por padrão em BGR, então convertemos de RGB para BGR
        imagem_bgr = cv2.cvtColor(matriz_imagem, cv2.COLOR_RGB2BGR)
        
        # EXEMPLO DE PROCESSO: Transforma a imagem da tela inteira em Tons de Cinza
        imagem_processada_bgr = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
        
        # Converte de volta para RGB para o Pygame conseguir exibir
        imagem_processada_rgb = cv2.cvtColor(imagem_processada_bgr, cv2.COLOR_GRAY2RGB)
        
        # Transpõe de volta para o formato do Pygame (X, Y, RGB)
        pixel_array_final = np.transpose(imagem_processada_rgb, (1, 0, 2))
        
        # Cria uma nova "Surface" do Pygame com a imagem modificada pelo OpenCV
        surface_filtrada = pygame.surfarray.make_surface(pixel_array_final)
        
        # Desenha a imagem modificada por cima da tela original
        tela.blit(surface_filtrada, (0, 0))

        # Altera a cor do bloco oculto clareando ele para testar o contraste
        pygame.draw.rect(tela, (100, 100, 100), (300, 400, 200, 100)) # Bloco oculto clareado para teste de contraste

    # Atualiza o monitor e crava em 60 FPS
    pygame.display.flip()
    relogio.tick(60)