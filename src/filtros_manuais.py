import numpy as np

def aplicar_pixelar_manual(imagem_bgr, tamanho_bloco=12):
    """
    Filtro de Mosaico (Pixelate) 100% Manual.
    Conceito: Divide a imagem em blocos espaciais (ex: 12x12). Calcula a cor média 
    de todos os pixels dentro daquele bloco e pinta o bloco inteiro com essa cor única.
    Isso reduz a resolução espacial (subamostragem) criando o efeito pixelado.
    """
    # Extrai as dimensões da matriz original
    alt, larg, canais = imagem_bgr.shape
    
    # Cria uma matriz em branco (preta) com o mesmo tamanho para receber a nova imagem
    resultado = np.zeros((alt, larg, canais), dtype=np.uint8)

    # Varre a imagem saltando de bloco em bloco
    for y in range(0, alt, tamanho_bloco):
        for x in range(0, larg, tamanho_bloco):
            
            # Delimita as coordenadas do bloco atual garantindo que não saia dos limites da tela
            limite_y = min(y + tamanho_bloco, alt)
            limite_x = min(x + tamanho_bloco, larg)
            
            # Recorta a região de vizinhança na imagem original
            bloco = imagem_bgr[y:limite_y, x:limite_x]
            
            # Calcula a média matemática das cores (R, G, B) de todos os pixels dentro desse bloco
            cor_media = np.mean(bloco, axis=(0, 1))
            
            # Preenche o espaço equivalente na imagem de resultado com essa cor média
            resultado[y:limite_y, x:limite_x] = cor_media

    return resultado


def aplicar_ruido_rgb_manual(imagem_bgr, intensidade=50):
    """
    Filtro de Ruído Aditivo RGB 100% Manual.
    Conceito: Em vez do ruído Sal e Pimenta (que joga pixels brancos ou pretos absolutos),
    este algoritmo gera valores aleatórios (positivos e negativos) independentes para cada 
    canal de cor e soma ao pixel original, criando uma interferência estática colorida.
    """
    # Converte a matriz para float32. Isso é obrigatório na matemática de PDI para
    # impedir que a soma estoure o limite de 255 e cause anomalias visuais antes do clip.
    resultado = imagem_bgr.astype(np.float32)
    alt, larg, canais = resultado.shape
    
    # Gera uma matriz de ruído do exato tamanho da imagem.
    # Os valores sorteados variam entre -intensidade e +intensidade.
    ruido = np.random.uniform(-intensidade, intensidade, (alt, larg, canais))
    
    # Adiciona o ruído diretamente aos canais B, G e R da imagem
    resultado += ruido
    
    # Trava (clip) os valores matemáticos para nunca passarem de 255 nem caírem abaixo de 0.
    # Depois, devolve para o formato uint8 (8-bits padrão de imagem digital).
    resultado = np.clip(resultado, 0, 255).astype(np.uint8)
    
    return resultado