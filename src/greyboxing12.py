import pygame
import random
import sys
import numpy as np
import cv2
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

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
pygame.display.set_caption("Greyboxing 12 - Integração de Filtros com Elementos 3D")
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
        self.r, self.g, self.b = random.randint(100, 255), random.randint(100, 200), random.randint(50, 150)
        
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

# 📐 MOTOR DE MODELAGEM TRIDIMENSIONAL MATEMÁTICO (Suporta Pirâmide e Cubo)
class Artefato3D:
    def __init__(self, tipo_modelo, x, y):
        self.tipo_modelo = tipo_modelo  # "piramide" ou "cubo"
        self.x = x
        self.y = y
        self.tamanho = 70
        self.angulo_rotacao = 0.0
        self.selecionado = False
        self.arrastando_para_girar = False
        
        # Modificadores de transformações geométricas
        self.escala = 1.0
        self.trans_x = 0
        self.trans_y = 0

    def restaurar_estado_original(self):
        """Devolve ao objeto 3D suas configurações de nascimento."""
        self.escala = 1.0
        self.trans_x = 0
        self.trans_y = 0
        self.angulo_rotacao = 0.0
        self.selecionado = False
        self.arrastando_para_girar = False

    def desenhar_projesao(self, superficie):
        cx, cy = self.x + self.trans_x, self.y + self.trans_y
        t = int(self.tamanho * self.escala)
        rad = np.radians(self.angulo_rotacao)
        
        if self.tipo_modelo == "piramide":
            vertices = []
            pontos_base = [(-t//2, -t//4), (t//2, -t//4), (t//2, t//4), (-t//2, t//4)]
            for px, py in pontos_base:
                rx = int(px * np.cos(rad) - py * np.sin(rad)) + cx
                ry = int(px * np.sin(rad) + py * np.cos(rad)) + cy
                vertices.append((rx, ry))
            topo = (cx, cy - int(t * 1.2))
            
            # Renderização das 4 faces preenchidas
            pygame.draw.polygon(superficie, (200, 150, 20), [vertices[0], vertices[1], topo])
            pygame.draw.polygon(superficie, (230, 180, 30), [vertices[1], vertices[2], topo])
            pygame.draw.polygon(superficie, (250, 210, 40), [vertices[2], vertices[3], topo])
            pygame.draw.polygon(superficie, (180, 130, 15), [vertices[3], vertices[0], topo])
            
            # Linhas de wireframe pretas para o Sobel detectar contornos
            for i in range(4):
                pygame.draw.line(superficie, (0, 0, 0), vertices[i], vertices[(i+1)%4], width=2)
                pygame.draw.line(superficie, (0, 0, 0), vertices[i], topo, width=2)
                
        elif self.tipo_modelo == "cubo":
            # Projeção de Perspectiva Isométrica de um Cubo 3D
            offset = t // 3
            v_front = [(cx-t//2, cy-t//2+offset), (cx+t//2, cy-t//2+offset), (cx+t//2, cy+t//2+offset), (cx-t//2, cy+t//2+offset)]
            v_back = [(cx-t//2+offset, cy-t//2), (cx+t//2+offset, cy-t//2), (cx+t//2+offset, cy+t//2), (cx-t//2+offset, cy+t//2)]
            
            # Rotaciona as duas tampas do cubo matematicamente no plano
            def rotacionar_pontos(lista_pts):
                pts_rot = []
                for px, py in lista_pts:
                    dx, dy = px - cx, py - cy
                    rx = int(dx * np.cos(rad) - dy * np.sin(rad)) + cx
                    ry = int(dx * np.sin(rad) + dy * np.cos(rad)) + cy
                    pts_rot.append((rx, ry))
                return pts_rot
                
            vf_r = rotacionar_pontos(v_front)
            vb_r = rotacionar_pontos(v_back)
            
            # Preenchimento das faces com variação harmônica de tons azuis/metálicos
            pygame.draw.polygon(superficie, (40, 100, 180), [vf_r[0], vf_r[1], vf_r[2], vf_r[3]]) # Frente
            pygame.draw.polygon(superficie, (60, 120, 210), [vf_r[0], vf_r[1], vb_r[1], vb_r[0]]) # Topo
            pygame.draw.polygon(superficie, (30, 80, 150), [vf_r[1], vf_r[2], vb_r[2], vb_r[1]]) # Direita
            pygame.draw.polygon(superficie, (50, 90, 170), [vf_r[3], vf_r[2], vb_r[2], vb_r[3]]) # Baixo
            
            # Wireframe estrutural preto
            for i in range(4):
                pygame.draw.line(superficie, (0, 0, 0), vf_r[i], vf_r[(i+1)%4], width=2)
                pygame.draw.line(superficie, (0, 0, 0), vb_r[i], vb_r[(i+1)%4], width=2)
                pygame.draw.line(superficie, (0, 0, 0), vf_r[i], vb_r[i], width=2)

        if self.selecionado:
            pygame.draw.circle(superficie, (0, 255, 255), (cx, cy), t + 15, width=2)

    def checar_clique(self, mouse_pos):
        cx, cy = self.x + self.trans_x, self.y + self.trans_y
        return ((cx - mouse_pos[0])**2 + (cy - mouse_pos[1])**2)**0.5 < (self.tamanho * self.escala)

# 🟢 REINSERÇÃO COMPLETA: Classe SliderHUD restaurada com sucesso!
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

formas = [FormaGeometrica(random.choice(["retangulo", "circulo", "triangulo"]), random.randint(150, 1100), random.randint(100, 380)) for _ in range(4)]
objeto_3d_cenario = Artefato3D("piramide", x=640, y=260) 
forma_selecionada = None
arrastando_forma_2d = False  

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
matriz_cena = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)

while True:
    pos_mouse = pygame.mouse.get_pos()
    matriz_cena = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:
                # Clique nos Sliders de HUD
                for s in sliders:
                    if s.rect_cursor.collidepoint(pos_mouse): s.arrastando = True
                
                # Clique no Histograma
                tom = histograma_cv.checar_clique(pos_mouse)
                if tom is not None:
                    print(f"Histograma: Tom de cor {tom} selecionado!")

                # Clique nos Filtros LENS
                for btn in botoes_lens:
                    if btn["rect"].collidepoint(pos_mouse):
                        if btn["id"] == 6:
                            btn["ativo"] = not btn["ativo"]
                            lupa_cv.ativo = btn["ativo"]
                        elif btn["id"] == 7:
                            btn["ativo"] = not btn["ativo"]
                            lupa_cv.invertida = btn["ativo"]
                        elif btn["id"] == 8:
                            nova_matriz = ins_img.selecionar_arquivo_background(LARGURA, ALTURA_JOGO)
                            if nova_matriz is not None:
                                matriz_fundo_original = nova_matriz
                        elif btn["id"] == 9: # Reset Total
                            fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0
                            for b in botoes_lens: b["ativo"] = False
                            lupa_cv.ativo = False
                            lupa_cv.invertida = False
                            histograma_cv.tom_selecionado = None
                            objeto_3d_cenario.restaurar_estado_original()
                            forma_selecionada = None
                            for f in formas: f.restaurar_estado_original()
                            for s in sliders:
                                s.valor = 0.5
                                s.rect_cursor.x = s.rect_linha.x + int(s.rect_linha.width * 0.5) - 6
                        else:
                            btn["ativo"] = not btn["ativo"]

                # Clique na Tela de Jogo (Seleção e Ativação do Arraste de Atores)
                if RETANGULO_JOGO.collidepoint(pos_mouse):
                    clicou_objeto = False
                    
                    # INTERAÇÃO MOUSE 3D: Ativa a rotação por movimento lateral
                    if objeto_3d_cenario.checar_clique(pos_mouse):
                        objeto_3d_cenario.selecionado = True
                        objeto_3d_cenario.arrastando_para_girar = True
                        forma_selecionada = None
                        clicou_objeto = True
                    else:
                        objeto_3d_cenario.selecionado = False
                        # INTERAÇÃO MOUSE 2D: Ativa o arraste de posição pelas coordenadas
                        for f in formas:
                            if f.checar_clique(pos_mouse):
                                forma_selecionada = f
                                arrastando_forma_2d = True
                                clicou_objeto = True
                                sliders[0].valor = f.r / 255
                                sliders[1].valor = f.g / 255
                                sliders[2].valor = f.b / 255
                                sliders[3].valor = (f.brilho + 100) / 200
                                sliders[4].valor = f.contraste / 2.0
                                sliders[5].valor = f.saturacao / 3.0
                                break
                                
                    if not clicou_objeto: 
                        forma_selecionada = None
                        objeto_3d_cenario.selecionado = False
                        sliders[0].valor = fator_global_r / 2.0
                        sliders[1].valor = fator_global_g / 2.0
                        sliders[2].valor = fator_global_b / 2.0

        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                for s in sliders: s.arrastando = False
                if objeto_3d_cenario: objeto_3d_cenario.arrastando_para_girar = False
                arrastando_forma_2d = False
                
        if evento.type == MOUSEMOTION:
            # Gira o modelo 3D proporcionalmente ao deslocamento relativo em X
            if objeto_3d_cenario.selecionado and objeto_3d_cenario.arrastando_para_girar:
                objeto_3d_cenario.angulo_rotacao += evento.rel[0] * 1.5
                
            # Translaça o ator 2D seguindo o vetor dinâmico do mouse
            elif forma_selecionada and arrastando_forma_2d:
                forma_selecionada.x += evento.rel[0]
                forma_selecionada.y += evento.rel[1]
                forma_selecionada.x = max(20, min(forma_selecionada.x, LARGURA - 20))
                forma_selecionada.y = max(20, min(forma_selecionada.y, ALTURA_JOGO - 20))

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_z: # Reset Total com Logs
                matriz_antes_reset = matriz_cena.copy()
                forma_selecionada = None
                lupa_cv.ativo = False
                lupa_cv.invertida = False
                fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0
                objeto_3d_cenario.restaurar_estado_original()
                
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
                objeto_3d_cenario.restaurar_estado_original()
                # Tecla X sorteia o novo modelo geométrico no centro
                objeto_3d_cenario.tipo_modelo = random.choice(["piramide", "cubo"])
                
                shapes_pool = ["retangulo", "circulo", "triangulo"]
                formas.clear()
                for _ in range(random.randint(4, 6)):
                    formas.append(FormaGeometrica(random.choice(shapes_pool), random.randint(150, 1100), random.randint(100, 380)))
                print(f"Debug: Laboratório alterado. Modelo 3D ativo: {objeto_3d_cenario.tipo_modelo.upper()}")

    histograma_cv.atualizar_arraste(pos_mouse, pygame.mouse.get_pressed())
    for s in sliders: s.atualizar(pos_mouse)

    # Teclado de comando contínuo
    teclas = pygame.key.get_pressed()
    if objeto_3d_cenario.selecionado:
        if teclas[pygame.K_LEFT]:  objeto_3d_cenario.trans_x -= 4
        if teclas[pygame.K_RIGHT]: objeto_3d_cenario.trans_x += 4
        if teclas[pygame.K_UP]:    objeto_3d_cenario.trans_y -= 4
        if teclas[pygame.K_DOWN]:  objeto_3d_cenario.trans_y += 4
        if teclas[pygame.K_q]:     objeto_3d_cenario.angulo_rotacao += 3.0
        if teclas[pygame.K_e]:     objeto_3d_cenario.angulo_rotacao -= 3.0
        if teclas[pygame.K_r]:     objeto_3d_cenario.escala = min(3.0, objeto_3d_cenario.escala + 0.03)
        if teclas[pygame.K_t]:     objeto_3d_cenario.escala = max(0.4, objeto_3d_cenario.escala - 0.03)
    elif forma_selecionada:
        forma_selecionada.r = int(sliders[0].valor * 255)
        forma_selecionada.g = int(sliders[1].valor * 255)
        forma_selecionada.b = int(sliders[2].valor * 255)
        forma_selecionada.brilho = int((sliders[3].valor - 0.5) * 200)
        forma_selecionada.contraste = float(sliders[4].valor * 2.0)
        forma_selecionada.saturacao = float(sliders[5].valor * 3.0)
        
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

    # -------------------------------------------------------------------------
    # 🧱 PIPELINE DE RENDERIZAÇÃO UNIFICADO (PRE-PROCESSAMENTO)
    # -------------------------------------------------------------------------
    surf_estagio = pygame.Surface((LARGURA, ALTURA_JOGO))
    if matriz_fundo_original is not None:
        surf_fundo = ins_img.converter_matriz_para_surface(matriz_fundo_original)
        if surf_fundo: surf_estagio.blit(surf_fundo, (0, 0))
    else:
        surf_estagio.fill(COR_FUNDO)

    for f in formas:
        f.desenhar(surf_estagio, selecionada=(f == forma_selecionada))

    objeto_3d_cenario.desenhar_projesao(surf_estagio)

    textura_jogo = pygame.surfarray.array3d(surf_estagio)
    matriz_jogo = np.transpose(textura_jogo, (1, 0, 2))
    matriz_cena = cv2.cvtColor(matriz_jogo, cv2.COLOR_RGB2BGR)

    # ---------------------------------------------------------
    # PROCESSAMENTO DE FILTROS OPENCV NA CENA INTEGRADA
    # ---------------------------------------------------------
    if not forma_selecionada and not objeto_3d_cenario.selecionado:
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

    if not forma_selecionada and not objeto_3d_cenario.selecionado:
        glb_brilho = int((sliders[3].valor - 0.5) * 200)
        glb_contraste = float(sliders[4].valor * 2.0)
        glb_saturacao = float(sliders[5].valor * 3.0)
        matriz_cena = pdi.ajustar_brilho_contraste_saturação(matriz_cena, glb_brilho, glb_contraste, glb_saturacao) if hasattr(pdi, 'ajustar_brilho_contrast_saturação') else pdi.ajustar_brilho_contraste_saturação(matriz_cena, glb_brilho, glb_contraste, glb_saturacao)

    # Aplicação contínua tridimensional de canais do Histograma 2D
    if histograma_cv.tom_selecionado is not None and histograma_cv.canal_ativo is not None and not forma_selecionada:
        tom_alvo = histograma_cv.tom_selecionado
        ganho_vertical = histograma_cv.fator_escala
        idx_canal = histograma_cv.canal_ativo
        tolerancia = 20
        
        matriz_cena = matriz_cena.astype(np.float32)
        canal_selecionado = matriz_cena[:, :, idx_canal]
        mascara_frequencia = (canal_selecionado >= tom_alvo - tolerancia) & (canal_selecionado <= tom_alvo + tolerancia)
        
        matriz_cena[:, :, idx_canal] = np.where(mascara_frequencia, matriz_cena[:, :, idx_canal] * ganho_vertical, matriz_cena[:, :, idx_canal])
        matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)

    # Exibe o frame final tratado pelo OpenCV
    surface_render = ins_img.converter_matriz_para_surface(matriz_cena)
    if surface_render: tela.blit(surface_render, (0, 0))

    lupa_cv.desenhar_contorno_hud(tela, pos_mouse, ALTURA_JOGO)
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

    # HUD 1: Seção LENS
    tela.blit(FONTE_M.render("LENS (Filtros & Ruídos)", True, (0, 128, 255)), (20, 495))
    for btn in botoes_lens:
        cor = (0, 128, 255) if btn["ativo"] else ((70, 70, 80) if btn["rect"].collidepoint(pos_mouse) else (40, 40, 45))
        if btn["id"] == 7 and lupa_cv.invertida: cor = (255, 120, 0)
        pygame.draw.rect(tela, cor, btn["rect"], border_radius=4)
        pygame.draw.rect(tela, (90, 90, 100), btn["rect"], width=1, border_radius=4)
        txt_n = FONTE_P.render(btn["nome"][:8], True, (255, 255, 255))
        tela.blit(txt_n, (btn["rect"].x + 6, btn["rect"].y + 15))

    # HUD 2: Seção SLIDERS
    titulo_sliders = "Ajustes de Objeto Ativos" if (forma_selecionada or objeto_3d_cenario.selecionado) else "Ajustes Globais da Cena"
    cor_titulo = (0, 255, 255) if objeto_3d_cenario.selecionado else ((255, 215, 0) if forma_selecionada else (255, 255, 255))
    tela.blit(FONTE_M.render(titulo_sliders, True, cor_titulo), (370, 495))
    for s in sliders: s.desenhar(tela)

    # HUD 3: Seção TRANSFORMAÇÕES
    tela.blit(FONTE_M.render("Transformações", True, (255, 215, 0)), (820, 495))
    if forma_selecionada or objeto_3d_cenario.selecionado:
        tela.blit(FONTE_P.render("⟳ Rotação: Teclas Q <- -> E", True, (230, 230, 230)), (820, 540))
        tela.blit(FONTE_P.render("⮂ Translação: Setas do Teclado", True, (230, 230, 230)), (820, 580))
        tela.blit(FONTE_P.render("⇲ Escala: Teclas R (+) e T (-)", True, (230, 230, 230)), (820, 620))
    else:
        tela.blit(FONTE_P.render("Selecione um objeto para", True, (120, 120, 120)), (820, 550))
        tela.blit(FONTE_P.render("liberar transformações.", True, (120, 120, 120)), (820, 570))

    # HUD 4: Seção HISTOGRAMA 2D
    tela.blit(FONTE_M.render("Histograma", True, (255, 255, 255)), (1070, 495))
    histograma_cv.calcular_e_desenhar(tela, matriz_cena)

    pygame.display.flip()
    relogio.tick(60)