import cv2
import numpy as np

def aplicar_escala_cinza(imagem_bgr):
    """Converte a imagem para tons de cinza e mantém os 3 canais para o Pygame."""
    cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)

def aplicar_sobel(imagem_bgr):
    """Aplica o filtro de linha (Operador Sobel) para detecção de bordas."""
    cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.Sobel(cinza, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(cinza, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    magnitude = np.uint8(np.clip(magnitude, 0, 255))
    return cv2.cvtColor(magnitude, cv2.COLOR_GRAY2BGR)

def aplicar_blur(imagem_bgr, intensidade=15):
    """Filtro espacial para desfocar/embaçar a tela (Filtro Gaussiano)."""
    # A intensidade (ksize) deve ser sempre um número ímpar
    if intensidade % 2 == 0: intensity += 1
    return cv2.GaussianBlur(imagem_bgr, (intensidade, intensidade), 0)

def injetar_ruido_salt_pepper(imagem_bgr, quantidade=0.02):
    """Adiciona ruído de sal e pimenta na matriz da imagem."""
    imagem_ruidosa = imagem_bgr.copy()
    # Salt (Branco)
    num_salt = np.ceil(quantidade * imagem_bgr.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in imagem_bgr.shape]
    imagem_ruidosa[coords[0], coords[1], :] = 255
    
    # Pepper (Preto)
    num_pepper = np.ceil(quantidade * imagem_bgr.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in imagem_bgr.shape]
    imagem_ruidosa[coords[0], coords[1], :] = 0
    return imagem_ruidosa

def aplicar_filtro_mediana(imagem_bgr, ksize=5):
    """Filtro de restauração perfeito contra ruído Salt & Pepper."""
    return cv2.medianBlur(imagem_bgr, ksize)

def ajustar_brilho_contraste_saturação(imagem_bgr, brilho=0, contraste=1.0, saturacao=1.0):
    """Aplica transformações de intensidade e espaço de cor (HSV)."""
    # 1. Brilho e Contraste
    imagem_ajustada = cv2.convertScaleAbs(imagem_bgr, alpha=contraste, beta=brilho)
    
    # 2. Saturação (Mudança de espaço de cor para HSV)
    if saturacao != 1.0:
        hsv = cv2.cvtColor(imagem_ajustada, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = np.clip(s * saturacao, 0, 255).astype(np.uint8)
        hsv = cv2.merge([h, s, v])
        imagem_ajustada = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
    return imagem_ajustada

def calcular_histograma_surface(imagem_bgr, largura=150, altura=120):
    """Calcula o histograma e gera uma imagem pronta para o Pygame."""
    import pygame
    # Cria uma superfície preta para o gráfico
    surf_hist = pygame.Surface((largura, altura))
    surf_hist.fill((10, 10, 12))
    
    cores_canais = ('b', 'g', 'r')
    cores_pygame = [(50, 50, 255), (50, 255, 50), (255, 50, 50)]
    
    for i, col in enumerate(cores_canais):
        hist = cv2.calcHist([imagem_bgr], [i], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, altura, cv2.NORM_MINMAX)
        
        # Desenha as linhas do gráfico na superfície do Pygame
        pontos = []
        for x in range(256):
            px = int(x * (largura / 256))
            py = altura - int(hist[x][0])
            pontos.append((px, py))
            
        if len(pontos) > 1:
            pygame.draw.lines(surf_hist, cores_pygame[i], False, pontos, 1)
            
    return surf_hist