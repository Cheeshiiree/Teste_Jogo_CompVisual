import pygame
import sys

class MenuUI:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        
        # Estados possíveis: "menu", "sandbox", "como_jogar", "config", "sobre", "conceitos"
        self.estado = "menu"
        self.tema_claro = True
        self.volume_musica = 0.65
        self.musica_mutada = False
        self.resolucoes = [(1280, 720), (1366, 768)]
        self.indice_resolucao = 0
        self.ajuste_volume = 0.05
        
        # Fontes do sistema
        self.fonte_titulo = pygame.font.SysFont("Arial", 48, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("Arial", 22, bold=True)
        self.fonte_btn = pygame.font.SysFont("Arial", 18, bold=True)
        self.fonte_texto = pygame.font.SysFont("Arial", 16, bold=True)
        self.fonte_codigo = pygame.font.SysFont("Courier New", 14, bold=True)

        # Fontes maiores usadas na tela rolável de Conceitos e Códigos
        self.fonte_conceito_titulo = pygame.font.SysFont("Arial", 25, bold=True)
        self.fonte_conceito_texto = pygame.font.SysFont("Arial", 17, bold=True)
        self.fonte_conceito_codigo = pygame.font.SysFont("Courier New", 15, bold=True)

        # Controle da rolagem da página Conceitos e Códigos
        self.scroll_conceitos = 0
        self.scroll_conceitos_max = 0
        self.recalcular_layout(largura, altura)

    def recalcular_layout(self, largura, altura):
        self.largura = largura
        self.altura = altura

        # Configuração dos botões organizados em duas colunas
        w_btn = 260
        h_btn = 45
        cx_esq = (largura // 2) - w_btn - 15
        cx_dir = (largura // 2) + 15

        self.btn_iniciar = pygame.Rect(cx_esq, 280, w_btn, h_btn)
        self.btn_como_jogar = pygame.Rect(cx_dir, 280, w_btn, h_btn)
        self.btn_config = pygame.Rect(cx_esq, 340, w_btn, h_btn)
        self.btn_sobre = pygame.Rect(cx_dir, 340, w_btn, h_btn)
        self.btn_conceitos = pygame.Rect(cx_esq, 400, w_btn, h_btn)
        self.btn_sair = pygame.Rect(cx_dir, 400, w_btn, h_btn)

        self.btn_voltar = pygame.Rect((largura // 2) - 100, max(altura - 90, 600), 200, 45)

        centro = largura // 2
        self.rect_volume_barra = pygame.Rect(centro - 170, 250, 340, 12)
        self.btn_volume_menos = pygame.Rect(centro - 228, 240, 42, 32)
        self.btn_volume_mais = pygame.Rect(centro + 186, 240, 42, 32)
        self.btn_mute = pygame.Rect(centro - 90, 288, 180, 34)

        self.btn_res_1280 = pygame.Rect(centro - 220, 422, 180, 38)
        self.btn_res_1366 = pygame.Rect(centro + 40, 422, 180, 38)

        self.btn_tema_claro = pygame.Rect(centro - 220, 502, 180, 38)
        self.btn_tema_escuro = pygame.Rect(centro + 40, 502, 180, 38)

    def _paleta(self):
        if self.tema_claro:
            return {
                "fundo": (236, 240, 245),
                "fundo_alt": (228, 233, 239),
                "painel": (245, 248, 252),
                "painel_alt": (222, 228, 236),
                "texto": (35, 45, 60),
                "texto_suave": (70, 80, 95),
                "borda": (158, 168, 182),
                "botao": (250, 252, 255),
                "botao_texto": (35, 45, 60),
                "titulo": (25, 102, 190),
                "titulo_sombra": (135, 152, 175),
                "acento_azul": (202, 226, 250),
                "acento_verde": (204, 238, 224),
                "acento_neutro": (224, 228, 236),
                "acento_amarelo": (248, 237, 201),
                "acento_roxo": (227, 214, 243),
                "acento_vermelho": (247, 213, 213),
                "botao_voltar": (202, 92, 92),
                "botao_selecionado": (25, 102, 190),
                "texto_botao_selecionado": (255, 255, 255),
            }

        return {
            "fundo": (19, 21, 27),
            "fundo_alt": (24, 27, 35),
            "painel": (31, 35, 44),
            "painel_alt": (40, 45, 56),
            "texto": (235, 239, 245),
            "texto_suave": (177, 185, 196),
            "borda": (77, 85, 99),
            "botao": (44, 49, 60),
            "botao_texto": (235, 239, 245),
            "titulo": (118, 169, 255),
            "titulo_sombra": (49, 59, 80),
            "acento_azul": (56, 124, 201),
            "acento_verde": (54, 145, 116),
            "acento_neutro": (82, 89, 104),
            "acento_amarelo": (168, 136, 44),
            "acento_roxo": (124, 82, 176),
            "acento_vermelho": (178, 74, 74),
            "botao_voltar": (174, 76, 76),
            "botao_selecionado": (118, 169, 255),
            "texto_botao_selecionado": (20, 20, 22),
        }

    def _normalizar_paleta(self, paleta):
        """Mantém compatibilidade entre nomes antigos e novos da paleta."""
        paleta["accent_azul"] = paleta.get("acento_azul", (0, 128, 255))
        paleta["accent_amarelo"] = paleta.get("acento_amarelo", (255, 215, 0))
        paleta["botao_hover"] = paleta.get("painel_alt", paleta.get("botao", (45, 45, 52)))
        return paleta

    def obter_paleta(self):
        # Usada apenas nas telas de menu/configurações/conceitos.
        # Esta paleta respeita a escolha de modo claro ou escuro.
        return self._normalizar_paleta(self._paleta())

    def obter_paleta_sandbox(self):
        # O sandbox deve permanecer sempre no visual escuro original,
        # independente da opção de modo claro/escuro escolhida no menu.
        return self._normalizar_paleta({
            "fundo": (20, 20, 22),
            "fundo_alt": (25, 25, 28),
            "painel": (30, 30, 35),
            "painel_alt": (45, 45, 52),
            "texto": (255, 255, 255),
            "texto_suave": (200, 200, 210),
            "borda": (70, 70, 80),
            "botao": (30, 30, 35),
            "botao_texto": (255, 255, 255),
            "titulo": (0, 128, 255),
            "titulo_sombra": (0, 0, 0),
            "acento_azul": (0, 128, 255),
            "acento_verde": (0, 180, 120),
            "acento_neutro": (100, 100, 110),
            "acento_amarelo": (255, 215, 0),
            "acento_roxo": (150, 50, 200),
            "acento_vermelho": (220, 50, 50),
            "botao_voltar": (200, 50, 50),
            "botao_selecionado": (0, 128, 255),
            "texto_botao_selecionado": (255, 255, 255),
        })

    def resolucao_atual(self):
        return self.resolucoes[self.indice_resolucao]

    def obter_resolucao_atual(self):
        return self.resolucao_atual()

    def volume_formatado(self):
        return int(self.volume_musica * 100)

    def desenhar_menu(self, superficie, pos_mouse):
        """Desenha a tela de abertura com os 6 botões interativos."""
        paleta = self._paleta()
        superficie.fill(paleta["fundo"])
        
        # Título Principal do Painel
        txt_titulo_s = self.fonte_titulo.render("LAB COMPUTAÇÃO VISUAL", True, paleta["titulo_sombra"])
        txt_titulo = self.fonte_titulo.render("LAB COMPUTAÇÃO VISUAL", True, paleta["titulo"])
        superficie.blit(txt_titulo_s, ((self.largura // 2) - txt_titulo_s.get_width() // 2 + 3, 133))
        superficie.blit(txt_titulo, ((self.largura // 2) - txt_titulo.get_width() // 2, 130))
        
        def renderizar_botao(rect, texto, cor_foco, pos):
            foco = rect.collidepoint(pos)
            cor = cor_foco if foco else paleta["botao"]
            pygame.draw.rect(superficie, cor, rect, border_radius=5)
            pygame.draw.rect(superficie, paleta["borda"], rect, width=2, border_radius=5)
            txt = self.fonte_btn.render(texto, True, paleta["botao_texto"])
            superficie.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Renderização da grade dupla de botões
        renderizar_botao(self.btn_iniciar, "Iniciar Sandbox", paleta["acento_azul"], pos_mouse)
        renderizar_botao(self.btn_como_jogar, "Como Jogar", paleta["acento_verde"], pos_mouse)
        renderizar_botao(self.btn_config, "Configurações", paleta["acento_neutro"], pos_mouse)
        renderizar_botao(self.btn_sobre, "Sobre", paleta["acento_amarelo"], pos_mouse)
        renderizar_botao(self.btn_conceitos, "Conceitos e Códigos", paleta["acento_roxo"], pos_mouse)
        renderizar_botao(self.btn_sair, "Sair do Programa", paleta["acento_vermelho"], pos_mouse)

    def desenhar_voltar(self, superficie, pos_mouse):
        """Desenha o botão de retorno para as sub-telas."""
        paleta = self._paleta()
        foco = self.btn_voltar.collidepoint(pos_mouse)
        cor = paleta["botao_voltar"] if foco else paleta["botao"]
        pygame.draw.rect(superficie, cor, self.btn_voltar, border_radius=5)
        pygame.draw.rect(superficie, paleta["borda"], self.btn_voltar, width=1, border_radius=5)
        cor_txt = (255, 255, 255) if foco else paleta["botao_texto"]
        txt = self.fonte_btn.render("Voltar ao Menu", True, cor_txt)
        superficie.blit(txt, (self.btn_voltar.centerx - txt.get_width() // 2, self.btn_voltar.centery - txt.get_height() // 2))

    def desenhar_como_jogar(self, superficie, pos_mouse):
        paleta = self._paleta()
        superficie.fill(paleta["fundo"])
        txt = self.fonte_titulo.render("COMO JOGAR", True, (24, 140, 96) if self.tema_claro else (82, 205, 157))
        superficie.blit(txt, ((self.largura // 2) - txt.get_width() // 2, 80))
        
        regras = [
            "• Clique nas Formas 2D com o botão esquerdo e arraste o mouse para movê-las livremente.",
            "• Clique no Artefato 3D centralizado e mova o mouse para rotacioná-lo em TODOS os eixos.",
            "• Use as SETAS do teclado para transladar a posição do objeto 3D pela tela.",
            "• Teclas Q e E rotacionam o objeto, e as teclas R e T controlam sua escala (tamanho).",
            "• Na HUD inferior, clique nos botões LENS para aplicar filtros espaciais OpenCV em tempo real.",
            "• No HISTOGRAMA, clique e arraste lateralmente para escolher o Tom, e verticalmente para alterar o Ganho.",
            "• Pressione X para regerar o laboratório e sortear uma nova forma 3D (Cubo, Octaedro, Cristal...).",
            "• Pressione Z a qualquer momento para resetar o cenário e exportar os logs em JSON."
        ]
        y = 180
        for r in regras:
            surf_r = self.fonte_texto.render(r, True, paleta["texto_suave"])
            superficie.blit(surf_r, (80, y))
            y += 40
        self.desenhar_voltar(superficie, pos_mouse)

    def desenhar_configuracoes(self, superficie, pos_mouse):
        paleta = self._paleta()
        superficie.fill(paleta["fundo_alt"])
        txt = self.fonte_titulo.render("CONFIGURAÇÕES", True, paleta["titulo"])
        superficie.blit(txt, ((self.largura // 2) - txt.get_width() // 2, 80))

        # Cartão de áudio
        pygame.draw.rect(superficie, paleta["painel"], (60, 180, self.largura - 120, 145), border_radius=12)
        pygame.draw.rect(superficie, paleta["borda"], (60, 180, self.largura - 120, 145), width=1, border_radius=12)
        superficie.blit(self.fonte_subtitulo.render("Áudio / BGM", True, paleta["texto"]), (84, 196))
        resolucao_atual = self.resolucao_atual()
        txt_volume = self.fonte_texto.render(f"Volume da música: {self.volume_formatado()}%", True, paleta["texto_suave"])
        superficie.blit(txt_volume, (84, 220))

        pygame.draw.rect(superficie, paleta["borda"], self.rect_volume_barra, width=1, border_radius=6)
        largura_preenchida = max(0, min(self.rect_volume_barra.width, int(self.rect_volume_barra.width * self.volume_musica)))
        barra_fill = pygame.Rect(self.rect_volume_barra.x, self.rect_volume_barra.y, largura_preenchida, self.rect_volume_barra.height)
        pygame.draw.rect(superficie, paleta["titulo"], barra_fill, border_radius=6)
        pygame.draw.rect(superficie, paleta["painel_alt"], self.btn_volume_menos, border_radius=6)
        pygame.draw.rect(superficie, paleta["painel_alt"], self.btn_volume_mais, border_radius=6)
        pygame.draw.rect(superficie, paleta["borda"], self.btn_volume_menos, width=1, border_radius=6)
        pygame.draw.rect(superficie, paleta["borda"], self.btn_volume_mais, width=1, border_radius=6)
        txt_menos = self.fonte_btn.render("-", True, paleta["texto"])
        txt_mais = self.fonte_btn.render("+", True, paleta["texto"])
        superficie.blit(txt_menos, (self.btn_volume_menos.centerx - txt_menos.get_width() // 2, self.btn_volume_menos.centery - txt_menos.get_height() // 2 - 2))
        superficie.blit(txt_mais, (self.btn_volume_mais.centerx - txt_mais.get_width() // 2, self.btn_volume_mais.centery - txt_mais.get_height() // 2 - 2))

        cor_mute = paleta["botao_voltar"] if self.musica_mutada else paleta["botao"]
        pygame.draw.rect(superficie, cor_mute, self.btn_mute, border_radius=6)
        pygame.draw.rect(superficie, paleta["borda"], self.btn_mute, width=1, border_radius=6)
        txt_mute = self.fonte_btn.render("Desmutar música" if self.musica_mutada else "Mutar música", True, (255, 255, 255) if self.musica_mutada else paleta["botao_texto"])
        superficie.blit(txt_mute, (self.btn_mute.centerx - txt_mute.get_width() // 2, self.btn_mute.centery - txt_mute.get_height() // 2))

        # Cartão de resolução
        pygame.draw.rect(superficie, paleta["painel"], (60, 345, self.largura - 120, 145), border_radius=12)
        pygame.draw.rect(superficie, paleta["borda"], (60, 345, self.largura - 120, 145), width=1, border_radius=12)
        superficie.blit(self.fonte_subtitulo.render("Resolução", True, paleta["texto"]), (84, 361))
        txt_res = self.fonte_texto.render(f"Resolução atual: {resolucao_atual[0]} x {resolucao_atual[1]}", True, paleta["texto_suave"])
        superficie.blit(txt_res, (84, 385))

        for indice, (rect, resolucao) in enumerate(((self.btn_res_1280, self.resolucoes[0]), (self.btn_res_1366, self.resolucoes[1]))):
            selecionado = resolucao == resolucao_atual
            cor_btn = paleta["botao_selecionado"] if selecionado else paleta["botao"]
            texto_cor = paleta["texto_botao_selecionado"] if selecionado else paleta["botao_texto"]
            pygame.draw.rect(superficie, cor_btn, rect, border_radius=6)
            pygame.draw.rect(superficie, paleta["borda"], rect, width=1, border_radius=6)
            txt_btn = self.fonte_btn.render(f"{resolucao[0]} x {resolucao[1]}", True, texto_cor)
            superficie.blit(txt_btn, (rect.centerx - txt_btn.get_width() // 2, rect.centery - txt_btn.get_height() // 2))

        # Cartão de tema
        pygame.draw.rect(superficie, paleta["painel"], (60, 510, self.largura - 120, 120), border_radius=12)
        pygame.draw.rect(superficie, paleta["borda"], (60, 510, self.largura - 120, 120), width=1, border_radius=12)
        superficie.blit(self.fonte_subtitulo.render("Tema da interface", True, paleta["texto"]), (84, 526))
        txt_tema = self.fonte_texto.render("Escolha entre modo claro e escuro.", True, paleta["texto_suave"])
        superficie.blit(txt_tema, (84, 550))

        for rect, texto, selecionado in (
            (self.btn_tema_claro, "Modo claro", self.tema_claro),
            (self.btn_tema_escuro, "Modo escuro", not self.tema_claro),
        ):
            cor_btn = paleta["botao_selecionado"] if selecionado else paleta["botao"]
            texto_cor = paleta["texto_botao_selecionado"] if selecionado else paleta["botao_texto"]
            pygame.draw.rect(superficie, cor_btn, rect, border_radius=6)
            pygame.draw.rect(superficie, paleta["borda"], rect, width=1, border_radius=6)
            txt_btn = self.fonte_btn.render(texto, True, texto_cor)
            superficie.blit(txt_btn, (rect.centerx - txt_btn.get_width() // 2, rect.centery - txt_btn.get_height() // 2))

        self.desenhar_voltar(superficie, pos_mouse)

    def desenhar_sobre(self, superficie, pos_mouse):
        paleta = self._paleta()
        superficie.fill(paleta["fundo_alt"])
        txt = self.fonte_titulo.render("SOBRE O PROJETO / AUTORES", True, paleta["acento_amarelo"])
        superficie.blit(txt, ((self.largura // 2) - txt.get_width() // 2, 80))
        
        dados = [
            "UNIVERSIDADE FEDERAL DE ITAJUBÁ — UNIFEI",
            "Instituto de Matemática e Computação — IMC",
            "Curso: Ciência da Computação",
            "Disciplina: COM242 — Computação Visual / Processamento Digital de Imagens",
            "--------------------------------------------------------------------------------------------------------",
            "Desenvolvido por:",
            "• Anna Beatryz Costa (ABC) — 2025007883",
            "• Emilly Vitória Pereira da Silva — 2023008676",
            "• Julia Barcellos Paiva — 2022010393",
            "• Rafaela Cristina de Moraes Mendes - 2024009453",
            "--------------------------------------------------------------------------------------------------------",
            "Finalidade: Aplicação prática interdisciplinar demonstrando a unificação de filtros espaciais,",
            "transformações geométricas tridimensionais manuais e análise estatística de histogramas."
        ]
        y = 180
        for d in dados:
            cor = paleta["titulo"] if "UNIFEI" in d else ((176, 130, 24) if "•" in d else paleta["texto_suave"])
            surf_d = self.fonte_texto.render(d, True, cor)
            superficie.blit(surf_d, ((self.largura // 2) - surf_d.get_width() // 2, y))
            y += 35
        self.desenhar_voltar(superficie, pos_mouse)

    def rolar_conceitos(self, deslocamento):
        """Atualiza a rolagem vertical da tela Conceitos e Códigos."""
        self.scroll_conceitos = max(0, min(self.scroll_conceitos + deslocamento, self.scroll_conceitos_max))

    def desenhar_conceitos(self, superficie, pos_mouse):
        paleta = self.obter_paleta()
        superficie.fill(paleta["fundo"])

        margem_x = 50
        topo_area = 105
        rodape_area = self.btn_voltar.y - 16
        area_visivel = pygame.Rect(margem_x, topo_area, self.largura - (margem_x * 2) - 18, max(220, rodape_area - topo_area))
        largura_conteudo = area_visivel.width

        txt = self.fonte_titulo.render("CONCEITOS & CÓDIGOS UTILIZADOS", True, paleta["acento_roxo"])
        superficie.blit(txt, ((self.largura // 2) - txt.get_width() // 2, 28))

        dica = "Use a roda do mouse, ↑/↓ ou PageUp/PageDown para navegar pelos códigos."
        txt_dica = self.fonte_texto.render(dica, True, paleta["texto_suave"])
        superficie.blit(txt_dica, ((self.largura // 2) - txt_dica.get_width() // 2, 78))

        def quebrar_texto(texto, fonte, largura_max):
            palavras = texto.split(" ")
            linhas = []
            linha = ""
            for palavra in palavras:
                tentativa = palavra if not linha else linha + " " + palavra
                if fonte.size(tentativa)[0] <= largura_max:
                    linha = tentativa
                else:
                    if linha:
                        linhas.append(linha)
                    linha = palavra
            if linha:
                linhas.append(linha)
            return linhas or [""]

        def linhas_codigo(codigo):
            saida = []
            for linha in codigo.strip("\n").split("\n"):
                if not linha.strip():
                    saida.append("")
                    continue
                # Quebra linhas muito longas mantendo uma leitura boa em 1280x720.
                while self.fonte_conceito_codigo.size(linha)[0] > largura_conteudo - 64 and len(linha) > 18:
                    corte = min(len(linha), 112)
                    melhor = max(linha.rfind(" ", 0, corte), linha.rfind(",", 0, corte), linha.rfind(")", 0, corte))
                    if melhor < 35:
                        melhor = corte
                    saida.append(linha[:melhor + 1].rstrip())
                    linha = "    " + linha[melhor + 1:].lstrip()
                saida.append(linha)
            return saida

        secoes = [
            {
                "titulo": "1. Lupa local — filtro aplicado só dentro do círculo",
                "cor": paleta["acento_azul"],
                "texto": "A lupa usa a posição do mouse como centro e cria uma máscara circular. Somente os pixels dentro do raio são substituídos pela versão filtrada; o restante da cena permanece original.",
                "codigo": """
# No greyboxing.py, quando a lupa está ativa:
if lupa_cv.ativo:
    matriz_cena = lupa_cv.aplicar_lente_local(matriz_cena, pos_mouse, botoes_lens)

# Ideia do algoritmo dentro do filtro local:
distancia = sqrt((x - mouse_x)**2 + (y - mouse_y)**2)
mascara_lupa = distancia <= raio
imagem_filtrada = aplicar_filtros_na_copia(imagem_bgr)
saida = imagem_bgr.copy()
saida[mascara_lupa] = imagem_filtrada[mascara_lupa]
""",
            },
            {
                "titulo": "2. Lupa invertida — preserva o centro e altera o lado de fora",
                "cor": (255, 120, 0),
                "texto": "A lupa invertida reutiliza a mesma distância ao mouse, mas troca a máscara: em vez de filtrar dentro do círculo, ela filtra tudo que está fora dele. Por isso o botão 'Inv Lupa' altera a área afetada.",
                "codigo": """
# Ativação no botão Inv Lupa:
elif btn["id"] == 7:
    btn["ativo"] = not btn["ativo"]
    lupa_cv.invertida = btn["ativo"]

# Ideia da máscara invertida:
mascara_lupa = distancia <= raio
if self.invertida:
    mascara_lupa = distancia > raio

saida[mascara_lupa] = imagem_filtrada[mascara_lupa]
""",
            },
            {
                "titulo": "3. Filtro pixelar manual — mosaico por média de blocos",
                "cor": paleta["acento_verde"],
                "texto": "O pixelar manual reduz a resolução espacial da imagem. A imagem é dividida em blocos, a cor média de cada bloco é calculada e todos os pixels daquele bloco recebem essa mesma cor.",
                "codigo": """
def aplicar_pixelar_manual(imagem_bgr, tamanho_bloco=12):
    alt, larg, canais = imagem_bgr.shape
    resultado = np.zeros((alt, larg, canais), dtype=np.uint8)

    for y in range(0, alt, tamanho_bloco):
        for x in range(0, larg, tamanho_bloco):
            limite_y = min(y + tamanho_bloco, alt)
            limite_x = min(x + tamanho_bloco, larg)
            bloco = imagem_bgr[y:limite_y, x:limite_x]
            cor_media = np.mean(bloco, axis=(0, 1))
            resultado[y:limite_y, x:limite_x] = cor_media

    return resultado
""",
            },
            {
                "titulo": "4. Funcionamento do histograma — seleção de tom e ganho",
                "cor": paleta["acento_amarelo"],
                "texto": "O histograma mostra a frequência dos tons em cada canal BGR. Ao clicar no gráfico, o programa guarda o tom selecionado. Ao arrastar verticalmente, ele altera o ganho aplicado nos pixels próximos daquele tom.",
                "codigo": """
# Clique no histograma:
tom = histograma_cv.checar_clique(pos_mouse)
if tom is not None:
    print(f"Histograma: Tom de cor {tom} selecionado!")

# Aplicação do ganho seletivo no canal ativo:
tom_alvo = histograma_cv.tom_selecionado
ganho_vertical = histograma_cv.fator_escala
idx_canal = histograma_cv.canal_ativo
tolerancia = 20

canal = matriz_cena[:, :, idx_canal]
mascara = (canal >= tom_alvo - tolerancia) & (canal <= tom_alvo + tolerancia)
matriz_cena[:, :, idx_canal] = np.where(mascara, canal * ganho_vertical, canal)
matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)
""",
            },
            {
                "titulo": "5. Transformações das formas 2D — translação, rotação e escala",
                "cor": paleta["acento_verde"],
                "texto": "As formas 2D armazenam posição, rotação e tamanho. A translação muda x/y, a rotação altera o ângulo da Surface e a escala aumenta ou reduz o tamanho usado no desenho.",
                "codigo": """
# Translação: altera a posição do centro da forma
if teclas[pygame.K_LEFT]:  forma_selecionada.x -= 4
if teclas[pygame.K_RIGHT]: forma_selecionada.x += 4
if teclas[pygame.K_UP]:    forma_selecionada.y -= 4
if teclas[pygame.K_DOWN]:  forma_selecionada.y += 4

# Rotação: altera o ângulo antes de desenhar na tela
if teclas[pygame.K_q]: forma_selecionada.rotacao += 3
if teclas[pygame.K_e]: forma_selecionada.rotacao -= 3
surf_rot = pygame.transform.rotate(surf, self.rotacao)
superficie.blit(surf_rot, surf_rot.get_rect(center=(self.x, self.y)).topleft)

# Escala: muda o tamanho da forma
if teclas[pygame.K_r]: forma_selecionada.tamanho = min(200, forma_selecionada.tamanho + 2)
if teclas[pygame.K_t]: forma_selecionada.tamanho = max(30, forma_selecionada.tamanho - 2)
""",
            },
            {
                "titulo": "6. Transformações do objeto 3D — rotação por matriz e projeção 2D",
                "cor": paleta["acento_amarelo"],
                "texto": "O artefato 3D usa vértices com coordenadas x, y e z. Primeiro os pontos são rotacionados nos eixos X e Y usando seno e cosseno; depois são projetados na tela 2D e desenhados por faces.",
                "codigo": """
# Rotação no eixo X
rad_x = np.radians(self.rot_x)
y1 = py * np.cos(rad_x) - pz * np.sin(rad_x)
z1 = py * np.sin(rad_x) + pz * np.cos(rad_x)

# Rotação no eixo Y
rad_y = np.radians(self.rot_y)
x2 = px * np.cos(rad_y) + z1 * np.sin(rad_y)
z2 = -px * np.sin(rad_y) + z1 * np.cos(rad_y)

# Projeção para a tela 2D
rx = int(x2 * self.escala) + centro_x
ry = int(y1 * self.escala) + centro_y
pontos_2d.append((rx, ry))

# Desenho das faces com sombreamento simples
pygame.draw.polygon(superficie, cor_face, pontos_2d)
""",
            },
            {
                "titulo": "7. Ordem das faces — algoritmo do pintor no 3D",
                "cor": paleta["acento_roxo"],
                "texto": "Para o objeto 3D parecer sólido, as faces são ordenadas pela profundidade média no eixo Z. As faces mais distantes são desenhadas primeiro e as mais próximas ficam por cima.",
                "codigo": """
lista_ordenada = []
for indices, sombreamento in faces:
    z_medio = np.mean([v_rot[idx][2] for idx in indices])
    lista_ordenada.append((z_medio, indices, sombreamento))

# reverse=True: desenha do fundo para a frente
lista_ordenada.sort(key=lambda item: item[0], reverse=True)

for z_m, indices, somb in lista_ordenada:
    pontos_2d = montar_pontos_da_face(indices)
    pygame.draw.polygon(superficie, cor_face, pontos_2d)
""",
            },
            {
                "titulo": "8. Fluxo geral no sandbox",
                "cor": paleta["acento_roxo"],
                "texto": "No sandbox, primeiro a cena é montada em uma Surface do Pygame. Depois ela vira matriz NumPy/OpenCV em BGR, recebe filtros, ajustes e histograma, e por fim volta para Surface para ser exibida na tela.",
                "codigo": """
# 1) Desenha a cena no Pygame
surf_estagio = pygame.Surface((LARGURA, ALTURA_JOGO))
formas_e_objeto_3d.desenhar(surf_estagio)

# 2) Converte para matriz para processar com OpenCV/NumPy
textura_jogo = pygame.surfarray.array3d(surf_estagio)
matriz_jogo = np.transpose(textura_jogo, (1, 0, 2))
matriz_cena = cv2.cvtColor(matriz_jogo, cv2.COLOR_RGB2BGR)

# 3) Aplica filtros e devolve para a tela
surface_render = ins_img.converter_matriz_para_surface(matriz_cena)
tela.blit(surface_render, (0, 0))
""",
            },
        ]

        altura_tmp = 5600
        conteudo = pygame.Surface((largura_conteudo, altura_tmp), pygame.SRCALPHA)
        y = 0

        for secao in secoes:
            titulo_linhas = quebrar_texto(secao["titulo"], self.fonte_conceito_titulo, largura_conteudo - 36)
            texto_linhas = quebrar_texto(secao["texto"], self.fonte_conceito_texto, largura_conteudo - 44)
            codigo_linhas = linhas_codigo(secao["codigo"])

            altura_titulo = len(titulo_linhas) * 30
            altura_texto = len(texto_linhas) * 23
            altura_codigo = max(36, len(codigo_linhas) * 21 + 22)
            altura_card = 24 + altura_titulo + 10 + altura_texto + 14 + altura_codigo + 24

            rect_card = pygame.Rect(0, y, largura_conteudo - 4, altura_card)
            pygame.draw.rect(conteudo, paleta["painel"], rect_card, border_radius=12)
            pygame.draw.rect(conteudo, paleta["borda"], rect_card, width=1, border_radius=12)
            pygame.draw.rect(conteudo, secao["cor"], (0, y, 8, altura_card), border_radius=6)

            py = y + 16
            for linha in titulo_linhas:
                conteudo.blit(self.fonte_conceito_titulo.render(linha, True, paleta["texto"]), (20, py))
                py += 30

            py += 4
            for linha in texto_linhas:
                conteudo.blit(self.fonte_conceito_texto.render(linha, True, paleta["texto_suave"]), (20, py))
                py += 23

            py += 10
            rect_code = pygame.Rect(18, py, largura_conteudo - 42, altura_codigo)
            pygame.draw.rect(conteudo, paleta["painel_alt"], rect_code, border_radius=8)
            pygame.draw.rect(conteudo, paleta["borda"], rect_code, width=1, border_radius=8)

            cy = py + 12
            cor_codigo = (16, 138, 88) if self.tema_claro else (118, 213, 163)
            for linha in codigo_linhas:
                conteudo.blit(self.fonte_conceito_codigo.render(linha, True, cor_codigo), (32, cy))
                cy += 21

            y += altura_card + 18

        altura_conteudo = max(area_visivel.height, y + 6)
        self.scroll_conceitos_max = max(0, altura_conteudo - area_visivel.height)
        self.scroll_conceitos = max(0, min(self.scroll_conceitos, self.scroll_conceitos_max))

        pygame.draw.rect(superficie, paleta["painel_alt"], area_visivel.inflate(10, 10), border_radius=12)
        pygame.draw.rect(superficie, paleta["borda"], area_visivel.inflate(10, 10), width=1, border_radius=12)

        janela = pygame.Rect(0, self.scroll_conceitos, area_visivel.width, area_visivel.height)
        superficie.blit(conteudo, area_visivel.topleft, janela)

        # Barra de rolagem visual
        barra = pygame.Rect(self.largura - 34, area_visivel.y, 8, area_visivel.height)
        pygame.draw.rect(superficie, paleta["borda"], barra, border_radius=4)
        if altura_conteudo > area_visivel.height:
            proporcao = area_visivel.height / altura_conteudo
            thumb_h = max(36, int(area_visivel.height * proporcao))
            thumb_y = area_visivel.y + int((area_visivel.height - thumb_h) * (self.scroll_conceitos / self.scroll_conceitos_max))
            pygame.draw.rect(superficie, paleta["titulo"], (barra.x, thumb_y, barra.width, thumb_h), border_radius=4)

        self.desenhar_voltar(superficie, pos_mouse)

    def checar_cliques(self, pos_mouse):
        """Gerencia os cliques e as transições de estado das janelas."""
        if self.estado == "config":
            if self.btn_voltar.collidepoint(pos_mouse):
                self.estado = "menu"
                return {"tipo": "estado", "valor": "menu"}

            if self.btn_volume_menos.collidepoint(pos_mouse):
                self.volume_musica = max(0.0, round(self.volume_musica - self.ajuste_volume, 2))
                return {"tipo": "audio", "volume": self.volume_musica, "mutado": self.musica_mutada}

            if self.btn_volume_mais.collidepoint(pos_mouse):
                self.volume_musica = min(1.0, round(self.volume_musica + self.ajuste_volume, 2))
                return {"tipo": "audio", "volume": self.volume_musica, "mutado": self.musica_mutada}

            if self.rect_volume_barra.collidepoint(pos_mouse):
                novo_volume = (pos_mouse[0] - self.rect_volume_barra.x) / self.rect_volume_barra.width
                self.volume_musica = max(0.0, min(1.0, round(novo_volume, 2)))
                return {"tipo": "audio", "volume": self.volume_musica, "mutado": self.musica_mutada}

            if self.btn_mute.collidepoint(pos_mouse):
                self.musica_mutada = not self.musica_mutada
                return {"tipo": "audio", "volume": self.volume_musica, "mutado": self.musica_mutada}

            if self.btn_res_1280.collidepoint(pos_mouse):
                self.indice_resolucao = 0
                return {"tipo": "resolucao", "valor": self.resolucao_atual()}

            if self.btn_res_1366.collidepoint(pos_mouse):
                self.indice_resolucao = 1
                return {"tipo": "resolucao", "valor": self.resolucao_atual()}

            if self.btn_tema_claro.collidepoint(pos_mouse):
                self.tema_claro = True
                return {"tipo": "tema", "valor": self.tema_claro}

            if self.btn_tema_escuro.collidepoint(pos_mouse):
                self.tema_claro = False
                return {"tipo": "tema", "valor": self.tema_claro}

            return None

        if self.estado == "menu":
            if self.btn_iniciar.collidepoint(pos_mouse): self.estado = "sandbox"
            elif self.btn_como_jogar.collidepoint(pos_mouse): self.estado = "como_jogar"
            elif self.btn_config.collidepoint(pos_mouse): self.estado = "config"
            elif self.btn_sobre.collidepoint(pos_mouse): self.estado = "sobre"
            elif self.btn_conceitos.collidepoint(pos_mouse):
                self.estado = "conceitos"
                self.scroll_conceitos = 0
            elif self.btn_sair.collidepoint(pos_mouse):
                pygame.quit()
                sys.exit()
        else:
            # Se estiver em qualquer tela interna, o botão voltar retorna ao menu inicial
            if self.btn_voltar.collidepoint(pos_mouse):
                self.estado = "menu"

        return None