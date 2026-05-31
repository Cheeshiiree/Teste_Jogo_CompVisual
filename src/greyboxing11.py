import pygame
import random
import sys
import numpy as np
import cv2
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP

# IMPORTAÇÃO DOS NOSSOS MOTORES MODULARIZADOS
import processamento_imagem as pdi
import filtro_local as fl
import histograma as hst
import logger_pdi as logg
import inserir_imagens as ins_img

pygame.init()
pygame.font.init()

# RESOLUÇÃO EXPANDIDA (Padrão HD do Projeto)
LARGURA, ALTURA = 1280, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 11 - Manipulação do histograma e filtros locais")
relogio = pygame.time.Clock()

FONTE_P = pygame.font.SysFont("Arial", 13, bold=True)
FONTE_M = pygame.font.SysFont("Arial", 16, bold=True)

# Definição das Regiões do Layout
ALTURA_JOGO = 480
RETANGULO_JOGO = pygame.Rect(0, 0, LARGURA, ALTURA_JOGO)
PANEL_CONTROLE = pygame.Rect(0, ALTURA_JOGO, LARGURA, ALTURA - ALTURA_JOGO)

# Instancia os módulos customizados
lupa_cv = fl.LupaFiltro(raio=90)
histograma_cv = hst.HistogramaInterativo(x=1065, y=535, largura=200, altura=130)

COR_FUNDO = (20, 20, 22)

# 🌅 CARREGAMENTO AUTOMÁTICO DO CENÁRIO PADRÃO (Classroom 11)
caminho_padrao = "assets/sprites/misc/Classroom 11.png"
matriz_fundo_original = ins_img.carregar_background_pdi(caminho_padrao, LARGURA, ALTURA_JOGO)

class FormaGeometrica:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x, self.y = x, y
        self.tamanho = random.randint(60, 90)
        self.rotacao = 0
        self.r, self.g, self.b = random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)
        
        # Modificadores Locais de Efeito OpenCV
        self.brilho = 0
        self.contraste = 1.0
        self.saturacao = 1.0

        # BACKUP DE SEGURANÇA (Para o Reset com 'Z')
        self.orig_x = x
        self.orig_y = y
        self.orig_tamanho = self.tamanho
        self.orig_r = self.r
        self.orig_g = self.g
        self.orig_b = self.b

    def restaurar_estado_original(self):
        """Devolve ao objeto suas características iniciais de cor, posição e escala."""
        self.x = self.orig_x
        self.y = self.orig_y
        self.tamanho = self.orig_tamanho
        self.r = self.orig_r
        self.g = self.orig_g
        self.b = self.orig_b
        self.rotacao = 0
        self.brilho = 0
        self.contraste = 1.0
        self.saturacao = 1.0

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

        # Se houver modificadores locais de objeto ativo, processa individualmente
        if selecionada and (self.brilho != 0 or self.contraste != 1.0 or self.saturacao != 1.0):
            array_objeto = pygame.surfarray.array3d(surf)
            matriz_obj = np.transpose(array_objeto, (1, 0, 2))
            matriz_obj_bgr = cv2.cvtColor(matriz_obj, cv2.COLOR_RGBA2BGR)
            matriz_obj_bgr = pdi.ajustar_brilho_contraste_saturação(matriz_obj_bgr, self.brilho, self.contraste, self.saturacao)
            obj_rgb = cv2.cvtColor(matriz_obj_bgr, cv2.COLOR_BGR2RGB)
            array_final_obj = np.transpose(obj_rgb, (1, 0, 2))
            
            surf_filtrada = pygame.surfarray.make_surface(array_final_obj)
            surf_alpha = surf.copy()
            surf_alpha.blit(surf_filtrada, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf = surf_alpha

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

formas = [FormaGeometrica(random.choice(["retangulo", "circulo", "triangulo"]), random.randint(150, 1100), random.randint(100, 380)) for _ in range(5)]
forma_selecionada = None

sliders = [
    SliderHUD("Red", 380, 530, 160, cor_linha=(255, 50, 50)),
    SliderHUD("Green", 380, 590, 160, cor_linha=(50, 255, 50)),
    SliderHUD("Blue", 380, 650, 160, cor_linha=(50, 50, 255)),
    SliderHUD("Brilho", 580, 530, 160),
    SliderHUD("Contraste", 580, 590, 160),
    SliderHUD("Saturação", 580, 650, 160)
]

nomes_filtros = ["Cinza", "Sobel", "Desfocar", "S&P", "Mediana", "Inverter", "Modo Lupa", "Inv Lupa", "Img Fundo", "Reset"]
botoes_lens = []
for i, nome in enumerate(nomes_filtros):
    col, lin = i % 4, i // 4
    bx = 20 + (col * 80)
    by = 530 + (lin * 60)
    botoes_lens.append({"id": i, "nome": nome, "rect": pygame.Rect(bx, by, 72, 45), "ativo": False})

fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0

# ---------------------------------------------------------
# LOOP PRINCIPAL DO JOGO
# ---------------------------------------------------------
while True:
    pos_mouse = pygame.mouse.get_pos()

    # Blindagem inicial de escopo exigida pelo analisador Pylance
    matriz_cena = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:
                # 1. Clique nos Sliders
                for s in sliders:
                    if s.rect_cursor.collidepoint(pos_mouse): s.arrastando = True
                
                # 2. Clique no Histograma
                tom = histograma_cv.checar_clique(pos_mouse)
                if tom is not None:
                    print(f"Histograma: Tom de cor {tom} selecionado!")

                # 3. Clique nos Filtros da Seção LENS
                for btn in botoes_lens:
                    if btn["rect"].collidepoint(pos_mouse):
                        if btn["id"] == 6:
                            btn["ativo"] = not btn["ativo"]
                            lupa_cv.ativo = btn["ativo"]
                        elif btn["id"] == 7:
                            btn["ativo"] = not btn["ativo"]
                            lupa_cv.invertida = btn["ativo"]
                        elif btn["id"] == 8: # Inserir Imagem Dinâmica
                            nova_matriz = ins_img.selecionar_arquivo_background(LARGURA, ALTURA_JOGO)
                            if nova_matriz is not None:
                                matriz_fundo_original = nova_matriz
                        elif btn["id"] == 9: # Botão Reset HUD
                            fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0
                            for b in botoes_lens: b["ativo"] = False
                            lupa_cv.ativo = False
                            lupa_cv.invertida = False
                            histograma_cv.tom_selecionado = None
                            for f in formas: f.restaurar_estado_original()
                            for s in sliders:
                                s.valor = 0.5
                                s.rect_cursor.x = s.rect_linha.x + int(s.rect_linha.width * 0.5) - 6
                        else:
                            btn["ativo"] = not btn["ativo"]

                if RETANGULO_JOGO.collidepoint(pos_mouse):
                    clicou_forma = False
                    for f in formas:
                        if f.checar_clique(pos_mouse):
                            forma_selecionada = f
                            clicou_forma = True
                            sliders[0].valor = f.r / 255
                            sliders[1].valor = f.g / 255
                            sliders[2].valor = f.b / 255
                            sliders[3].valor = (f.brilho + 100) / 200
                            sliders[4].valor = f.contraste / 2.0
                            sliders[5].valor = f.saturacao / 3.0
                            break
                    if not clicou_forma: 
                        forma_selecionada = None
                        sliders[0].valor = fator_global_r / 2.0
                        sliders[1].valor = fator_global_g / 2.0
                        sliders[2].valor = fator_global_b / 2.0

        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                for s in sliders: s.arrastando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_z: # Reset Total e exportação de logs
                matriz_antes_reset = matriz_cena.copy()
                forma_selecionada = None
                lupa_cv.ativo = False
                lupa_cv.invertida = False
                fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0
                
                for f in formas: f.restaurar_estado_original()
                for s in sliders: 
                    s.valor = 0.5
                    s.rect_cursor.x = s.rect_linha.x + int(s.rect_linha.width * 0.5) - 6
                for btn in botoes_lens: btn["ativo"] = False
                
                if matriz_fundo_original is not None:
                    matriz_depois_reset = matriz_fundo_original.copy()
                else:
                    matriz_depois_reset = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)
                    matriz_depois_reset[:, :] = COR_FUNDO
                
                logg.salvar_log_experimento("RESET_LABORATORIO_Z", matriz_antes_reset, matriz_depois_reset, histograma_cv.tom_selecionado, sliders)
                histograma_cv.tom_selecionado = None

            if evento.key == pygame.K_x:
                forma_selecionada = None
                formas.clear()
                for _ in range(random.randint(4, 7)):
                    formas.append(FormaGeometrica(random.choice(["retangulo", "circulo", "triangulo"]), random.randint(150, 1100), random.randint(100, 380)))

    # 🟢 ADICIONE ESTA LINHA AQUI (Logo após o fechamento do 'for evento in pygame.event.get():')
    # Ela passa a posição do mouse e quais botões estão pressionados para o histograma atualizar o arraste!
    histograma_cv.atualizar_arraste(pos_mouse, pygame.mouse.get_pressed())

    for s in sliders: s.atualizar(pos_mouse)

    if forma_selecionada:
        forma_selecionada.r = int(sliders[0].valor * 255)
        forma_selecionada.g = int(sliders[1].valor * 255)
        forma_selecionada.b = int(sliders[2].valor * 255)
        forma_selecionada.brilho = int((sliders[3].valor - 0.5) * 200)
        forma_selecionada.contraste = float(sliders[4].valor * 2.0)
        forma_selecionada.saturacao = float(sliders[5].valor * 3.0)
        
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:  forma_selecionada.x -= 4
        if teclas[pygame.K_RIGHT]: forma_selecionada.x += 4
        if teclas[pygame.K_UP]:    forma_selecionada.y -= 4
        if teclas[pygame.K_DOWN]:  forma_selecionada.y += 4
        if teclas[pygame.K_q]:     forma_selecionada.rotacao += 3
        if teclas[pygame.K_e]:     forma_selecionada.rotacao -= 3
        if teclas[pygame.K_r]:     forma_selecionada.tamanho = min(200, forma_selecionada.tamanho + 2)
        if teclas[pygame.K_t]:     forma_selecionada.tamanho = max(30, forma_selecionada.tamanho - 2)
    else:
        fator_global_r = float(sliders[0].valor * 2.0)
        fator_global_g = float(sliders[1].valor * 2.0)
        fator_global_b = float(sliders[2].valor * 2.0)

    # ---------------------------------------------------------
    # 🧱 O PULO DO GATO: PIPELINE UNIFICADO DE PROCESSAMENTO (PDI)
    # ---------------------------------------------------------
    # 1. Monta o plano de fundo inicial na janela temporária do Pygame
    surf_estagio = pygame.Surface((LARGURA, ALTURA_JOGO))
    if matriz_fundo_original is not None:
        surf_fundo = ins_img.converter_matriz_para_surface(matriz_fundo_original)
        if surf_fundo:
            surf_estagio.blit(surf_fundo, (0, 0))
    else:
        surf_estagio.fill(COR_FUNDO)

    # 2. Renderiza os blocos geométricos por cima do fundo ANTES de capturar para o OpenCV
    for f in formas:
        f.desenhar(surf_estagio, selecionada=(f == forma_selecionada))

    # 3. CAPTURA DO BUFFER COMBINADO: Envia o bloco completo (Cenário + Atores) para as matrizes
    textura_jogo = pygame.surfarray.array3d(surf_estagio)
    matriz_jogo = np.transpose(textura_jogo, (1, 0, 2))
    matriz_cena = cv2.cvtColor(matriz_jogo, cv2.COLOR_RGB2BGR)

    # 4. APLICAÇÃO DOS FILTROS ACADÊMICOS DIRETAMENTE NA MATRIZ INTEGRADA
    if not forma_selecionada:
        matriz_cena = matriz_cena.astype(np.float32)
        matriz_cena[:, :, 0] *= fator_global_b
        matriz_cena[:, :, 1] *= fator_global_g
        matriz_cena[:, :, 2] *= fator_global_r
        matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)

    if lupa_cv.ativo:
        matriz_cena = lupa_cv.aplicar_lente_local(matriz_cena, pos_mouse, botoes_lens)
    else:
        if botoes_lens[0]["ativo"]: matriz_cena = pdi.aplicar_escala_cinza(matriz_cena)
        if botoes_lens[1]["ativo"]: matriz_cena = pdi.aplicar_sobel(matriz_cena)
        if botoes_lens[2]["ativo"]: matriz_cena = pdi.aplicar_blur(matriz_cena)
        if botoes_lens[3]["ativo"]: matriz_cena = pdi.injetar_ruido_salt_pepper(matriz_cena)
        if botoes_lens[4]["ativo"]: matriz_cena = pdi.aplicar_filtro_mediana(matriz_cena)
        if botoes_lens[5]["ativo"]: matriz_cena = cv2.bitwise_not(matriz_cena)

    if not forma_selecionada:
        glb_brilho = int((sliders[3].valor - 0.5) * 200)
        glb_contraste = float(sliders[4].valor * 2.0)
        glb_saturacao = float(sliders[5].valor * 3.0)
        matriz_cena = pdi.ajustar_brilho_contraste_saturação(matriz_cena, glb_brilho, glb_contraste, glb_saturacao)

    # -------------------------------------------------------------------------
    # 📊 REAÇÃO DA SELEÇÃO 2D DO HISTOGRAMA NA CENA GLOBAL (Novo!)
    # -------------------------------------------------------------------------
    if histograma_cv.tom_selecionado is not None and not forma_selecionada:
        tom_alvo = histograma_cv.tom_selecionado
        ganho = histograma_cv.fator_escala
        
        # Para evitar uma quebra brusca de cor, criamos uma máscara de tolerância.
        # Todos os pixels cujo tom esteja a +- 15 valores do alvo vão sofrer o efeito.
        tolerancia = 15
        
        # Converte temporariamente para float para não estourar o limite de 255 do uint8
        matriz_cena = matriz_cena.astype(np.float32)
        
        # Cria a máscara booleana: onde os pixels da imagem estão próximos do tom escolhido
        # Buscamos a média dos 3 canais BGR para avaliar o tom geral do pixel
        tom_atual_pixels = np.mean(matriz_cena, axis=2)
        mascara_tons = (tom_atual_pixels >= tom_alvo - tolerancia) & (tom_atual_pixels <= tom_alvo + tolerancia)
        
        # Aplica a multiplicação do ganho vertical apenas nos pixels da máscara!
        matriz_cena[mascara_tons] *= ganho
        
        # Trava os valores entre 0 e 255 e volta para o formato de imagem padrão
        matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)
    # -------------------------------------------------------------------------

    # Devolve o frame tratado pelo OpenCV para o Pygame de forma correta
    surface_render = ins_img.converter_matriz_para_surface(matriz_cena)

    # 5. EXIBIÇÃO: Converte a matriz final processada e joga na janela de exibição do Pygame
    surface_render = ins_img.converter_matriz_para_surface(matriz_cena)
    if surface_render:
        tela.blit(surface_render, (0, 0))

    # Desenha o anel sutil da lente circular por cima de tudo
    lupa_cv.desenhar_contorno_hud(tela, pos_mouse, ALTURA_JOGO)

    # 📝 CAMADA DO TEXTO DO OBJETIVO (Fica fixo por cima do jogo com efeito de sombra)
    txt_sombra = FONTE_M.render("Objetivo: Teste dos filtros e as transformações geométricas nos objetos", True, (0, 0, 0))
    txt_obj = FONTE_M.render("Objetivo: Teste dos filtros e as transformações geométricas nos objetos", True, (255, 255, 255))
    tela.blit(txt_sombra, (21, 21))
    tela.blit(txt_obj, (20, 20))

    # ---------------------------------------------------------
    # PAINEL DE CONTROLE DA INTERFACE (HUD FIXA)
    # ---------------------------------------------------------
    pygame.draw.rect(tela, (24, 24, 27), PANEL_CONTROLE)
    pygame.draw.rect(tela, (0, 128, 255), PANEL_CONTROLE, width=2)
    pygame.draw.line(tela, (50, 50, 60), (350, ALTURA_JOGO), (350, ALTURA), width=2)
    pygame.draw.line(tela, (50, 50, 60), (800, ALTURA_JOGO), (800, ALTURA), width=2)
    pygame.draw.line(tela, (50, 50, 60), (1050, ALTURA_JOGO), (1050, ALTURA), width=2)

    # HUD Quadrante 1: Filtros da LENS
    tela.blit(FONTE_M.render("LENS (Filtros & Ruídos)", True, (0, 128, 255)), (20, 495))
    for btn in botoes_lens:
        cor = (0, 128, 255) if btn["ativo"] else ((70, 70, 80) if btn["rect"].collidepoint(pos_mouse) else (40, 40, 45))
        if btn["id"] == 7 and lupa_cv.invertida: cor = (255, 120, 0)
        pygame.draw.rect(tela, cor, btn["rect"], border_radius=4)
        pygame.draw.rect(tela, (90, 90, 100), btn["rect"], width=1, border_radius=4)
        txt_n = FONTE_P.render(btn["nome"][:8], True, (255, 255, 255))
        tela.blit(txt_n, (btn["rect"].x + 6, btn["rect"].y + 15))

    # HUD Quadrante 2: Barras dos Sliders
    titulo_sliders = "Ajustes de Objeto Ativos" if forma_selecionada else "Ajustes Globais da Cena"
    cor_titulo = (255, 215, 0) if forma_selecionada else (255, 255, 255)
    tela.blit(FONTE_M.render(titulo_sliders, True, cor_titulo), (370, 495))
    for s in sliders: s.desenhar(tela)

    # HUD Quadrante 3: Instruções das Transformações
    tela.blit(FONTE_M.render("Transformações", True, (255, 215, 0)), (820, 495))
    if forma_selecionada:
        tela.blit(FONTE_P.render("⟳ Rotação: Teclas Q <- -> E", True, (230, 230, 230)), (820, 540))
        tela.blit(FONTE_P.render("⮂ Translação: Setas do Teclado", True, (230, 230, 230)), (820, 580))
        tela.blit(FONTE_P.render("⇲ Escala: Teclas R (+) e T (-)", True, (230, 230, 230)), (820, 620))
    else:
        tela.blit(FONTE_P.render("Selecione um objeto para", True, (120, 120, 120)), (820, 550))
        tela.blit(FONTE_P.render("liberar transformações.", True, (120, 120, 120)), (820, 570))

    # HUD Quadrante 4: Gráfico do Histograma Real
    tela.blit(FONTE_M.render("Histograma", True, (255, 255, 255)), (1070, 495))
    histograma_cv.calcular_e_desenhar(tela, matriz_cena)

    pygame.display.flip()
    relogio.tick(60)

    #Ainda não implementado: Exportação de logs detalhados para análise posterior (histogramas, matrizes antes/depois, etc.)
    # Ainda não funciona escolher uma imagem mas na imagem padrão funciona normalmente
    # Não esquecer de corrigir o reset do botão para só voltar os sliders e filtros, sem resetar a posição e rotação dos objetos geométricos (deixar só o reset total com 'Z' para isso)
    # E não esquecer de trocar a camada do texto do objetivo para ficar por baixo dos filtros para poder testar os filtros no texto tambem igual estava anteriormente.