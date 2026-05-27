import pygame
import random
import sys
# Importa explicitamente as constantes de eventos e teclado do Pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP

# 1. Inicialização do Pygame
# Cores do Cenário de Teste e Configurações da Janela
COR_FUNDO = (20, 20, 20)
pygame.init()
pygame.font.init()

LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 8 - Central de PDI e Transformações")
relogio = pygame.time.Clock()

FONTE_P_NEGRITO = pygame.font.SysFont("Arial", 14, bold=True)
FONTE_M_NEGRITO = pygame.font.SysFont("Arial", 18, bold=True)

# 2. Definição das Regiões do Layout (Baseado no esboço do Tldraw)
RETANGULO_JOGO = pygame.Rect(0, 0, 800, 400)          # Área das formas (Topo)
PANEL_CONTROLE = pygame.Rect(0, 400, 800, 200)         # Painel inferior completo
RETANGULO_LENS = pygame.Rect(0, 400, 280, 200)         # Seção de botões de filtros
RETANGULO_SLIDERS = pygame.Rect(280, 400, 360, 200)    # Seção das barras deslizantes
RETANGULO_HIST = pygame.Rect(640, 400, 160, 200)       # Espaço do gráfico do Histograma

# 3. Classe para Gerenciar as Formas Geométricas
class FormaGeometrica:
    def __init__(self, tipo, x, y):
        self.tipo = tipo  # "retangulo", "circulo" ou "triangulo"
        self.x = x
        self.y = y
        self.tamanho = random.randint(40, 80)
        self.rotacao = 0
        
        # Cores iniciais em canais separados (R, G, B)
        self.r = random.randint(50, 255)
        self.g = random.randint(50, 255)
        self.b = random.randint(50, 255)

    def desenhar(self, superficie, selecionada=False):
        cor = (self.r, self.g, self.b)
        
        # Cria a superfície interna para a forma
        surf_forma = pygame.Surface((self.tamanho * 2, self.tamanho * 2), pygame.SRCALPHA)
        centro_local = (self.tamanho, self.tamanho)
        
        # Desenha a forma e o seu respectivo contorno no mesmo bloco de escopo
        if self.tipo == "retangulo":
            pygame.draw.rect(surf_forma, cor, (self.tamanho // 2, self.tamanho // 2, self.tamanho, self.tamanho))
            if selecionada:
                pygame.draw.rect(surf_forma, (255, 255, 0), (self.tamanho // 2, self.tamanho // 2, self.tamanho, self.tamanho), width=3)
                
        elif self.tipo == "circulo":
            pygame.draw.circle(surf_forma, cor, centro_local, self.tamanho // 2)
            if selecionada:
                pygame.draw.circle(surf_forma, (255, 255, 0), centro_local, self.tamanho // 2, width=3)
                
        elif self.tipo == "triangulo":
            p1 = (self.tamanho, self.tamanho // 2)
            p2 = (self.tamanho // 2, self.tamanho + self.tamanho // 2)
            p3 = (self.tamanho + self.tamanho // 2, self.tamanho + self.tamanho // 2)
            pygame.draw.polygon(surf_forma, cor, [p1, p2, p3])
            if selecionada:
                pygame.draw.polygon(surf_forma, (255, 255, 0), [p1, p2, p3], width=3)

        # Aplica a Transformação Geométrica de Rotação
        surf_rotacionada = pygame.transform.rotate(surf_forma, self.rotacao)
        novo_rect = surf_rotacionada.get_rect(center=(self.x, self.y))
        
        superficie.blit(surf_rotacionada, novo_rect.topleft)

    def checar_clique(self, mouse_pos):
        """Verifica se o clique do mouse colidiu com a área da forma"""
        distancia = ((self.x - mouse_pos[0])**2 + (self.y - mouse_pos[1])**2)**0.5
        return distancia < (self.tamanho // 2)

# 4. Configuração dos Sliders da HUD (Guardam valor de 0.0 a 1.0)
class SliderHUD:
    def __init__(self, nome, x, y, largura, valor_inicial=0.5, cor_linha=(100, 100, 100)):
        self.nome = nome
        self.rect_linha = pygame.Rect(x, y, largura, 4)
        self.valor = valor_inicial
        self.cor_linha = cor_linha
        self.rect_cursor = pygame.Rect(x + int(largura * valor_inicial) - 6, y - 6, 12, 16)
        self.arrastando = False

    def desenhar(self, superficie):
        # Linha guia do slider
        pygame.draw.rect(superficie, self.cor_linha, self.rect_linha)
        # Cursor deslizante
        pygame.draw.rect(superficie, (200, 200, 200), self.rect_cursor, border_radius=3)
        # Texto descritivo
        txt = FONTE_P_NEGRITO.render(f"{self.nome}: {int(self.valor * 100)}%", True, (255, 255, 255))
        superficie.blit(txt, (self.rect_linha.x, self.rect_linha.y - 20))

    def atualizar(self, mouse_pos):
        if self.arrastando:
            # Limita a movimentação dentro do tamanho da linha
            x_local = max(self.rect_linha.x, min(mouse_pos[0], self.rect_linha.right))
            self.valor = (x_local - self.rect_linha.x) / self.rect_linha.width
            self.rect_cursor.x = x_local - 6

# Inicialização do Cenário de Teste
formas = []
def GerarCenarioAleatorio():
    formas.clear()
    tipos = ["retangulo", "circulo", "triangulo"]
    for _ in range(5):
        tipo = random.choice(tipos)
        x = random.randint(100, 700)
        y = random.randint(100, 300)
        formas.append(FormaGeometrica(tipo, x, y))

GerarCenarioAleatorio()
forma_selecionada = None

# Criando as instâncias dos Sliders conforme o Tldraw
sliders = [
    SliderHUD("Red", 300, 440, 140, cor_linha=(255, 50, 50)),
    SliderHUD("Green", 300, 490, 140, cor_linha=(50, 255, 50)),
    SliderHUD("Blue", 300, 540, 140, cor_linha=(50, 50, 255)),
    SliderHUD("Brilho", 480, 440, 140),
    SliderHUD("Contraste", 480, 490, 140),
    SliderHUD("Saturação", 480, 540, 140)
]

# Botões Simples da seção LENS (Matriz 2x4 como no desenho)
botoes_lens = []
for i in range(8):
    col = i % 4
    lin = i // 4
    bx = 20 + (col * 60)
    by = 440 + (lin * 50)
    botoes_lens.append({"id": i, "rect": pygame.Rect(bx, by, 50, 40), "ativo": False})

# Loop Principal
while True:
    pos_mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1: # Clique Esquerdo
                # 1. Verifica clique nos Sliders
                for s in sliders:
                    if s.rect_cursor.collidepoint(pos_mouse):
                        s.arrastando = True
                
                # 2. Verifica clique nos botões da Seção LENS
                for btn in botoes_lens:
                    if btn["rect"].collidepoint(pos_mouse):
                        btn["ativo"] = not btn["ativo"]
                        print(f"LENS: Botão {btn['id']} alternado para {btn['ativo']}")

                # 3. Lógica de Seleção de Formas dentro da Tela de Jogo
                if RETANGULO_JOGO.collidepoint(pos_mouse):
                    clicou_em_algo = False
                    for f in formas:
                        if f.checar_clique(pos_mouse):
                            forma_selecionada = f
                            clicou_em_algo = True
                            print(f"Forma do tipo '{f.tipo}' SELECIONADA!")
                            break
                    if not clicou_em_algo:
                        forma_selecionada = None
                        print("Nenhuma forma selecionada. Modo Global Ativado.")

        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                for s in sliders:
                    s.arrastando = False

    # Captura arrasto dos sliders
    for s in sliders:
        s.atualizar(pos_mouse)

    # ---------------------------------------------------------
    # PROCESSAMENTO DE LOGICA CONTEXTUAL (A regra de ouro pedida!)
    # ---------------------------------------------------------
    if forma_selecionada:
        # Modo Local: Os sliders alteram apenas a cor/propriedades da forma selecionada
        forma_selecionada.r = int(sliders[0].valor * 255)
        forma_selecionada.g = int(sliders[1].valor * 255)
        forma_selecionada.b = int(sliders[2].valor * 255)
        
        # Interação por teclado para a Abinha de Transformações Contextuais
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:   forma_selecionada.x -= 3   # Translação X-
        if teclas[pygame.K_RIGHT]:  forma_selecionada.x += 3   # Translação X+
        if teclas[pygame.K_UP]:     forma_selecionada.y -= 3   # Translação Y-
        if teclas[pygame.K_DOWN]:   forma_selecionada.y += 3   # Translação Y+
        if teclas[pygame.K_KP_PLUS] or teclas[pygame.K_EQUALS]: 
            forma_selecionada.tamanho = min(150, forma_selecionada.tamanho + 1) # Escala +
        if teclas[pygame.K_KP_MINUS] or teclas[pygame.K_MINUS]: 
            forma_selecionada.tamanho = max(20, forma_selecionada.tamanho - 1)  # Escala -
        if teclas[pygame.K_r]:      forma_selecionada.rotacao += 2  # Rotação Horária
        if teclas[pygame.K_e]:      forma_selecionada.rotacao -= 2  # Rotação Anti-horária
    else:
        # Modo Global: Se nenhuma forma estiver selecionada, as alterações
        # afetam a cena como um todo (será injetado nas matrizes OpenCV do frame aqui amanhã)
        pass

    # 5. RENDERIZAÇÃO GRÁFICA
    tela.fill(COR_FUNDO)

    # Camada 1: Desenhar o Cenário do Jogo (Formas)
    for f in formas:
        f.desenhar(tela, selecionada=(f == forma_selecionada))

    # Desenha o texto do objetivo/HUD superior de forma limpa
    txt_obj = FONTE_M_NEGRITO.render("Objetivo: Manipule a visão para revelar as estruturas ocultas", True, (200, 200, 200))
    tela.blit(txt_obj, (20, 15))

    # Camada 2: Desenhar o Painel Inferior da Interface (HUD do Tldraw)
    # Fundo do painel
    pygame.draw.rect(tela, (25, 25, 30), PANEL_CONTROLE)
    pygame.draw.rect(tela, (0, 128, 255), PANEL_CONTROLE, width=2) # Divisória azul neon

    # Linhas de separação das seções (Como as caixas do seu desenho)
    pygame.draw.line(tela, (50, 50, 60), (280, 400), (280, 600), width=2) # Separa LENS dos Sliders
    pygame.draw.line(tela, (50, 50, 60), (640, 400), (640, 600), width=2) # Separa Sliders do Histo

    # RENDERIZANDO A SEÇÃO LENS
    txt_lens = FONTE_M_NEGRITO.render("Lens", True, (0, 128, 255))
    tela.blit(txt_lens, (20, 410))
    for btn in botoes_lens:
        cor_btn = (0, 128, 255) if btn["ativo"] else ((60, 60, 70) if btn["rect"].collidepoint(pos_mouse) else (40, 40, 45))
        pygame.draw.rect(tela, cor_btn, btn["rect"], border_radius=4)
        pygame.draw.rect(tela, (100, 100, 120), btn["rect"], width=1, border_radius=4)
        
        # ID do filtro dentro do botão para guiar os testes
        txt_id = FONTE_P_NEGRITO.render(f"F{btn['id']}", True, (255, 255, 255))
        tela.blit(txt_id, (btn["rect"].x + 16, btn["rect"].y + 12))

    # RENDERIZANDO OS SLIDERS
    for s in sliders:
        s.desenhar(tela)

    # RENDERIZANDO O ESPAÇO DO HISTOGRAMA
    txt_hist = FONTE_M_NEGRITO.render("Histograma", True, (255, 255, 255))
    tela.blit(txt_hist, (650, 410))
    # Caixa interna preta onde o gráfico do OpenCV vai ser plotado
    pygame.draw.rect(tela, (10, 10, 12), (655, 440, 130, 120))
    pygame.draw.rect(tela, (60, 60, 70), (655, 440, 130, 120), width=1)

    # IF CONTEXTUAL: Se houver uma forma selecionada, mostra uma "abinha" de aviso de Transformação ativa
    if forma_selecionada:
        # Caixa de alerta contextual flutuando discretamente na HUD
        rect_aviso = pygame.Rect(480, 405, 140, 20)
        pygame.draw.rect(tela, (255, 215, 0), rect_aviso, border_radius=3)
        txt_aviso = FONTE_P_NEGRITO.render("Modo Objeto: Setas / R / E", True, (0, 0, 0))
        tela.blit(txt_aviso, (rect_aviso.x + 5, rect_aviso.y + 2))

    pygame.display.flip()
    relogio.tick(60)