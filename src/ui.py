import pygame
import sys

class MenuUI:
    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        
        # Estados possíveis: "menu", "sandbox", "como_jogar", "config", "sobre", "conceitos"
        self.estado = "menu"
        
        # Configuração dos botões organizados em duas colunas (Baseado no seu esboço)
        w_btn = 260
        h_btn = 45
        cx_esq = (largura // 2) - w_btn - 15  # Coluna da esquerda
        cx_dir = (largura // 2) + 15         # Coluna da direita
        
        # Linha 1
        self.btn_iniciar = pygame.Rect(cx_esq, 280, w_btn, h_btn)
        self.btn_como_jogar = pygame.Rect(cx_dir, 280, w_btn, h_btn)
        # Linha 2
        self.btn_config = pygame.Rect(cx_esq, 340, w_btn, h_btn)
        self.btn_sobre = pygame.Rect(cx_dir, 340, w_btn, h_btn)
        # Linha 3
        self.btn_conceitos = pygame.Rect(cx_esq, 400, w_btn, h_btn)
        self.btn_sair = pygame.Rect(cx_dir, 400, w_btn, h_btn)
        
        # Botão Voltar universal para as telas internas (Centralizado na parte inferior)
        self.btn_voltar = pygame.Rect((largura // 2) - 100, 600, 200, 45)
        
        # Fontes do sistema
        self.fonte_titulo = pygame.font.SysFont("Arial", 48, bold=True)
        self.fonte_subtitulo = pygame.font.SysFont("Arial", 22, bold=True)
        self.fonte_btn = pygame.font.SysFont("Arial", 18, bold=True)
        self.fonte_texto = pygame.font.SysFont("Arial", 15, bold=True)
        self.fonte_codigo = pygame.font.SysFont("Courier New", 13, bold=True)

    def desenhar_menu(self, superficie, pos_mouse):
        """Desenha a tela de abertura com os 6 botões interativos."""
        superficie.fill((15, 15, 18))
        
        # Título Principal do Painel
        txt_titulo_s = self.fonte_titulo.render("LAB COMPUTAÇÃO VISUAL", True, (10, 50, 100))
        txt_titulo = self.fonte_titulo.render("LAB COMPUTAÇÃO VISUAL", True, (0, 128, 255))
        superficie.blit(txt_titulo_s, ((self.largura // 2) - txt_titulo_s.get_width() // 2 + 3, 133))
        superficie.blit(txt_titulo, ((self.largura // 2) - txt_titulo.get_width() // 2, 130))
        
        def renderizar_botao(rect, texto, cor_foco, pos):
            foco = rect.collidepoint(pos)
            cor = cor_foco if foco else (30, 30, 35)
            pygame.draw.rect(superficie, cor, rect, border_radius=5)
            pygame.draw.rect(superficie, (70, 70, 80), rect, width=2, border_radius=5)
            txt = self.fonte_btn.render(texto, True, (255, 255, 255))
            superficie.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        # Renderização da grade dupla de botões
        renderizar_botao(self.btn_iniciar, "Iniciar Sandbox", (0, 128, 255), pos_mouse)
        renderizar_botao(self.btn_como_jogar, "Como Jogar", (0, 180, 120), pos_mouse)
        renderizar_botao(self.btn_config, "Configurações", (100, 100, 110), pos_mouse)
        renderizar_botao(self.btn_sobre, "Sobre", (255, 215, 0), pos_mouse)
        renderizar_botao(self.btn_conceitos, "Conceitos e Códigos", (150, 50, 200), pos_mouse)
        renderizar_botao(self.btn_sair, "Sair do Programa", (220, 50, 50), pos_mouse)

    def desenhar_voltar(self, superficie, pos_mouse):
        """Desenha o botão de retorno para as sub-telas."""
        foco = self.btn_voltar.collidepoint(pos_mouse)
        cor = (200, 50, 50) if foco else (35, 35, 40)
        pygame.draw.rect(superficie, cor, self.btn_voltar, border_radius=5)
        pygame.draw.rect(superficie, (70, 70, 80), self.btn_voltar, width=1, border_radius=5)
        txt = self.fonte_btn.render("Voltar ao Menu", True, (255, 255, 255))
        superficie.blit(txt, (self.btn_voltar.centerx - txt.get_width() // 2, self.btn_voltar.centery - txt.get_height() // 2))

    def desenhar_como_jogar(self, superficie, pos_mouse):
        superficie.fill((15, 15, 18))
        txt = self.fonte_titulo.render("COMO JOGAR", True, (0, 180, 120))
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
            surf_r = self.fonte_texto.render(r, True, (200, 200, 210))
            superficie.blit(surf_r, (80, y))
            y += 40
        self.desenhar_voltar(superficie, pos_mouse)

    def desenhar_configuracoes(self, superficie, pos_mouse):
        superficie.fill((15, 15, 18))
        txt = self.fonte_titulo.render("CONFIGURAÇÕES", True, (130, 130, 140))
        superficie.blit(txt, ((self.largura // 2) - txt.get_width() // 2, 80))
        # essa parte pode ficar no como jogar
        # Aqui deveriam ficar as configurações mesmo tipo volume, mute e ajustar tamanho da tela caso em 
        # alguma maquina fique desconfigurado
        info = [
            "Resolução Ativa do Projeto: 1280 x 720 (Padrão HD Estável)",
            "Pipeline de Renderização: Matrizes NumPy e Superfícies Pygame (Foco em CPU)",
            "Mapeamento de Cores do Histograma: Canais Independentes [0: Azul, 1: Verde, 2: Vermelho]",
            "Taxa de Quadros Alvo: 60 FPS com VSync via Software",
            "Diretório de Exportação de Logs: Raiz do Projeto (formato JSON estruturado)",
            "Ambiente de Execução Seguro: Analisador Pylance Ativo"
        ]
        y = 220
        for i in info:
            surf_i = self.fonte_texto.render(f"⚙️ {i}", True, (170, 170, 180))
            superficie.blit(surf_i, ((self.largura // 2) - surf_i.get_width() // 2, y))
            y += 45
        self.desenhar_voltar(superficie, pos_mouse)

    def desenhar_sobre(self, superficie, pos_mouse):
        superficie.fill((15, 15, 18))
        txt = self.fonte_titulo.render("SOBRE O PROJETO / AUTORES", True, (255, 215, 0))
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
            "• Rafaela Cristina de Moraes Mendes - 2024009453".
            "--------------------------------------------------------------------------------------------------------",
            "Finalidade: Aplicação prática interdisciplinar demonstrando a unificação de filtros espaciais,",
            "transformações geométricas tridimensionais manuais e análise estatística de histogramas."
        ]
        y = 180
        for d in dados:
            cor = (0, 128, 255) if "UNIFEI" in d else ((255, 215, 0) if "•" in d else (210, 210, 220))
            surf_d = self.fonte_texto.render(d, True, cor)
            superficie.blit(surf_d, ((self.largura // 2) - surf_d.get_width() // 2, y))
            y += 35
        self.desenhar_voltar(superficie, pos_mouse)

    def desenhar_conceitos(self, superficie, pos_mouse):
        superficie.fill((12, 12, 14))
        txt = self.fonte_titulo.render("CONCEITOS & MATEMÁTICA DE PDI", True, (150, 50, 200))
        superficie.blit(txt, ((self.largura // 2) - txt.get_width() // 2, 45))
        
        # Demonstração teórica das fómulas de Convolução e Transformação Exigidas
        superficie.blit(self.fonte_subtitulo.render("1. Filtro Sobel Manual (Gradiente de Bordas)", True, (255, 255, 255)), (60, 120))
        pygame.draw.rect(superficie, (22, 22, 26), (60, 150, 520, 110), border_radius=4)
        linhas_sobel = [
            "Kernel Gx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]",
            "Kernel Gy = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]",
            "Magnitude = sqrt(Gx² + Gy²)",
            "Convolução: F(x,y) = sum(Vizinhança_3x3 * Kernel)"
        ]
        for idx, l in enumerate(linhas_sobel):
            superficie.blit(self.fonte_codigo.render(l, True, (0, 255, 128)), (75, 160 + idx * 22))

        superficie.blit(self.fonte_subtitulo.render("2. Matriz de Projeção e Rotação 3D Livre", True, (255, 255, 255)), (60, 280))
        pygame.draw.rect(superficie, (22, 22, 26), (60, 310, 520, 90), border_radius=4)
        linhas_rot = [
            "Rot_X: y1 = y*cos(θ) - z*sin(θ) | z1 = y*sin(θ) + z*cos(θ)",
            "Rot_Y: x2 = x*cos(ϕ) + z1*sin(ϕ)",
            "Algoritmo do Pintor: Sort_Faces(Z_médio, reverse=True)"
        ]
        for idx, l in enumerate(linhas_rot):
            superficie.blit(self.fonte_codigo.render(l, True, (0, 200, 255)), (75, 320 + idx * 22))

        # Coluna da Direita: Trecho Real do Código NumPy do Grupo
        superficie.blit(self.fonte_subtitulo.render("3. Recorte de Código NumPy do Projeto", True, (255, 255, 255)), (620, 120))
        pygame.draw.rect(superficie, (18, 18, 22), (620, 150, 600, 250), border_radius=4)
        linhas_code = [
            "# Máscara de frequência por canal BGR do Histograma",
            "matriz_cena = matriz_cena.astype(np.float32)",
            "canal_selecionado = matriz_cena[:, :, idx_canal]",
            "mascara = (canal_selecionado >= tom - tol) & \\",
            "          (canal_selecionado <= tom + tol)",
            "",
            "# Aplicação do Ganho Seletivo Bidimensional",
            "matriz_cena[:, :, idx_canal] = np.where(",
            "    mascara, canal_selecionado * ganho, canal_selecionado",
            ")",
            "matriz_cena = np.clip(matriz_cena, 0, 255).astype(np.uint8)"
        ]
        for idx, l in enumerate(linhas_code):
            superficie.blit(self.fonte_codigo.render(l, True, (240, 180, 100)), (635, 160 + idx * 20))

        self.desenhar_voltar(superficie, pos_mouse)

    def checar_cliques(self, pos_mouse):
        """Gerencia os cliques e as transições de estado das janelas."""
        if self.estado == "menu":
            if self.btn_iniciar.collidepoint(pos_mouse): self.estado = "sandbox"
            elif self.btn_como_jogar.collidepoint(pos_mouse): self.estado = "como_jogar"
            elif self.btn_config.collidepoint(pos_mouse): self.estado = "config"
            elif self.btn_sobre.collidepoint(pos_mouse): self.estado = "sobre"
            elif self.btn_conceitos.collidepoint(pos_mouse): self.estado = "conceitos"
            elif self.btn_sair.collidepoint(pos_mouse):
                pygame.quit()
                sys.exit()
        else:
            # Se estiver em qualquer tela interna, o botão voltar retorna ao menu inicial
            if self.btn_voltar.collidepoint(pos_mouse):
                self.estado = "menu"