import pygame
import random
import sys
import numpy as np
import cv2
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP

# IMPORTAÇÃO DO NOSSO MOTOR DE FILTROS SEPARADO
import processamento_imagem as pdi

pygame.init()
pygame.font.init()

# NOVA RESOLUÇÃO EXPANDIDA (Estilo HD para caber todo o seu design)
LARGURA, ALTURA = 1280, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 8 - Interface Humana e Central de Filtros")
relogio = pygame.time.Clock()

FONTE_P = pygame.font.SysFont("Arial", 13, bold=True)
FONTE_M = pygame.font.SysFont("Arial", 16, bold=True)

# 📐 Definição das Novas Coordenadas Baseadas no Rascunho 2
ALTURA_JOGO = 480
RETANGULO_JOGO = pygame.Rect(0, 0, LARGURA, ALTURA_JOGO)
PANEL_CONTROLE = pygame.Rect(0, ALTURA_JOGO, LARGURA, ALTURA - ALTURA_JOGO)

# Subdivisões do Painel Inferior (Y variando de 480 a 720 -> 240px de espaço)
RETANGULO_LENS = pygame.Rect(0, ALTURA_JOGO, 350, 240)
RETANGULO_SLIDERS = pygame.Rect(350, ALTURA_JOGO, 450, 240)
RETANGULO_TRANSF = pygame.Rect(800, ALTURA_JOGO, 250, 240)
RETANGULO_HIST = pygame.Rect(1050, ALTURA_JOGO, 230, 240)

COR_FUNDO = (20, 20, 22)

# Classes Auxiliares de UI (Formas e Sliders)
class FormaGeometrica:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x, self.y = x, y
        self.tamanho = random.randint(50, 90)
        self.rotacao = 0
        self.r, self.g, self.b = random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)

    def desenhar(self, superficie, selecionada=False):
        surf = pygame.Surface((self.tamanho * 2, self.tamanho * 2), pygame.SRCALPHA)
        centro = (self.tamanho, self.tamanho)
        cor = (self.r, self.g, self.b)
        
        if self.tipo == "retangulo":
            pygame.draw.rect(surf, cor, (self.tamanho//2, self.tamanho//2, self.tamanho, self.tamanho))
            if selecionada: pygame.draw.rect(surf, (255, 255, 0), (self.tamanho//2, self.tamanho//2, self.tamanho, self.tamanho), width=3)
        elif self.tipo == "circulo":
            pygame.draw.circle(surf, cor, centro, self.tamanho // 2)
            if selecionada: pygame.draw.circle(surf, (255, 255, 0), centro, self.tamanho // 2, width=3)
        elif self.tipo == "triangulo":
            p1, p2, p3 = (self.tamanho, self.tamanho//2), (self.tamanho//2, self.tamanho + self.tamanho//2), (self.tamanho + self.tamanho//2, self.tamanho + self.tamanho//2)
            pygame.draw.polygon(surf, cor, [p1, p2, p3])
            if selecionada: pygame.draw.polygon(surf, (255, 255, 0), [p1, p2, p3], width=3)

        surf_rot = pygame.transform.rotate(surf, self.rotacao)
        superficie.blit(surf_rot, surf_rot.get_rect(center=(self.x, self.y)).topleft)

    def checar_clique(self, mouse_pos):
        return ((self.x - mouse_pos[0])**2 + (self.y - mouse_pos[1])**2)**0.5 < (self.tamanho // 2)

class SliderHUD:
    def __init__(self, nome, x, y, largura, valor_inicial=0.5, cor_linha=(100, 100, 100)):
        self.nome = nome
        self.rect_linha = pygame.Rect(x, y, largura, 4)
        self.valor = valor_inicial
        self.cor_linha = cor_linha
        self.rect_cursor = pygame.Rect(x + int(largura * valor_inicial) - 6, y - 8, 12, 20)
        self.arrastando = False

    def desenhar(self, superficie):
        pygame.draw.rect(superficie, self.cor_linha, self.rect_linha)
        pygame.draw.rect(superficie, (200, 200, 200), self.rect_cursor, border_radius=4)
        txt = FONTE_P.render(f"{self.nome}: {int(self.valor * 100)}%", True, (255, 255, 255))
        superficie.blit(txt, (self.rect_linha.x, self.rect_linha.y - 18))

    def atualizar(self, mouse_pos):
        if self.arrastando:
            x_local = max(self.rect_linha.x, min(mouse_pos[0], self.rect_linha.right))
            self.valor = (x_local - self.rect_linha.x) / self.rect_linha.width
            self.rect_cursor.x = x_local - 6

# Inicialização de Objetos de Teste
formas = [FormaGeometrica(random.choice(["retangulo", "circulo", "triangulo"]), random.randint(150, 1100), random.randint(100, 380)) for _ in range(6)]
forma_selecionada = None

# Sliders alinhados com o novo tamanho de tela
sliders = [
    SliderHUD("Red", 380, 530, 160, cor_linha=(255, 50, 50)),
    SliderHUD("Green", 380, 590, 160, cor_linha=(50, 255, 50)),
    SliderHUD("Blue", 380, 650, 160, cor_linha=(50, 50, 255)),
    SliderHUD("Brilho", 580, 530, 160),
    SliderHUD("Contraste", 580, 590, 160),
    SliderHUD("Saturação", 580, 650, 160)
]

# Mapeamento dos botões de Filtros da LENS (Agora funcionais!)
nomes_filtros = ["Cinza", "Sobel (Linhas)", "Desfocar (Blur)", "Ruído S&P", "Filtro Mediana", "Inverter", "F6 (Vazio)", "Reset Global"]
botoes_lens = []
for i, nome in enumerate(nomes_filtros):
    col, lin = i % 4, i // 4
    bx = 20 + (col * 80)
    by = 530 + (lin * 60)
    botoes_lens.append({"id": i, "nome": nome, "rect": pygame.Rect(bx, by, 72, 45), "ativo": False})

# Loop Principal do Jogo
while True:
    pos_mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:
                for s in sliders:
                    if s.rect_cursor.collidepoint(pos_mouse): s.arrastando = True
                
                # Clique nos Filtros da Seção LENS
                for btn in botoes_lens:
                    if btn["rect"].collidepoint(pos_mouse):
                        if btn["id"] == 7: # Botão de Reset
                            for b in botoes_lens: b["ativo"] = False
                            for s in sliders: s.valor = 0.5
                        else:
                            btn["ativo"] = not btn["ativo"]

                # Clique na Tela de Jogo (Seleção de Formas)
                if RETANGULO_JOGO.collidepoint(pos_mouse):
                    clicou_forma = False
                    for f in formas:
                        if f.checar_clique(pos_mouse):
                            forma_selecionada = f
                            clicou_forma = True
                            # Sincroniza sliders com a cor real da forma ao selecionar
                            sliders[0].valor = f.r / 255
                            sliders[1].valor = f.g / 255
                            sliders[2].valor = f.b / 255
                            break
                    if not clicou_forma: forma_selecionada = None

        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                for s in sliders: s.arrastando = False

    for s in sliders: s.atualizar(pos_mouse)

    # ---------------------------------------------------------
    # APLICAÇÃO CONTEXTUAL DAS TRANSFORMAÇÕES E CORES
    # ---------------------------------------------------------
    if forma_selecionada:
        # Altera apenas a cor do objeto selecionado individualmente via Sliders R G B
        forma_selecionada.r = int(sliders[0].valor * 255)
        forma_selecionada.g = int(sliders[1].valor * 255)
        forma_selecionada.b = int(sliders[2].valor * 255)
        
        # Escuta Teclado para o NOVO Bloco de Transformações
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:  forma_selecionada.x -= 4  # Translação
        if teclas[pygame.K_RIGHT]: forma_selecionada.x += 4
        if teclas[pygame.K_UP]:    forma_selecionada.y -= 4
        if teclas[pygame.K_DOWN]:  forma_selecionada.y += 4
        if teclas[pygame.K_q]:     forma_selecionada.rotacao += 3 # Rotação (Seu rascunho: Q e E)
        if teclas[pygame.K_e]:     forma_selecionada.rotacao -= 3
        if teclas[pygame.K_r]:     forma_selecionada.tamanho = min(200, forma_selecionada.tamanho + 2) # Escala (R T Y)
        if teclas[pygame.K_t]:     forma_selecionada.tamanho = max(30, forma_selecionada.tamanho - 2)

    # 5. RENDERIZAÇÃO DA CENA ORIGINAL (Pré-processamento)
    tela.fill(COR_FUNDO)
    for f in formas:
        f.desenhar(tela, selecionada=(f == forma_selecionada))
        
    txt_obj = FONTE_M.render("Objetivo: Teste os filtros de PDI e as transformações geométricas nos objetos", True, (200, 200, 200))
    tela.blit(txt_obj, (20, 20))

    # ---------------------------------------------------------
    # 🎛️ CAPTURA E PROCESSAMENTO REAL VIA OPENCV (Agora Funcional!)
    # ---------------------------------------------------------
    # Capturamos a área de jogo para aplicar os filtros globais
    textura_jogo = pygame.surfarray.array3d(tela)
    matriz_jogo = np.transpose(textura_jogo, (1, 0, 2))
    matriz_bgr = cv2.cvtColor(matriz_jogo, cv2.COLOR_RGB2BGR)
    
    # Corta a matriz para processar apenas a região de jogo (Y de 0 a 480)
    matriz_cena = matriz_bgr[0:ALTURA_JOGO, 0:LARGURA]

    # Aplicação dos Filtros de acordo com o estado dos botões da LENS
    if botoes_lens[0]["ativo"]: matriz_cena = pdi.aplicar_escala_cinza(matriz_cena)
    if botoes_lens[1]["ativo"]: matriz_cena = pdi.aplicar_sobel(matriz_cena)
    if botoes_lens[2]["ativo"]: matriz_cena = pdi.aplicar_blur(matriz_cena)
    if botoes_lens[3]["ativo"]: matriz_cena = pdi.injetar_ruido_salt_pepper(matriz_cena)
    if botoes_lens[4]["ativo"]: matriz_cena = pdi.aplicar_filtro_mediana(matriz_cena)
    if botoes_lens[5]["ativo"]: matriz_cena = cv2.bitwise_not(matriz_cena) # Inversão de Cores rápida

    # Aplicação dos Sliders Globais de Brilho, Contraste e Saturação (Se nenhuma forma estiver selecionada)
    if not forma_selecionada:
        fator_brilho = int((sliders[3].valor - 0.5) * 200)       # Varia de -100 a +100
        fator_contraste = float(sliders[4].valor * 2.0)          # Varia de 0.0 a 2.0
        fator_saturacao = float(sliders[5].valor * 3.0)          # Varia de 0.0 a 3.0
        matriz_cena = pdi.ajustar_brilho_contraste_saturação(matriz_cena, fator_brilho, fator_contraste, fator_saturacao)

    # Devolve a cena tratada pelo OpenCV para o monitor
    cena_rgb = cv2.cvtColor(matriz_cena, cv2.COLOR_BGR2RGB)
    array_final = np.transpose(cena_rgb, (1, 0, 2))
    surface_render = pygame.surfarray.make_surface(array_final)
    tela.blit(surface_render, (0, 0))

    # ---------------------------------------------------------
    # 🎚️ DESENHO DA HUD COMPLETA (Por cima de tudo, fixa na janela)
    # ---------------------------------------------------------
    pygame.draw.rect(tela, (24, 24, 27), PANEL_CONTROLE)
    pygame.draw.rect(tela, (0, 128, 255), PANEL_CONTROLE, width=2)

    # Linhas Divisórias das Caixas do Tldraw
    pygame.draw.line(tela, (50, 50, 60), (350, ALTURA_JOGO), (350, ALTURA), width=2)
    pygame.draw.line(tela, (50, 50, 60), (800, ALTURA_JOGO), (800, ALTURA), width=2)
    pygame.draw.line(tela, (50, 50, 60), (1050, ALTURA_JOGO), (1050, ALTURA), width=2)

    # 1. Desenho da Seção LENS
    tela.blit(FONTE_M.render("LENS (Filtros & Ruídos)", True, (0, 128, 255)), (20, 495))
    for btn in botoes_lens:
        cor = (0, 128, 255) if btn["ativo"] else ((70, 70, 80) if btn["rect"].collidepoint(pos_mouse) else (40, 40, 45))
        pygame.draw.rect(tela, cor, btn["rect"], border_radius=4)
        pygame.draw.rect(tela, (90, 90, 100), btn["rect"], width=1, border_radius=4)
        
        # Mostra as duas primeiras letras do nome do filtro dentro do botão
        txt_n = FONTE_P.render(btn["nome"][:8], True, (255, 255, 255))
        tela.blit(txt_n, (btn["rect"].x + 6, btn["rect"].y + 15))

    # 2. Desenho da Seção SLIDERS
    tela.blit(FONTE_M.render("Ajustes de PDI / Canais", True, (255, 255, 255)), (370, 495))
    for s in sliders: s.desenhar(tela)

    # 3. Desenho da Nova Seção TRANSFORMAÇÕES CONTEXTUAIS
    tela.blit(FONTE_M.render("Transformações", True, (255, 215, 0)), (820, 495))
    if forma_selecionada:
        # Se um objeto estiver focado, mostra as instruções de controle idênticas ao desenho
        tela.blit(FONTE_P.render("🔄 Rotação: Teclas Q <- -> E", True, (230, 230, 230)), (820, 540))
        tela.blit(FONTE_P.render("🎮 Translação: Setas do Teclado", True, (230, 230, 230)), (820, 580))
        tela.blit(FONTE_P.render("📐 Escala: Teclas R (+) e T (-)", True, (230, 230, 230)), (820, 620))
        
        pygame.draw.rect(tela, (255, 215, 0), (1000, 495, 40, 20), border_radius=3)
        tela.blit(FONTE_P.render("OBJ", True, (0, 0, 0)), (1008, 498))
    else:
        tela.blit(FONTE_P.render("Clique em um objeto para", True, (120, 120, 120)), (820, 550))
        tela.blit(FONTE_P.render("liberar transformações.", True, (120, 120, 120)), (820, 570))

    # 4. Desenho e Cálculo do HISTOGRAMA Real através do nosso módulo PDI
    tela.blit(FONTE_M.render("Histograma", True, (255, 255, 255)), (1070, 495))
    surface_histograma = pdi.calcular_histograma_surface(matriz_cena, largura=200, altura=130)
    tela.blit(surface_histograma, (1065, 535))
    pygame.draw.rect(tela, (90, 90, 100), (1065, 535, 200, 130), width=1) # Contorno do gráfico

    pygame.display.flip()
    relogio.tick(60)