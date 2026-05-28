import cv2
import numpy as np
import pygame
import processamento_imagem as pdi

class LupaFiltro:
    def __init__(self, raio=90):
        self.raio = raio
        self.ativo = False  # Controla se a lupa está ligada ou desligada

    def aplicar_lente_local(self, matriz_cena, mouse_pos, botoes_lens):
        """
        Recorta a região ao redor do mouse, aplica o filtro ativo do OpenCV
        apenas nessa área e devolve a composição final para a cena.
        """
        # Se a lupa não estiver ativa, retorna a cena original sem alterações
        if not self.ativo:
            return matriz_cena

        mx, my = mouse_pos
        altura, largura = matriz_cena.shape[:2]

        # Garante que a lupa só processe se o mouse estiver dentro dos limites da tela de jogo
        if my >= altura or mx >= largura or mx < 0 or my < 0:
            return matriz_cena

        # 1. Cria uma máscara booleana preta do tamanho exato da área de jogo
        mascara = np.zeros((altura, largura), dtype=np.uint8)
        # Desenha o círculo da lupa em branco (255) na posição do mouse
        cv2.circle(mascara, (mx, my), self.raio, 255, -1)

        # 2. Cria uma cópia da imagem original que receberá o processamento local
        imagem_filtrada_local = matriz_cena.copy()

        # 3. Aplica na cena inteira (temporariamente) o filtro selecionado na HUD
        if botoes_lens[0]["ativo"]: 
            imagem_filtrada_local = pdi.aplicar_escala_cinza(imagem_filtrada_local)
        if botoes_lens[1]["ativo"]: 
            imagem_filtrada_local = pdi.aplicar_sobel(imagem_filtrada_local)
        if botoes_lens[2]["ativo"]: 
            imagem_filtrada_local = pdi.aplicar_blur(imagem_filtrada_local)
        if botoes_lens[3]["ativo"]: 
            imagem_filtrada_local = pdi.injetar_ruido_salt_pepper(imagem_filtrada_local)
        if botoes_lens[4]["ativo"]: 
            imagem_filtrada_local = pdi.aplicar_filtro_mediana(imagem_filtrada_local)
        if botoes_lens[5]["ativo"]: 
            imagem_filtrada_local = cv2.bitwise_not(imagem_filtrada_local)

        # 4. O SEGREDO DA ROI: Onde a máscara for 255 (dentro do círculo), usa a imagem com filtro.
        # Onde for 0 (fora do círculo), mantém a imagem original intacta.
        cena_composta = np.where(mascara[:, :, None] == 255, imagem_filtrada_local, matriz_cena)

        return cena_composta

    def desenhar_contorno_hud(self, superficie_pygame, mouse_pos, altura_limite):
        """Desenha a bordinha sutil da lupa para o jogador ver onde ela está na tela."""
        if self.ativo and mouse_pos[1] < altura_limite:
            # Desenha um círculo de contorno branco com 2px de espessura
            pygame.draw.circle(superficie_pygame, (255, 255, 255), mouse_pos, self.raio, 2)