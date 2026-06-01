import numpy as np
import cv2

def aplicar_sobel_manual(imagem_bgr):
    """
    Aplica o operador Sobel de forma 100% manual (via Convolução 2D)
    conforme as diretrizes teóricas de PDI.
    """
    # 1. Converte a imagem para tons de cinza (Sobel precisa de apenas 1 canal de intensidade)
    if len(imagem_bgr.shape) == 3:
        imagem_cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
    else:
        imagem_cinza = imagem_bgr.copy()
        
    alt, larg = imagem_cinza.shape
    # Cria a matriz de saída preenchida com zeros
    sobel_final = np.zeros((alt, larg), dtype=np.uint8)
    
    # 2. Definição das máscaras clássicas de Sobel (Kernels 3x3)
    kernel_x = np.array([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]], dtype=np.float32)
                         
    kernel_y = np.array([[-1, -2, -1],
                         [ 0,  0,  0],
                         [ 1,  2,  1]], dtype=np.float32)
    
    # 3. Varredura da imagem (Convolução Espacial) desconsiderando as bordas externas (borda de 1 pixel)
    # Convertemos para float32 temporariamente para os cálculos matemáticos não estourarem
    cinza_f = imagem_cinza.astype(np.float32)
    
    for y in range(1, alt - 1):
        for x in range(1, larg - 1):
            # Recorta a vizinhança 3x3 ao redor do pixel atual
            vizinhanca = cinza_f[y-1:y+2, x-1:x+2]
            
            # Operação de Convolução: Multiplicação ponto a ponto somando o total
            grad_x = np.sum(vizinhanca * kernel_x)
            grad_y = np.sum(vizinhanca * kernel_y)
            
            # Magnitude do Gradiente (Teorema de Pitágoras aproximado para performance)
            magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Armazena o valor limitando entre 0 e 255
            sobel_final[y, x] = min(255, max(0, int(magnitude)))
            
    # Devolve a imagem convertida de volta para 3 canais BGR para manter a compatibilidade com o Pygame
    return cv2.cvtColor(sobel_final, cv2.COLOR_GRAY2BGR)