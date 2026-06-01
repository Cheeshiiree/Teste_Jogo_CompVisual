import pygame
import random
import sys
import numpy as np
import cv2
import time
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION

# IMPORTAÇÃO DOS NOSSOS MOTORES MODULARIZADOS
import processamento_imagem as pdi
import filtro_local as fl
import histograma as hst
import logger_pdi as logg
import inserir_imagens as ins_img
import sobel_manual as sm
import ui  # Importa o painel UI 

pygame.init()
pygame.font.init()

# RESOLUÇÃO 
LARGURA, ALTURA = 1280, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Laboratório de Computação Visual")
relogio = pygame.time.Clock()

FONTE_P = pygame.font.SysFont("Arial", 13, bold=True)
FONTE_M = pygame.font.SysFont("Arial", 16, bold=True)

# -------------------------------------------------------------------------
#  CONFIGURAÇÃO DOS ÍCONES DA JANELA E BARRA DE TAREFAS
# -------------------------------------------------------------------------
try:
    caminho_icone = "assets/sprites/misc/icon_janela.png"
    surf_icone = pygame.image.load(caminho_icone)
    pygame.display.set_icon(surf_icone) # Acopla o ícone na barra do Windows
    print("Sucesso: Ícones de identificação acoplados à barra de tarefas!")
except Exception as e:
    print(f"Aviso: Não foi possível carregar os ícones customizados. Erro: {e}")

# Definição das Regiões do Layout
ALTURA_JOGO = 480
RETANGULO_JOGO = pygame.Rect(0, 0, LARGURA, ALTURA_JOGO)
PANEL_CONTROLE = pygame.Rect(0, ALTURA_JOGO, LARGURA, ALTURA - ALTURA_JOGO)

# Instancia os módulos customizados
lupa_cv = fl.LupaFiltro(raio=90)
histograma_cv = hst.HistogramaInterativo(x=1065, y=535, largura=200, altura=130)
gerenciador_menu = ui.MenuUI(LARGURA, ALTURA)

COR_FUNDO = (20, 20, 22)

# CARREGAMENTO AUTOMÁTICO DO CENÁRIO PADRÃO (Classroom 11)
caminho_padrao = "assets/sprites/misc/Classroom 11.png"
matriz_fundo_original = ins_img.carregar_background_pdi(caminho_padrao, LARGURA, ALTURA_JOGO)

# -------------------------------------------------------------------------
#  EXECUÇÃO DA SPLASH SCREEN INICIAL (Abre por 3 segundos antes do Menu)
# -------------------------------------------------------------------------
try:
    caminho_splash = "assets/sprites/misc/splash_logo.png"
    img_splash = pygame.image.load(caminho_splash)
    # Redimensiona a imagem para cobrir a tela HD inteira se necessário
    img_splash = pygame.transform.smoothscale(img_splash, (LARGURA, ALTURA))
    
    # Exibe a imagem de abertura na tela
    tela.blit(img_splash, (0, 0))
    pygame.display.flip()
    print("Splash Screen: Carregando motores gráficos e de processamento de imagens...")
    time.sleep(3.0) # Segura o logotipo na tela por 3 segundos exatos
except Exception as e:
    print(f"Aviso: Splash Screen pulada. Imagem ausente ou corrompida. Detalhes: {e}")
# -------------------------------------------------------------------------

class FormaGeometrica:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x, self.y = x, y
        self.tamanho = random.randint(60, 90)
        self.rotacao = 0
        self.r, self.g, self.b = random.randint(100, 255), random.randint(100, 200), random.randint(50, 150)
        
        self.brilho = 0
        self.contraste = 1.0
        self.saturacao = 1.0

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


class Artefato3D:
    def __init__(self, tipo_modelo, x, y):
        self.tipo_modelo = tipo_modelo  
        self.x = x
        self.y = y
        self.tamanho = 70
        self.selecionado = False
        self.arrastando_para_girar = False
        
        self.rot_x = 25.0
        self.rot_y = -35.0
        
        self.escala = 1.0
        self.trans_x = 0
        self.trans_y = 0

        self.r, self.g, self.b = 230, 180, 30  
        self.brilho = 0
        self.contraste = 1.0
        self.saturacao = 1.0

    def restaurar_estado_original(self):
        self.escala = 1.0
        self.trans_x = 0
        self.trans_y = 0
        self.rot_x = 25.0
        self.rot_y = -35.0
        self.selecionado = False
        self.arrastando_para_girar = False
        self.r, self.g, self.b = 230, 180, 30
        self.brilho = 0
        self.contraste = 1.0
        self.saturacao = 1.0

    def transformar_e_rotacionar_3d(self, px, py, pz):
        rad_x = np.radians(self.rot_x)
        rad_y = np.radians(self.rot_y)
        
        y1 = py * np.cos(rad_x) - pz * np.sin(rad_x)
        z1 = py * np.sin(rad_x) + pz * np.cos(rad_x)
        
        x2 = px * np.cos(rad_y) + z1 * np.sin(rad_y)
        z2 = -px * np.sin(rad_y) + z1 * np.cos(rad_y)
        
        return x2, y1, z2

    def desenhar_projesao(self, superficie):
        cx, cy = self.x + self.trans_x, self.y + self.trans_y
        t = self.tamanho
        
        v_rot = []
        faces = []
        
        if self.tipo_modelo == "piramide":
            pts = [(-t, t, -t), (t, t, -t), (t, t, t), (-t, t, t), (0, -t, 0)]
            v_rot = [self.transformar_e_rotacionar_3d(p[0], p[1], p[2]) for p in pts]
            faces = [
                ([0, 1, 4], 0.8), ([1, 2, 4], 1.0), 
                ([2, 3, 4], 1.1), ([3, 0, 4], 0.6),
                ([0, 1, 2, 3], 0.5) 
            ]
        elif self.tipo_modelo == "cubo":
            pts = [(-t, -t, -t), (t, -t, -t), (t, t, -t), (-t, t, -t),
                   (-t, -t, t), (t, -t, t), (t, t, t), (-t, t, t)]
            v_rot = [self.transformar_e_rotacionar_3d(p[0], p[1], p[2]) for p in pts]
            faces = [
                ([0, 1, 2, 3], 1.0), ([4, 5, 6, 7], 0.8), 
                ([0, 1, 5, 4], 1.1), ([3, 2, 6, 7], 0.7), 
                ([0, 3, 7, 4], 0.6), ([1, 2, 6, 5], 0.9)  
            ]
        elif self.tipo_modelo == "prisma":
            pts = [(-t, t, -t), (t, t, -t), (0, -t, -t),
                   (-t, t, t), (t, t, t), (0, -t, t)]
            v_rot = [self.transformar_e_rotacionar_3d(p[0], p[1], p[2]) for p in pts]
            faces = [
                ([0, 1, 2], 1.0), ([3, 4, 5], 0.8), 
                ([0, 1, 4, 3], 1.1), ([1, 2, 5, 4], 0.7), ([2, 0, 3, 5], 0.6) 
            ]
        elif self.tipo_modelo == "octaedro":
            pts = [(-t, 0, -t), (t, 0, -t), (t, 0, t), (-t, 0, t), (0, -int(t*1.4), 0), (0, int(t*1.4), 0)]
            v_rot = [self.transformar_e_rotacionar_3d(p[0], p[1], p[2]) for p in pts]
            faces = [
                ([0, 1, 4], 1.0), ([1, 2, 4], 1.1), ([2, 3, 4], 0.9), ([3, 0, 4], 0.8), 
                ([0, 1, 5], 0.7), ([1, 2, 5], 0.8), ([2, 3, 5], 0.6), ([3, 0, 5], 0.5)  
            ]
        elif self.tipo_modelo == "cristal":
            pts = [(-int(t*0.7), 0, -int(t*0.7)), (int(t*0.7), 0, -int(t*0.7)), (int(t*0.7), 0, int(t*0.7)), (-int(t*0.7), 0, int(t*0.7)),
                   (0, -int(t*1.5), 0), (0, int(t*1.5), 0)]
            v_rot = [self.transformar_e_rotacionar_3d(p[0], p[1], p[2]) for p in pts]
            faces = [
                ([0, 1, 4], 1.1), ([1, 2, 4], 1.2), ([2, 3, 4], 0.9), ([3, 0, 4], 0.8),
                ([0, 1, 5], 0.6), ([1, 2, 5], 0.7), ([2, 3, 5], 0.5), ([3, 0, 5], 0.4)
            ]

        lista_ordenada = []
        for indices, sombreamento in faces:
            z_medio = np.mean([v_rot[idx][2] for idx in indices])
            lista_ordenada.append((z_medio, indices, sombreamento))
            
        lista_ordenada.sort(key=lambda item: item[0], reverse=True)

        for z_m, indices, somb in lista_ordenada:
            pontos_2d = []
            for idx in indices:
                rx = int(v_rot[idx][0] * self.escala) + cx
                ry = int(v_rot[idx][1] * self.escala) + cy
                pontos_2d.append((rx, ry))
                
            f_r = (self.r * self.contraste) + self.brilho
            f_g = (self.g * self.contraste) + self.brilho
            f_b = (self.b * self.contraste) + self.brilho
            
            cor_face = (
                max(0, min(255, int(f_r * somb))),
                max(0, min(255, int(f_g * somb))),
                max(0, min(255, int(f_b * somb)))
            )
            
            pygame.draw.polygon(superficie, cor_face, pontos_2d)
            for i in range(len(pontos_2d)):
                pygame.draw.line(superficie, (0, 0, 0), pontos_2d[i], pontos_2d[(i+1)%len(pontos_2d)], width=2)

        if self.selecionado:
            pygame.draw.circle(superficie, (0, 255, 255), (cx, cy), int(t * self.escala) + 20, width=2)

    def checar_clique(self, mouse_pos):
        cx, cy = self.x + self.trans_x, self.y + self.trans_y
        return ((cx - mouse_pos[0])**2 + (cy - mouse_pos[1])**2)**0.5 < (self.tamanho * 1.4 * self.escala)


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
objeto_3d_cenario = Artefato3D("piramide", x=640, y=240) 
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

nomes_filtros = ["Cinza", "Sobel Biblioteca", "Desfocar", "S&P", "Mediana", "Inverter", "Modo Lupa", "Inv Lupa", "Img Fundo", "Reset", "Sobel Manual"]
botoes_lens = []
for i, nome in enumerate(nomes_filtros):
    col, lin = i % 4, i // 4
    bx = 20 + (col * 80)
    by = 530 + (lin * 48)  
    botoes_lens.append({"id": i, "nome": nome, "rect": pygame.Rect(bx, by, 72, 42), "ativo": False})

fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0
matriz_cena = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)

# ---------------------------------------------------------
# LOOP PRINCIPAL DO PROGRAMA
# ---------------------------------------------------------
while True:
    pos_mouse = pygame.mouse.get_pos()
    matriz_cena = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1:
                # 🟢 INTERCEPÇÃO DE CLIQUES DA INTERFACE DO MENU
                if gerenciador_menu.estado != "sandbox":
                    gerenciador_menu.checar_cliques(pos_mouse)
                    continue

                for s in sliders:
                    if s.rect_cursor.collidepoint(pos_mouse): s.arrastando = True
                
                tom = histograma_cv.checar_clique(pos_mouse)
                if tom is not None:
                    print(f"Histograma: Tom de cor {tom} selecionado!")

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
                        elif btn["id"] == 9: # Reset
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
                        elif btn["id"] == 1:  
                            btn["ativo"] = not btn["ativo"]
                            if btn["ativo"]: botoes_lens[10]["ativo"] = False
                        elif btn["id"] == 10: 
                            btn["ativo"] = not btn["ativo"]
                            if btn["ativo"]: botoes_lens[1]["ativo"] = False
                        else:
                            btn["ativo"] = not btn["ativo"]

                if RETANGULO_JOGO.collidepoint(pos_mouse):
                    clicou_objeto = False
                    if objeto_3d_cenario.checar_clique(pos_mouse):
                        objeto_3d_cenario.selecionado = True
                        objeto_3d_cenario.arrastando_para_girar = True
                        forma_selecionada = None
                        clicou_objeto = True
                        
                        sliders[0].valor = objeto_3d_cenario.r / 255
                        sliders[1].valor = objeto_3d_cenario.g / 255
                        sliders[2].valor = objeto_3d_cenario.b / 255
                        sliders[3].valor = (objeto_3d_cenario.brilho + 100) / 200
                        sliders[4].valor = objeto_3d_cenario.contraste / 2.0
                        sliders[5].valor = objeto_3d_cenario.saturacao / 3.0
                    else:
                        objeto_3d_cenario.selecionado = False
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
            if gerenciador_menu.estado == "sandbox":
                if objeto_3d_cenario.selecionado and objeto_3d_cenario.arrastando_para_girar:
                    objeto_3d_cenario.rot_y += evento.rel[0] * 1.2 
                    objeto_3d_cenario.rot_x -= evento.rel[1] * 1.2 
                elif forma_selecionada and arrastando_forma_2d:
                    forma_selecionada.x += evento.rel[0]
                    forma_selecionada.y += evento.rel[1]

        if evento.type == pygame.KEYDOWN:
            # Atalhos de teclado só respondem se o laboratório sandbox estiver na tela
            if gerenciador_menu.estado == "sandbox":
                if evento.key == pygame.K_z: 
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
                    objeto_3d_cenario.tipo_modelo = random.choice(["piramide", "cubo", "prisma", "octaedro", "cristal"])
                    formas.clear()
                    for _ in range(random.randint(4, 6)):
                        formas.append(FormaGeometrica(random.choice(["retangulo", "circulo", "triangulo"]), random.randint(150, 1100), random.randint(100, 380)))

                # Tecla ESC oferece uma forma fácil de voltar ao Menu Principal
                if evento.key == pygame.K_ESCAPE:
                    gerenciador_menu.estado = "menu"

    # -------------------------------------------------------------------------
    # 🧱 ÁRVORE DE RENDERIZAÇÃO POR ESTADOS DE INTERFACE
    # -------------------------------------------------------------------------
    if gerenciador_menu.estado == "sandbox":
        histograma_cv.atualizar_arraste(pos_mouse, pygame.mouse.get_pressed())
        for s in sliders: s.atualizar(pos_mouse)

        teclas = pygame.key.get_pressed()
        if objeto_3d_cenario.selecionado:
            objeto_3d_cenario.r = int(sliders[0].valor * 255)
            objeto_3d_cenario.g = int(sliders[1].valor * 255)
            objeto_3d_cenario.b = int(sliders[2].valor * 255)
            objeto_3d_cenario.brilho = int((sliders[3].valor - 0.5) * 200)
            objeto_3d_cenario.contraste = float(sliders[4].valor * 2.0)
            objeto_3d_cenario.saturacao = float(sliders[5].valor * 3.0)

            if teclas[pygame.K_LEFT]:  objeto_3d_cenario.trans_x -= 4
            if teclas[pygame.K_RIGHT]: objeto_3d_cenario.trans_x += 4
            if teclas[pygame.K_UP]:    objeto_3d_cenario.trans_y -= 4
            if teclas[pygame.K_DOWN]:  objeto_3d_cenario.trans_y += 4
            if teclas[pygame.K_q]:     objeto_3d_cenario.rot_y += 3.0
            if teclas[pygame.K_e]:     objeto_3d_cenario.rot_y -= 3.0
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

        # Montagem do Buffer de Estágio 
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

        # Processamento OpenCV
        if lupa_cv.ativo:
            matriz_cena = lupa_cv.aplicar_lente_local(matriz_cena, pos_mouse, botoes_lens)
        else:
            if botoes_lens[0]["ativo"]: matriz_cena = pdi.aplicar_escala_cinza(matriz_cena)
            if botoes_lens[1]["ativo"]: matriz_cena = pdi.aplicar_sobel(matriz_cena)
            if botoes_lens[2]["ativo"]: matriz_cena = pdi.aplicar_blur(matriz_cena)
            if botoes_lens[3]["ativo"]: matriz_cena = pdi.injetar_ruido_salt_pepper(matriz_cena)
            if botoes_lens[4]["ativo"]: matriz_cena = pdi.aplicar_filtro_mediana(matriz_cena)
            if botoes_lens[5]["ativo"]: matriz_cena = cv2.bitwise_not(matriz_cena)
            if botoes_lens[10]["ativo"]: matriz_cena = sm.aplicar_sobel_manual(matriz_cena)

        if not forma_selecionada and not objeto_3d_cenario.selecionado:
            matriz_cena = matriz_cena.astype(np.float32)
            matriz_cena[:, :, 0] *= fator_global_b
            matriz_cena[:, :, 1] *= fator_global_g
            matriz_cena[:, :, 2] *= fator_global_r
            matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)

            glb_brilho = int((sliders[3].valor - 0.5) * 200)
            glb_contraste = float(sliders[4].valor * 2.0)
            glb_saturacao = float(sliders[5].valor * 3.0)
            matriz_cena = pdi.ajustar_brilho_contraste_saturação(matriz_cena, glb_brilho, glb_contraste, glb_saturacao)

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

        # Exibição do Monitor
        surface_render = ins_img.converter_matriz_para_surface(matriz_cena)
        if surface_render: tela.blit(surface_render, (0, 0))

        lupa_cv.desenhar_contorno_hud(tela, pos_mouse, ALTURA_JOGO)
        
        # Objetivo sempre visível no topo
        txt_sombra = FONTE_M.render("Objetivo: Teste dos filtros e as transformações geométricas nos objetos", True, (0, 0, 0))
        txt_obj = FONTE_M.render("Objetivo: Teste dos filtros e as transformações geométricas nos objetos", True, (255, 255, 255))
        tela.blit(txt_sombra, (21, 21))
        tela.blit(txt_obj, (20, 20))

        # Painel Inferior (HUD FIXA)
        pygame.draw.rect(tela, (24, 24, 27), PANEL_CONTROLE)
        pygame.draw.rect(tela, (0, 128, 255), PANEL_CONTROLE, width=2)
        pygame.draw.line(tela, (50, 50, 60), (350, ALTURA_JOGO), (350, ALTURA), width=2)
        pygame.draw.line(tela, (50, 50, 60), (800, ALTURA_JOGO), (800, ALTURA), width=2)
        pygame.draw.line(tela, (50, 50, 60), (1050, ALTURA_JOGO), (1050, ALTURA), width=2)

        tela.blit(FONTE_M.render("LENS (Filtros & Ruídos)", True, (0, 128, 255)), (20, 495))
        for btn in botoes_lens:
            cor = (0, 128, 255) if btn["ativo"] else ((70, 70, 80) if btn["rect"].collidepoint(pos_mouse) else (40, 40, 45))
            if btn["id"] == 7 and lupa_cv.invertida: cor = (255, 120, 0)
            pygame.draw.rect(tela, cor, btn["rect"], border_radius=4)
            pygame.draw.rect(tela, (90, 90, 100), btn["rect"], width=1, border_radius=4)
            txt_n = FONTE_P.render(btn["nome"][:9], True, (255, 255, 255))
            tela.blit(txt_n, (btn["rect"].x + 5, btn["rect"].y + 14))

        titulo_sliders = "Ajustes de Objeto Ativos" if (forma_selecionada or objeto_3d_cenario.selecionado) else "Ajustes Globais da Cena"
        cor_titulo = (0, 255, 255) if objeto_3d_cenario.selecionado else ((255, 215, 0) if forma_selecionada else (255, 255, 255))
        tela.blit(FONTE_M.render(titulo_sliders, True, cor_titulo), (370, 495))
        for s in sliders: s.desenhar(tela)

        tela.blit(FONTE_M.render("Transformações", True, (255, 215, 0)), (820, 495))
        if forma_selecionada or objeto_3d_cenario.selecionado:
            tela.blit(FONTE_P.render("⟳ Rotação: Teclas Q <- -> E (ou Mouse no 3D)", True, (230, 230, 230)), (820, 540))
            tela.blit(FONTE_P.render("⮂ Translação: Setas (ou Mouse no 2D)", True, (230, 230, 230)), (820, 580))
            tela.blit(FONTE_P.render("⇲ Escala: Teclas R (+) e T (-)", True, (230, 230, 230)), (820, 620))
        else:
            tela.blit(FONTE_P.render("Selecione um objeto para", True, (120, 120, 120)), (820, 550))
            tela.blit(FONTE_P.render("liberar transformações.", True, (120, 120, 120)), (820, 570))

        tela.blit(FONTE_M.render("Histograma 2D", True, (255, 255, 255)), (1070, 495))
        histograma_cv.calcular_e_desenhar(tela, matriz_cena)

    elif gerenciador_menu.estado == "menu":
        gerenciador_menu.desenhar_menu(tela, pos_mouse)

    elif gerenciador_menu.estado == "como_jogar":
        gerenciador_menu.desenhar_como_jogar(tela, pos_mouse)

    elif gerenciador_menu.estado == "config":
        gerenciador_menu.desenhar_configuracoes(tela, pos_mouse)

    elif gerenciador_menu.estado == "sobre":
        gerenciador_menu.desenhar_sobre(tela, pos_mouse)

    elif gerenciador_menu.estado == "conceitos":
        gerenciador_menu.desenhar_conceitos(tela, pos_mouse)

    pygame.display.flip()
    relogio.tick(60)