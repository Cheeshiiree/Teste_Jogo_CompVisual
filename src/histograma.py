import cv2
import numpy as np
import pygame

class HistogramaInterativo:
    def __init__(self, x, y, largura=200, altura=130):
        self.rect_area = pygame.Rect(x, y, largura, altura)
        self.tom_selecionado = None # Guarda o tom (0-255) que o usuário clicou
        self.fonte_p = pygame.font.SysFont("Arial", 11, bold=True)

    def calcular_e_desenhar(self, superficie_pygame, imagem_bgr):
        """Calcula o histograma real e desenha o gráfico na tela."""
        # Cria uma superfície interna preta para o gráfico
        surf_hist = pygame.Surface((self.rect_area.width, self.rect_area.height))
        surf_hist.fill((10, 10, 12))
        
        cores_canais = ('b', 'g', 'r')
        cores_pygame = [(50, 50, 255), (50, 255, 50), (255, 50, 50)]
        
        # Calcula o histograma para cada canal (RGB)
        for i, col in enumerate(cores_canais):
            hist = cv2.calcHist([imagem_bgr], [i], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, self.rect_area.height - 15, cv2.NORM_MINMAX)
            
            pontos = []
            for x_tom in range(256):
                px = int(x_tom * (self.rect_area.width / 256))
                py = (self.rect_area.height - 15) - int(hist[x_tom][0])
                pontos.append((px, py))
                
            if len(pontos) > 1:
                pygame.draw.lines(surf_hist, cores_pygame[i], False, pontos, 1)
        
        # Se o usuário clicou em algum tom, desenha uma linha amarela vertical indicando a seleção
        if self.tom_selecionado is not None:
            px_selecionado = int(self.tom_selecionado * (self.rect_area.width / 256))
            pygame.draw.line(surf_hist, (255, 215, 0), (px_selecionado, 0), (px_selecionado, self.rect_area.height), width=2)
            
            # Escreve o valor do tom selecionado no rodapé do gráfico
            txt_tom = self.fonte_p.render(f"Tom: {self.tom_selecionado}", True, (255, 215, 0))
            surf_hist.blit(txt_tom, (5, self.rect_area.height - 14))

        # Desenha a superfície montada na tela principal
        superficie_pygame.blit(surf_hist, (self.rect_area.x, self.rect_area.y))
        pygame.draw.rect(superficie_pygame, (90, 90, 100), self.rect_area, width=1) # Borda

    def checar_clique(self, mouse_pos):
        """Verifica se o usuário clicou dentro do histograma e calcula o tom correspondente."""
        if self.rect_area.collidepoint(mouse_pos):
            # Calcula a posição relativa do clique dentro do retângulo (0 até largura)
            x_relativo = mouse_pos[0] - self.rect_area.x
            # Transforma a posição de pixels para a escala de tons de cor (0 a 255)
            self.tom_selecionado = int((x_relativo / self.rect_area.width) * 255)
            return self.tom_selecionado
        return None