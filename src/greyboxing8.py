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

pygame.init()
pygame.font.init()

# RESOLUÇÃO EXPANDIDA (Estilo HD para caber todo o design do Tldraw)
LARGURA, ALTURA = 1280, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Greyboxing 8 - Central de Filtros Avançada")
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

# Classe para Gerenciar os Objetos Gráficos e seus Backups
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

        # BACKUP DE SEGURANÇA (Guarda os valores originais de nascimento para o Reset com 'Z')
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

        # Se estiver selecionada, aplica filtros OpenCV locais diretamente na sua própria matriz!
        if selecionada and (self.brilho != 0 or self.contraste != 1.0 or self.saturacao != 1.0):
            array_objeto = pygame.surfarray.array3d(surf)
            matriz_obj = np.transpose(array_objeto, (1, 0, 2))
            matriz_obj_bgr = cv2.cvtColor(matriz_obj, cv2.COLOR_RGBA2BGR)
            
            matriz_obj_bgr = pdi.ajustar_brilho_contraste_saturação(matriz_obj_bgr, self.brilho, self.contraste, self.saturacao)
            
            obj_rgb = cv2.cvtColor(matriz_obj_bgr, cv2.COLOR_BGR2RGB)
            array_final_obj = np.transpose(obj_rgb, (1, 0, 2))
            
            # Preserva o canal alpha de transparência original do Pygame
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

# Configurações iniciais da HUD e dos Atores
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

nomes_filtros = ["Cinza", "Sobel (Linhas)", "Desfocar (Blur)", "Ruído S&P", "Filtro Mediana", "Inverter", "Modo Lupa", "Reset Global"]
botoes_lens = []
for i, nome in enumerate(nomes_filtros):
    col, lin = i % 4, i // 4
    bx = 20 + (col * 80)
    by = 530 + (lin * 60)
    botoes_lens.append({"id": i, "nome": nome, "rect": pygame.Rect(bx, by, 72, 45), "ativo": False})

# Fatores globais iniciais para o processamento de cor da cena
fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0

# Declaramos a variável da matriz fora do loop para os atalhos lerem com segurança
matriz_cena = np.zeros((ALTURA_JOGO, LARGURA, 3), dtype=np.uint8)

# ---------------------------------------------------------
# LOOP PRINCIPAL DO JOGO
# ---------------------------------------------------------
while True:
    pos_mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == MOUSEBUTTONDOWN:
            if evento.button == 1: # Clique Esquerdo
                # 1. Clique nos Sliders
                for s in sliders:
                    if s.rect_cursor.collidepoint(pos_mouse): s.arrastando = True
                
                # 2. Clique Interativo no Histograma
                tom = histograma_cv.checar_clique(pos_mouse)
                if tom is not None:
                    print(f"Histograma: Tom de cor {tom} selecionado pelo clique do mouse!") #Ainda não altera nada e só seleciona verticalmente 
                    # Falta poder segurar com o mouse e arrastar para escolher outros tons, mas já é um começo funcional!
                    # O valor do tom selecionado pode ser usado futuramente para aplicar filtros específicos ou destacar objetos com esse tom na cena! (Funcionalidade futura a ser implementada)
                    # TODO - Implementar a funcionalidade de arrastar o mouse para selecionar tons de cor no histograma e aplicar efeitos relacionados na cena com base nessa seleção! (Ex: Destacar formas que contenham o tom selecionado, ou aplicar um filtro de cor específico na cena usando o tom como referência) e adicionar a linha horizontal tambem para precisão de leitura do histograma. não só a linha vertical implementada atualmente.

                # 3. Clique nos Filtros da Seção LENS
                for btn in botoes_lens:
                    if btn["rect"].collidepoint(pos_mouse):
                        if btn["id"] == 7: # Alterar o reset como estava antes não globalmente mas retornado os sliders e desativando os efeitos
                            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
                        else:
                            btn["ativo"] = not btn["ativo"] # Adicinar a opção de inverter o estado para filtro na lupa ou a lupa para limpar o filtro ativo na cena
                            if btn["id"] == 6: lupa_cv.ativo = btn["ativo"]

                # 4. Clique na Tela de Jogo (Seleção de Formas)
                if RETANGULO_JOGO.collidepoint(pos_mouse):
                    clicou_forma = False
                    for f in formas:
                        if f.checar_clique(pos_mouse):
                            forma_selecionada = f
                            clicou_forma = True
                            # Sincroniza sliders com os atributos internos do Objeto Focado
                            # Retirar a funcionalidade de sincronizar os sliders quando troca da cena para a forma ou vice versa. 
                            # Desincronizar os sliders evita que ao alterar os atributos da forma selecionada e depois na cena os mesmos valores sejam aplicados globalmente na cena, o que não é a intenção. A ideia é que os sliders controlem apenas a forma selecionada, e quando nenhuma forma estiver selecionada, os sliders não devem ter efeito algum na cena. A não ser quando editar os sliders sem nenhuma forma selecionada, ai sim os valores dos sliders devem ser aplicados globalmente na cena, e não mais na forma selecionada, já que não há forma selecionada.
                            sliders[0].valor = f.r / 255
                            sliders[1].valor = f.g / 255
                            sliders[2].valor = f.b / 255
                            sliders[3].valor = (f.brilho + 100) / 200
                            sliders[4].valor = f.contraste / 2.0
                            sliders[5].valor = f.saturacao / 3.0
                            break
                    if not clicou_forma: 
                        forma_selecionada = None
                        # Retorna os sliders visuais para refletir os multiplicadores Globais
                        sliders[0].valor = fator_global_r / 2.0
                        sliders[1].valor = fator_global_g / 2.0
                        sliders[2].valor = fator_global_b / 2.0

        if evento.type == MOUSEBUTTONUP:
            if evento.button == 1:
                for s in sliders: s.arrastando = False
        
        # EVENTOS DE TECLADO (Cliques Únicos / Debugs)
        if evento.type == pygame.KEYDOWN:
            
            # TECLA 'Z': Reset Total + Gravação Estatística no Pseudo Banco JSON
            if evento.key == pygame.K_z:
                # A. Salva uma cópia da matriz alterada de PDI antes de limpar
                matriz_antes_reset = matriz_cena.copy()
                
                # B. Aplica a restauração nativa em todas as formas
                forma_selecionada = None
                lupa_cv.ativo = False
                fator_global_r, fator_global_g, fator_global_b = 1.0, 1.0, 1.0
                
                for f in formas:
                    f.restaurar_estado_original()
                
                # Reseta sliders e botões visuais da HUD
                for s in sliders: 
                    s.valor = 0.5
                    s.rect_cursor.x = s.rect_linha.x + int(s.rect_linha.width * 0.5) - 6
                for btn in botoes_lens: 
                    btn["ativo"] = False
                
                # C. Gera em background o estado limpo pós-reset para amostragem
                tela.fill(COR_FUNDO)
                for f in formas: f.desenhar(tela, selecionada=False)
                tex_pos = pygame.surfarray.array3d(tela)
                mat_pos = np.transpose(tex_pos, (1, 0, 2))
                matriz_depois_reset = cv2.cvtColor(mat_pos, cv2.COLOR_RGB2BGR)[0:ALTURA_JOGO, 0:LARGURA]
                
                # D. Grava o log estruturado no arquivo historico_pdi.json
                logg.salvar_log_experimento(
                    tipo_evento="RESET_LABORATORIO_Z",
                    matriz_antes=matriz_antes_reset,
                    matriz_depois=matriz_depois_reset,
                    tom_histograma=histograma_cv.tom_selecionado,
                    sliders=sliders
                )
                
                histograma_cv.tom_selecionado = None
                print("Debug: HUD limpa, formas restauradas e dados de PDI salvos no JSON!")

            # TECLA 'X': Apagar Cenário Antigo e Regerar Novas Formas Aleatórias
            if evento.key == pygame.K_x:
                forma_selecionada = None
                formas.clear()
                
                quantidade_novas = random.randint(4, 7)
                for _ in range(quantidade_novas):
                    tipo_sorteado = random.choice(["retangulo", "circulo", "triangulo"])
                    nx = random.randint(150, 1100)
                    ny = random.randint(100, 380)
                    formas.append(FormaGeometrica(tipo_sorteado, nx, ny))
                    
                print(f"Debug: {quantidade_novas} novas formas geradas com sucesso via tecla 'X'!")

    for s in sliders: s.atualizar(pos_mouse)

    # ---------------------------------------------------------
    # PROCESSAMENTO DE LOGICA CONTEXTUAL 
    # ---------------------------------------------------------
    if forma_selecionada:
        # Modo Objeto: Sliders controlam exclusivamente a forma em foco
        forma_selecionada.r = int(sliders[0].valor * 255)
        forma_selecionada.g = int(sliders[1].valor * 255)
        forma_selecionada.b = int(sliders[2].valor * 255)
        
        forma_selecionada.brilho = int((sliders[3].valor - 0.5) * 200)
        forma_selecionada.contraste = float(sliders[4].valor * 2.0)
        forma_selecionada.saturacao = float(sliders[5].valor * 3.0)
        
        # Escuta Teclado contínuo para as Transformações Geométricas
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
        # Modo Global: Sliders de canais guardam multiplicadores de matriz para a cena toda
        fator_global_r = float(sliders[0].valor * 2.0)
        fator_global_g = float(sliders[1].valor * 2.0)
        fator_global_b = float(sliders[2].valor * 2.0)

    # 5. RENDERIZAÇÃO DA CENA ORIGINAL
    tela.fill(COR_FUNDO)
    for f in formas:
        f.desenhar(tela, selecionada=(f == forma_selecionada))
        
    txt_obj = FONTE_M.render("Objetivo: Teste dos filtros e as transformações geométricas nos objetos", True, (200, 200, 200))
    tela.blit(txt_obj, (20, 20))

    # ---------------------------------------------------------
    # 🎛️ CAPTURA E PROCESSAMENTO REAL VIA OPENCV 
    # ---------------------------------------------------------
    textura_jogo = pygame.surfarray.array3d(tela)
    matriz_jogo = np.transpose(textura_jogo, (1, 0, 2))
    matriz_bgr = cv2.cvtColor(matriz_jogo, cv2.COLOR_RGB2BGR)
    matriz_cena = matriz_bgr[0:ALTURA_JOGO, 0:LARGURA]

    # Se o Modo Global de cor estiver ativo, aplica a multiplicação linear nos canais da cena
    if not forma_selecionada:
        matriz_cena = matriz_cena.astype(np.float32)
        matriz_cena[:, :, 0] *= fator_global_b  # B
        matriz_cena[:, :, 1] *= fator_global_g  # G
        matriz_cena[:, :, 2] *= fator_global_r  # R
        matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)

    # Aplicação Condicional: Lupa Local vs Filtros de Tela Cheia
    if lupa_cv.ativo:
        matriz_cena = lupa_cv.aplicar_lente_local(matriz_cena, pos_mouse, botoes_lens)
    else:
        if botoes_lens[0]["ativo"]: matriz_cena = pdi.aplicar_escala_cinza(matriz_cena)
        if botoes_lens[1]["ativo"]: matriz_cena = pdi.aplicar_sobel(matriz_cena)
        if botoes_lens[2]["ativo"]: matriz_cena = pdi.aplicar_blur(matriz_cena)
        if botoes_lens[3]["ativo"]: matriz_cena = pdi.injetar_ruido_salt_pepper(matriz_cena)
        if botoes_lens[4]["ativo"]: matriz_cena = pdi.aplicar_filtro_mediana(matriz_cena)
        if botoes_lens[5]["ativo"]: matriz_cena = cv2.bitwise_not(matriz_cena)

    # Adicionar o toggle de lupa para:
    # - Ativar a lupa para aplicar um filtro local apenas na região da lente, sem afetar o restante da cena.
    # - Ativar a lupa para limpar os filtros local ativos globais na cena apenas na região da lente, como uma espécie de "borracha de filtro" local, sem afetar o restante da cena. 

    # Sliders Globais de Efeito (Apenas em Modo Cena)
    if not forma_selecionada:
        glb_brilho = int((sliders[3].valor - 0.5) * 200)
        glb_contraste = float(sliders[4].valor * 2.0)
        glb_saturacao = float(sliders[5].valor * 3.0)
        matriz_cena = pdi.ajustar_brilho_contraste_saturação(matriz_cena, glb_brilho, glb_contraste, glb_saturacao)

    # Devolve o buffer de vídeo processado de volta para a Surface do Pygame
    cena_rgb = cv2.cvtColor(matriz_cena, cv2.COLOR_BGR2RGB)
    array_final = np.transpose(cena_rgb, (1, 0, 2))
    surface_render = pygame.surfarray.make_surface(array_final)
    tela.blit(surface_render, (0, 0))

    # Desenha o anel sutil da lente por cima da cena
    lupa_cv.desenhar_contorno_hud(tela, pos_mouse, ALTURA_JOGO)

    # ---------------------------------------------------------
    # DESENHO DA HUD COMPLETA (Fixa na Janela)
    # ---------------------------------------------------------
    pygame.draw.rect(tela, (24, 24, 27), PANEL_CONTROLE)
    pygame.draw.rect(tela, (0, 128, 255), PANEL_CONTROLE, width=2)

    pygame.draw.line(tela, (50, 50, 60), (350, ALTURA_JOGO), (350, ALTURA), width=2)
    pygame.draw.line(tela, (50, 50, 60), (800, ALTURA_JOGO), (800, ALTURA), width=2)
    pygame.draw.line(tela, (50, 50, 60), (1050, ALTURA_JOGO), (1050, ALTURA), width=2)

    # 1. Desenho da Seção LENS
    tela.blit(FONTE_M.render("LENS (Filtros & Ruídos)", True, (0, 128, 255)), (20, 495))
    for btn in botoes_lens:
        cor = (0, 128, 255) if btn["ativo"] else ((70, 70, 80) if btn["rect"].collidepoint(pos_mouse) else (40, 40, 45))
        pygame.draw.rect(tela, cor, btn["rect"], border_radius=4)
        pygame.draw.rect(tela, (90, 90, 100), btn["rect"], width=1, border_radius=4)
        txt_n = FONTE_P.render(btn["nome"][:8], True, (255, 255, 255))
        tela.blit(txt_n, (btn["rect"].x + 6, btn["rect"].y + 15))

    # 2. Desenho da Seção SLIDERS (Títulos dinâmicos por contexto)
    titulo_sliders = "Ajustes de Objeto Ativos" if forma_selecionada else "Ajustes Globais da Cena"
    cor_titulo = (255, 215, 0) if forma_selecionada else (255, 255, 255)
    tela.blit(FONTE_M.render(titulo_sliders, True, cor_titulo), (370, 495))
    for s in sliders: s.desenhar(tela)

    # 3. Desenho da Seção TRANSFORMAÇÕES GEOMÉTRICAS
    tela.blit(FONTE_M.render("Transformações", True, (255, 215, 0)), (820, 495))
    if forma_selecionada:
        tela.blit(FONTE_P.render("⟳ Rotação: Teclas Q <- -> E", True, (230, 230, 230)), (820, 540))
        tela.blit(FONTE_P.render("⮂ Translação: Setas do Teclado", True, (230, 230, 230)), (820, 580))
        tela.blit(FONTE_P.render("⇲ Escala: Teclas R (+) e T (-)", True, (230, 230, 230)), (820, 620))
    else:
        tela.blit(FONTE_P.render("Selecione um objeto para", True, (120, 120, 120)), (820, 550))
        tela.blit(FONTE_P.render("liberar transformações.", True, (120, 120, 120)), (820, 570))

    # 4. Desenho e Plotagem do HISTOGRAMA INTERATIVO MODULAR
    tela.blit(FONTE_M.render("Histograma", True, (255, 255, 255)), (1070, 495))
    histograma_cv.calcular_e_desenhar(tela, matriz_cena)
    # Falta implementar real interatividade de clique e arraste para seleção de tons no histograma, e usar essa seleção para aplicar efeitos relacionados na cena! Funcionalidade futura que deve ser implementada

    pygame.display.flip()
    relogio.tick(60)

    # ---------------------------------------------------------
    # Lista de tarefas
    # ---------------------------------------------------------
    # Modularizar as funções que vão ser usadas no jogo principal
    # Adicionar a opçao de salvar a imagem processada atual da cena como um arquivo .png para comparação visual direta entre o estado original e o estado processado
    # Adicionar um melhor sistema de logging para registrar as ações do usuário, os parâmetros dos filtros aplicados e as mudanças na cena, salvando tudo em talvez um banco de dados local ou um arquivo JSON estruturado para análises futuras e para entender melhor o comportamento dos filtros e as todas as transformações aplicadas, e não só os resets como está sendo feito atualmente, mas também os filtros aplicados, as transformações geométricas, as interações com o histograma, etc. para ter um registro completo do que foi testado e aplicado na cena.
    # Adicionar a opção de adicionar uma imagem de fundo personalizada para a cena ou textura, para testar os filtros e as transformações em um cenário mais complexo e realista, além das formas geométricas básicas. Isso pode ajudar a entender melhor como os filtros interagem com diferentes tipos de imagens e texturas, e não só com formas simples.
    # Adicionar a opção de exportar os dados do experimento, como os logs de interação, as matrizes de imagem antes e depois dos filtros, os parâmetros aplicados, etc. para um formato que possa ser facilmente analisado posteriormente, como um arquivo CSV ou um banco de dados local, para facilitar a análise dos resultados e entender melhor o impacto dos filtros e das transformações aplicadas na cena.
    # Adicionar um menu de configurações para personalizar os atalhos de teclado, as cores da HUD, os tipos de formas disponíveis, os filtros aplicáveis, etc. para tornar o laboratório mais flexível e adaptável às preferências do usuário e aos diferentes tipos de testes que podem ser realizados. E adicionar configurações como sons, musica e como jogar, para tornar a experiência mais imersiva e divertida, além de facilitar o entendimento de como usar o laboratório e seus recursos.
    # Adicionar funções uteis com redo e undo para desfazer ou refazer as últimas ações realizadas, como a aplicação de um filtro, uma transformação geométrica, uma alteração de cor, etc. para facilitar a experimentação e permitir que o usuário possa testar diferentes combinações de filtros e transformações sem se preocupar em perder o progresso ou ter que resetar tudo para voltar a um estado anterior.
    # Começar a implementar funções do jogo mesmo como selecionar e coletar itens e adicionar o  personagem e seus assets e mecanicas de movimento, para começar a testar as mecânicas de jogo e como os filtros e as transformações podem ser usados de forma estratégica dentro do contexto de um jogo, e não só como um laboratório de testes isolado. Isso pode ajudar a entender melhor o potencial dos filtros e das transformações como ferramentas de gameplay, e não só como efeitos visuais ou experimentos técnicos.
    # 
    # ---------------------------------------------------------
    # Lista de correções e melhorias
    # ---------------------------------------------------------
    # Corrigir o bug onde os sliders ficam desincronizados com os atributos da forma selecionada quando se alterna entre a cena e a forma, fazendo com que os sliders apliquem efeitos globais ao deselecionar, o que não é o comportamento esperado a cena não deveria aplicar os valores do slider alterados para a forma. A ideia é que os sliders controlem apenas a forma selecionada, e quando nenhuma forma estiver selecionada, os sliders devem controlar os efeitos globais da cena. Corrigir essa lógica de sincronização para garantir que os sliders tenham o comportamento esperado em ambos os contextos.
    # Corrigir o histograma para que a seleção de tons de cor seja mais precisa e intuitiva, permitindo que o usuário clique e arraste para selecionar uma faixa de tons no histograma, e que essa seleção seja refletida na cena de forma clara, como destacando as formas que contenham os tons selecionados ou aplicando um filtro específico baseado nessa seleção. Dando uma interatividade para o histograma e torná-lo uma ferramenta mais útil para análise e manipulação da cena.
    # Corrigir o bug onde ao aplicar um filtro global na cena e depois selecionar uma forma, os sliders refletem os valores do filtro global em vez dos atributos da forma selecionada, causando confusão sobre o que está sendo editado. Garantir que ao selecionar uma forma, os sliders mostrem os atributos originais da forma, e que as alterações feitas nos sliders afetem apenas a forma selecionada, sem interferir nos filtros globais aplicados na cena.
    # Corrigir o comportamento do botão de reset para que diferentemente do atalho de teclado 'Z' ele limpe apenas os filtros e sliders globais aplicados na cena, sem restaurar as formas para seus estados originais, permitindo que o usuário possa experimentar com os filtros globais sem perder as transformações e alterações feitas nas formas. O botão de reset deve agir como uma "borracha de filtro" para a cena, enquanto o atalho 'Z' continua a ser um reset total que restaura tudo ao estado original.
    # Corrigir a HUD para que os botões de filtro e os sliders tenham um feedback visual mais claro sobre seu estado ativo ou inativo, como mudar de cor, mostrar um ícone, ou ter uma animação sutil, para facilitar a identificação rápida do que está ativo na cena e melhorar a usabilidade da interface. E melhorar a organização visual da HUD para que as seções de filtros, sliders, transformações, e histograma sejam mais claramente delimitadas e fáceis de entender, talvez usando caixas, linhas divisórias, ou cores de fundo diferentes para cada seção, para tornar a interface mais intuitiva e agradável de usar.
    #
    #
    #
    #
    #