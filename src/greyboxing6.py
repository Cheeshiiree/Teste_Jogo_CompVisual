import pygame
import sys
import ctypes
import os

# 1. Configuração do Ícone da Barra de Tarefas direto na API do Windows
try:
    import win32gui
    import win32con
    
    # Força o Windows a tratar o jogo como um processo único
    meu_appid = 'unifei.computacaovisual.visionquest.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(meu_appid)
    
    # Obtém o identificador (handle) da janela atual do Pygame
    hwnd = win32gui.GetForegroundWindow()
    
    # Carrega a imagem do troféu usando a API do Windows
    hicon = win32gui.LoadImage(
        0, 
        "assets/sprites/misc/icone_barraTarefas.png", 
        win32con.IMAGE_ICON, 
        0, 0, 
        win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    )
    
    # Usando hash() nós extraímos o ID numérico inteiro puro do handle.
    # Isso engana o Pylance perfeitamente porque hash() sempre retorna um 'int' válido!
    hicon_int = hash(hicon)
    
    # Envia a mensagem para o Windows aplicar o troféu na Barra de Tarefas
    win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, hicon_int)
except Exception as e:
    print(f"Aviso: Não foi possível aplicar o ícone na barra de tarefas: {e}")

# 2. Inicialização e Configurações Básicas do Pygame
pygame.init()
pygame.font.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 6 - Interface, HUD Fixa e Câmera")
relogio = pygame.time.Clock()

FONTE_HUD = pygame.font.SysFont("Arial", 18, bold=True)
FONTE_SPLASH = pygame.font.SysFont("Arial", 40, bold=True)

# 3. Configuração do Ícone da Barra de Título (Fantasminha Laranja) pelo Pygame
try:
    icone_fantasma = pygame.image.load("assets/sprites/misc/icon_janela.png")
    pygame.display.set_icon(icone_fantasma)
except pygame.error:
    print("Aviso: Fantasminha não encontrado em 'assets/sprites/misc/icon_janela.png'. Usando padrão.")

# Cores do Sistema
COR_FUNDO = (30, 30, 35)
COR_TEXTO = (255, 255, 255)

# ---------------------------------------------------------
# FUNÇÃO DA SPLASH SCREEN (Tela Inicial Customizada)
# ---------------------------------------------------------
def ExecutarSplashScreen():
    """Mostra uma tela de carregamento com a imagem da caixa por 3 segundos ou até clicar"""
    tempo_inicial = pygame.time.get_ticks()
    
    logo_splash = None
    try:
        logo_splash = pygame.image.load("assets/sprites/misc/splash_logo.png")
    except pygame.error:
        print("Aviso: Logo da Splash não encontrado em 'assets/sprites/misc/splash_logo.png'.")

    mostrando_splash = True
    while mostrando_splash:
        if pygame.time.get_ticks() - tempo_inicial > 3000:
            mostrando_splash = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN or evento.type == pygame.KEYDOWN:
                mostrando_splash = False

        tela.fill((15, 15, 20)) # Fundo escuro para destacar a arte
        
        if logo_splash:
            rect_logo = logo_splash.get_rect(center=(LARGURA // 2, ALTURA // 2))
            tela.blit(logo_splash, rect_logo)
        else:
            texto_logo = FONTE_SPLASH.render("VISION QUEST", True, (0, 128, 255))
            tela.blit(texto_logo, (LARGURA // 2 - texto_logo.get_width() // 2, ALTURA // 2 - 20))

        texto_pular = FONTE_HUD.render("Pressione qualquer tecla para iniciar", True, (100, 100, 100))
        tela.blit(texto_pular, (LARGURA // 2 - texto_pular.get_width() // 2, ALTURA - 50))

        pygame.display.flip()
        relogio.tick(60)

# Executa a splash screen antes do jogo começar
ExecutarSplashScreen()

# ---------------------------------------------------------
# CONFIGURAÇÕES DO JOGO (Pós-Splash)
# ---------------------------------------------------------
player_x, player_y = 100, 450
player_largura, player_altura = 40, 40
player_velocidade = 5
camera_x = 0

# Elementos do Mundo Sidescrolling
blocos_mundo = [
    (0, 500, 2000, 100, (50, 50, 50)),       # Chão bem longo
    (300, 400, 150, 30, (100, 50, 50)),      # Plataforma 1
    (600, 320, 150, 30, (50, 100, 50)),      # Plataforma 2
    (1000, 250, 100, 250, (50, 50, 100)),    # Barreira/Obstáculo
    (1300, 420, 200, 30, (120, 120, 50)),    # Plataforma 3
    (1600, 450, 50, 50, (255, 215, 0))       # Item "Estrela" Dourada no fim
]

# Configurações do Botão Estilizado da HUD (Fixo na Tela)
RETANGULO_BOTAO = pygame.Rect(600, 20, 180, 40)
cor_botao = (40, 40, 45)
filtro_ativo = False
interacoes = 0

# Loop principal do jogo
while True:
    pos_mouse = pygame.mouse.get_pos()
    mouse_em_cima_do_botao = RETANGULO_BOTAO.collidepoint(pos_mouse)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if mouse_em_cima_do_botao:
                    filtro_ativo = not filtro_ativo
                    interacoes += 1
                    print(f"HUD: Botão de Filtro Alternado! Estado: {filtro_ativo}")

    # Controles do Player (Andar para os lados)
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT] and player_x > 0:
        player_x -= player_velocidade
    if teclas[pygame.K_RIGHT]:
        player_x += player_velocidade

    # Sistema de Câmera Dinâmica (Sidescrolling)
    if player_x > LARGURA // 2:
        camera_x = player_x - LARGURA // 2
    else:
        camera_x = 0

    # Renderização do Frame
    tela.fill(COR_FUNDO)

    # --- CAMADA 1: Cenário que se move com a Câmera (Mundo) ---
    for bloco in blocos_mundo:
        bx, by, bw, bh, cor = bloco
        pygame.draw.rect(tela, cor, (bx - camera_x, by, bw, bh))

    # Player renderizado em relação ao X da câmera
    pygame.draw.rect(tela, (0, 255, 0), (player_x - camera_x, player_y, player_largura, player_altura))

    # --- CAMADA 2: HUD fixa na janela (Ignora a Câmera) ---
    # Painel superior escuro
    pygame.draw.rect(tela, (20, 20, 25), (0, 0, LARGURA, 80))
    pygame.draw.rect(tela, (0, 128, 255), (0, 78, LARGURA, 2)) # Divisória azul neon

    # Renderização dos textos estáticos da HUD
    txt_pos = FONTE_HUD.render(f"Posição no Mundo: {player_x}m", True, COR_TEXTO)
    txt_cam = FONTE_HUD.render(f"Deslocamento Câmera: {camera_x}px", True, (150, 150, 150))
    txt_int = FONTE_HUD.render(f"Cliques no Botão: {interacoes}", True, COR_TEXTO)
    
    tela.blit(txt_pos, (20, 15))
    tela.blit(txt_cam, (20, 45))
    tela.blit(txt_int, (320, 30))

    # Design Estilizado do Botão (Estados: Ativo, Hover, Normal)
    if filtro_ativo:
        cor_botao = (0, 128, 255)
    elif mouse_em_cima_do_botao:
        cor_botao = (70, 70, 80)
    else:
        cor_botao = (40, 40, 45)

    pygame.draw.rect(tela, cor_botao, RETANGULO_BOTAO, border_radius=6)
    pygame.draw.rect(tela, (100, 100, 110), RETANGULO_BOTAO, width=2, border_radius=6) # Contorno sutil

    texto_btn = "Filtro CV: ATIVO" if filtro_ativo else "Filtro CV: INATIVO"
    txt_btn_surface = FONTE_HUD.render(texto_btn, True, COR_TEXTO)
    tela.blit(txt_btn_surface, (RETANGULO_BOTAO.x + 18, RETANGULO_BOTAO.y + 10))

    pygame.display.flip()
    relogio.tick(60)