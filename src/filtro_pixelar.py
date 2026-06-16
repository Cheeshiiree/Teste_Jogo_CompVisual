# -------------------------------------------------------------------------------
# Filtro Pixelar Manual - Função para aplicar a pixelização na cena toda dos 
# greybox recebendo o tamanho do pixel como parâmetro
# -------------------------------------------------------------------------------

import cv2
import sys

def pixelar_manual(imagem, tamanho_pixel):
    """
    Aplica um filtro que deixa a cena pixelada, onde o tamanho do pixel é controlado por um slider.
    A função percorre a imagem em blocos do tamanho especificado e substitui cada bloco pela média de seus pixels.
    Função é chamada a cada movimento do slider, atualizando a cena em tempo real. chamada no arquivo principal

    Parametros:
    - imagem: A imagem a ser pixelada (numpy array).(A cena toda do greybox ou de forma focal com a função lupa)
    - tamanho_pixel: O tamanho do bloco de pixelização (ex: 10 para blocos 10x10). (Valor controlado por slider)

    Retorna:
    - imagem_pixelada: A imagem resultante após a aplicação do filtro de pixelização.
    """

    # Verifica se o tamanho do pixel é válido
    if tamanho_pixel <= 0:
        raise ValueError("O tamanho do pixel deve ser um número inteiro positivo.")

    # Cria uma cópia da imagem para modificar
    imagem_pixelada = imagem.copy()

    # Percorre a imagem em blocos do tamanho especificado
    for y in range(0, imagem.shape[0], tamanho_pixel):
        for x in range(0, imagem.shape[1], tamanho_pixel):
            # Define os limites do bloco
            y_end = min(y + tamanho_pixel, imagem.shape[0])
            x_end = min(x + tamanho_pixel, imagem.shape[1])

            # Calcula a média dos pixels no bloco
            bloco = imagem[y:y_end, x:x_end]
            media_b = int(bloco[:, :, 0].mean())
            media_g = int(bloco[:, :, 1].mean())
            media_r = int(bloco[:, :, 2].mean())

            # Preenche o bloco com a cor média
            imagem_pixelada[y:y_end, x:x_end] = (media_b, media_g, media_r)

    return imagem_pixelada