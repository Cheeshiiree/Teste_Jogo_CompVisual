import cv2
import numpy as np
import pygame

class HistogramaInterativo:
    def __init__(self, x, y, largura=200, altura=130):
        self.rect_area = pygame.Rect(x, y, largura, altura)
        self.tom_selecionado = None  # Eixo X: Tom alvo (0-255)
        self.fator_escala = 1.0      # Eixo Y: Multiplicador (0.0 a 2.0)
        self.arrastando = False      
        self.fonte_p = pygame.font.SysFont("Arial", 11, bold=True)

    def calcular_e_desenhar(self, superficie_pygame, imagem_bgr):
        """Calcula o histograma real da cena via OpenCV e plota na HUD do Pygame."""
        surf_hist = pygame.Surface((self.rect_area.width, self.rect_area.height))
        surf_hist.fill((10, 10, 12))
        
        # Desenha linhas de grade horizontais discretas
        for h_linha in range(20, self.rect_area.height - 15, 25):
            pygame.draw.line(surf_hist, (30, 30, 35), (0, h_linha), (self.rect_area.width, h_linha), width=1)
        
        cores_canais = ('b', 'g', 'r')
        cores_pygame = [(50, 50, 255), (50, 255, 50), (255, 50, 50)]
        
        for i, col in enumerate(cores_canais):
            hist = cv2.calcHist([imagem_bgr], [i], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, self.rect_area.height - 20, cv2.NORM_MINMAX)
            
            pontos = []
            for x_tom in range(256):
                px = int(x_tom * (self.rect_area.width / 256))
                py = (self.rect_area.height - 15) - int(hist[x_tom][0])
                pontos.append((px, py))
                
            if len(pontos) > 1:
                pygame.draw.lines(surf_hist, cores_pygame[i], False, pontos, 1)
        
        # 🎯 SELEÇÃO EIXO X e EIXO Y ACTIVOS
        if self.tom_selecionado is not None:
            px_selecionado = int(self.tom_selecionado * (self.rect_area.width / 256))
            
            # 1. Linha Vertical Amarela (Mapeamento do Tom)
            pygame.draw.line(surf_hist, (255, 215, 0), (px_selecionado, 0), (px_selecionado, self.rect_area.height - 15), width=2)
            
            # 2. Linha Horizontal Dinâmica baseada no Fator de Escala atual
            # Converte o fator de escala de volta para pixels locais para desenhar a linha estável
            py_escala = int((self.rect_area.height - 15) * (1.0 - (self.fator_escala / 2.0)))
            py_escala = max(0, min(py_escala, self.rect_area.height - 15))
            pygame.draw.line(surf_hist, (255, 215, 0), (0, py_escala), (self.rect_area.width, py_escala), width=1)

            # 3. Texto do Rodapé com o feedback estatístico duplo
            txt_tom = self.fonte_p.render(f"TOM: {self.tom_selecionado} | GANHO: {int(self.fator_escala * 100)}%", True, (255, 215, 0))
            surf_hist.blit(txt_tom, (6, self.rect_area.height - 14))
        else:
            txt_padrao = self.fonte_p.render("CLIQUE / ARRASTE EM 2D NO GRÁFICO", True, (120, 120, 125))
            surf_hist.blit(txt_padrao, (6, self.rect_area.height - 14))

        superficie_pygame.blit(surf_hist, (self.rect_area.x, self.rect_area.y))
        pygame.draw.rect(superficie_pygame, (90, 90, 100), self.rect_area, width=1, border_radius=3)

    def checar_clique(self, mouse_pos):
        """Ativa o arraste se o usuário clicar com o botão esquerdo dentro do gráfico."""
        if self.rect_area.collidepoint(mouse_pos):
            self.arrastando = True
            self.atualizar_dados_por_posicao(mouse_pos)
            return self.tom_selecionado
        return None

    def atualizar_arraste(self, mouse_pos, mouse_botoes):
        """Atualiza continuamente o tom (X) e o ganho (Y) se o usuário mover o mouse segurando o clique."""
        if self.arrastando:
            if not mouse_botoes[0]:
                self.arrastando = False
                return
            self.atualizar_dados_por_posicao(mouse_pos)

    def atualizar_dados_por_posicao(self, mouse_pos):
        """Calcula o Tom Alvo (Eixo X) e o Fator de Escala (Eixo Y)."""
        # A. CÁLCULO DO EIXO X (Tom: 0 a 255)
        x_restrito = max(self.rect_area.x, min(mouse_pos[0], self.rect_area.right))
        x_relativo = x_restrito - self.rect_area.x
        self.tom_selecionado = int((x_relativo / self.rect_area.width) * 255)
        self.tom_selecionado = max(0, min(self.tom_selecionado, 255))
        
        # B. CÁLCULO DO EIXO Y (Ganho: 0.0 a 2.0)
        # Limita a leitura vertical na área útil do gráfico
        y_restrito = max(self.rect_area.y, min(mouse_pos[1], self.rect_area.y + self.rect_area.height - 15))
        y_relativo = y_restrito - self.rect_area.y
        
        # Inverte a proporção (porque no Pygame Y=0 é o topo e nós queremos que o topo seja o ganho máximo)
        proporcao_vertical = 1.0 - (y_relativo / (self.rect_area.height - 15))
        self.fator_escala = float(proporcao_vertical * 2.0) # Varia de 0.0 a 2.0