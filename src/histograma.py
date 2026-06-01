import cv2
import numpy as np
import pygame

class HistogramaInterativo:
    def __init__(self, x, y, largura=200, altura=130):
        self.rect_area = pygame.Rect(x, y, largura, altura)
        self.tom_selecionado = None  # Eixo X (0-255)
        self.fator_escala = 1.0      # Eixo Y (0.0 a 2.0)
        self.canal_ativo = None      # 0: Azul, 1: Verde, 2: Vermelho
        self.arrastando = False      
        self.fonte_p = pygame.font.SysFont("Arial", 11, bold=True)

    def calcular_e_desenhar(self, superficie_pygame, imagem_bgr):
        """Calcula o histograma via OpenCV e projeta as 3 zonas de canais coloridos."""
        surf_hist = pygame.Surface((self.rect_area.width, self.rect_area.height))
        surf_hist.fill((10, 10, 12))
        
        # 🎨 DESENHO DAS 3 PISTAS COLORIDAS (Baseado no seu esboço!)
        largura_pista = self.rect_area.width // 3
        alt_util = self.rect_area.height - 15
        
        # Cores de fundo bem discretas e transparentes para servir de guia de quadrante
        pygame.draw.rect(surf_hist, (10, 10, 40), (0, 0, largura_pista, alt_util))
        pygame.draw.rect(surf_hist, (10, 30, 10), (largura_pista, 0, largura_pista, alt_util))
        pygame.draw.rect(surf_hist, (40, 10, 10), (largura_pista * 2, 0, largura_pista, alt_util))
        
        # Linhas verticais separadoras de canais
        pygame.draw.line(surf_hist, (40, 40, 50), (largura_pista, 0), (largura_pista, alt_util), width=1)
        pygame.draw.line(surf_hist, (40, 40, 50), (largura_pista * 2, 0), (largura_pista * 2, alt_util), width=1)

        # Grades horizontais de amplitude
        for h_linha in range(20, alt_util, 25):
            pygame.draw.line(surf_hist, (25, 25, 30), (0, h_linha), (self.rect_area.width, h_linha), width=1)
        
        cores_canais = ('b', 'g', 'r')
        cores_pygame = [(80, 80, 255), (80, 255, 80), (255, 80, 80)]
        
        # Renderiza as linhas dinâmicas de distribuição de pixels
        for i, col in enumerate(cores_canais):
            hist = cv2.calcHist([imagem_bgr], [i], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, self.rect_area.height - 20, cv2.NORM_MINMAX)
            
            pontos = []
            for x_tom in range(256):
                px = int(x_tom * (self.rect_area.width / 256))
                py = alt_util - int(hist[x_tom][0])
                pontos.append((px, py))
                
            if len(pontos) > 1:
                pygame.draw.lines(surf_hist, cores_pygame[i], False, pontos, 1)
        
        # 🎯 FEEDBACK VISUAL DO CANAL SELECIONADO VIA MOUSE
        if self.tom_selecionado is not None and self.canal_ativo is not None:
            px_selecionado = int(self.tom_selecionado * (self.rect_area.width / 256))
            
            # Linhas guias cruzadas indicando a mira 2D exata
            pygame.draw.line(surf_hist, (255, 215, 0), (px_selecionado, 0), (px_selecionado, alt_util), width=2)
            py_escala = int(alt_util * (1.0 - (self.fator_escala / 2.0)))
            py_escala = max(0, min(py_escala, alt_util))
            pygame.draw.line(surf_hist, (255, 215, 0), (0, py_escala), (self.rect_area.width, py_escala), width=1)

            # Texto do rodapé com o feedback de qual canal está sofrendo PDI
            nomes_canais = ["AZUL (B)", "VERDE (G)", "VERMELHO (R)"]
            txt_status = self.fonte_p.render(f"{nomes_canais[self.canal_ativo]} | TOM: {self.tom_selecionado} | {int(self.fator_escala * 100)}%", True, (255, 215, 0))
            surf_hist.blit(txt_status, (6, self.rect_area.height - 14))
        else:
            txt_padrao = self.fonte_p.render("CLIQUE EM UMA PISTA (B / G / R)", True, (120, 120, 125))
            surf_hist.blit(txt_padrao, (6, self.rect_area.height - 14))

        superficie_pygame.blit(surf_hist, (self.rect_area.x, self.rect_area.y))
        pygame.draw.rect(superficie_pygame, (90, 90, 100), self.rect_area, width=1, border_radius=3)

    def checar_clique(self, mouse_pos):
        """Identifica qual canal foi clicado com base nas terças partes do gráfico."""
        if self.rect_area.collidepoint(mouse_pos):
            self.arrastando = True
            
            # Divide a detecção em 3 quadrantes horizontais
            largura_pista = self.rect_area.width // 3
            x_local = mouse_pos[0] - self.rect_area.x
            
            if x_local < largura_pista:
                self.canal_ativo = 0  # Zona Azul
            elif x_local < largura_pista * 2:
                self.canal_ativo = 1  # Zona Verde
            else:
                self.canal_ativo = 2  # Zona Vermelha
                
            self.atualizar_dados_por_posicao(mouse_pos)
            return self.tom_selecionado
        return None

    def atualizar_arraste(self, mouse_pos, mouse_botoes):
        if self.arrastando:
            if not mouse_botoes[0]:
                self.arrastando = False
                return
            self.atualizar_dados_por_posicao(mouse_pos)

    def atualizar_dados_por_posicao(self, mouse_pos):
        # Mapeamento do Tom Alvo (Eixo X)
        x_restrito = max(self.rect_area.x, min(mouse_pos[0], self.rect_area.right))
        x_relativo = x_restrito - self.rect_area.x
        self.tom_selecionado = int((x_relativo / self.rect_area.width) * 255)
        self.tom_selecionado = max(0, min(self.tom_selecionado, 255))
        
        # Mapeamento do Fator de Escala (Eixo Y)
        y_restrito = max(self.rect_area.y, min(mouse_pos[1], self.rect_area.y + self.rect_area.height - 15))
        y_relativo = y_restrito - self.rect_area.y
        proporcao_vertical = 1.0 - (y_relativo / (self.rect_area.height - 15))
        self.fator_escala = float(proporcao_vertical * 2.0)