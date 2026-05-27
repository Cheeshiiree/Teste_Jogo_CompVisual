import pygame
import numpy as np
import cv2
import sys

# 1. Inicialização do Pygame
pygame.init()
pygame.font.init()  # Inicializa o sistema de fontes para escrever no botão

# Configurações da janela de teste
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 1 - Teste de Botão com Mouse")
relogio = pygame.time.Clock()

# Fonte para o texto do botão
FONTE = pygame.font.SysFont("Arial", 20)

# 2. Criação de Elementos Gráficos Simples para o Teste
COR_FUNDO = (20, 20, 20)
COR_BLOCO_OCULTO = (20, 20, 20)  
COR_PLAYER_TESTE = (0, 255, 0)     
QUADRADO_VERMELHO = (255, 0, 0)            

# Configurações do BOTÃO (Posição X, Y, Largura, Altura)
RETANGULO_BOTAO = pygame.Rect(20, 20, 180, 40)
COR_BOTAO_NORMAL = (50, 50, 50)
COR_BOTAO_HOVER = (80, 80, 80)     # Cor quando o mouse está em cima
COR_BOTAO_ATIVO = (0, 128, 255)    # Cor quando o filtro está ligado
COR_TEXTO = (255, 255, 255)

# Posição inicial do player de teste
player_x, player_y = 100, 450
player_velocidade = 5

# Controle de estado do filtro de teste
aplicar_filtro_cinza = False

# Loop principal do jogo de teste
while True:
    # Captura a posição atual do mouse (X, Y) a cada frame
    posicao_mouse = pygame.mouse.get_pos()
    
    # Verifica se o mouse está posicionado em cima do retângulo do botão (Efeito Hover)
    mouse_em_cima_do_botao = RETANGULO_BOTAO.collidepoint(posicao_mouse)

    # Gerenciamento de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # EVENTO DE MOUSE: Verifica o clique do botão esquerdo
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # 1 significa botão esquerdo do mouse
                if mouse_em_cima_do_botao:
                    aplicar_filtro_cinza = not aplicar_filtro_cinza
                    print(f"Botão Clicado! Filtro: {aplicar_filtro_cinza}")

    # Movimentação super básica do player
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        player_x -= player_velocidade
    if teclas[pygame.K_RIGHT]:
        player_x += player_velocidade

    # 3. RENDERIZAÇÃO DA CENA ORIGINAL (Pre-processamento)
    tela.fill(COR_FUNDO)
    
    # Desenha um "bloco secreto" no chão
    pygame.draw.rect(tela, COR_BLOCO_OCULTO, (300, 400, 200, 100))
    
    # Desenha o bloco vermelho para teste de contraste
    pygame.draw.rect(tela, QUADRADO_VERMELHO, (300, 50, 100, 100))

    # Desenha o player (quadrado verde)
    pygame.draw.rect(tela, COR_PLAYER_TESTE, (player_x, player_y, 40, 40))

    # Definindo a cor dinâmica do botão baseado no estado
    if aplicar_filtro_cinza:
        cor_atual_botao = COR_BOTAO_ATIVO
    elif mouse_em_cima_do_botao:
        cor_atual_botao = COR_BOTAO_HOVER
    else:
        cor_atual_botao = COR_BOTAO_NORMAL

    # Desenha o retângulo do botão na tela
    pygame.draw.rect(tela, cor_atual_botao, RETANGULO_BOTAO, border_radius=5)
    
    # Renderiza o texto do botão
    texto_surface = FONTE.render("Escala de Cinza", True, COR_TEXTO)
    # Centraliza o texto dentro do retângulo do botão
    tela.blit(texto_surface, (RETANGULO_BOTAO.x + 25, RETANGULO_BOTAO.y + 8))

    # 4. CAPTURA E FILTRAGEM (Computação Visual)
    if aplicar_filtro_cinza:
        pixel_array = pygame.surfarray.array3d(tela)
        matriz_imagem = np.transpose(pixel_array, (1, 0, 2))
        imagem_bgr = cv2.cvtColor(matriz_imagem, cv2.COLOR_RGB2BGR)
        
        imagem_processada_bgr = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
        imagem_processada_rgb = cv2.cvtColor(imagem_processada_bgr, cv2.COLOR_GRAY2RGB)
        
        pixel_array_final = np.transpose(imagem_processada_rgb, (1, 0, 2))
        surface_filtrada = pygame.surfarray.make_surface(pixel_array_final)
        
        tela.blit(surface_filtrada, (0, 0))

        # Mantendo sua lógica original: Altera a cor do bloco oculto clareando ele
        pygame.draw.rect(tela, (100, 100, 100), (300, 400, 200, 100))

    # Atualiza o monitor e crava em 60 FPS
    pygame.display.flip()
    relogio.tick(60)