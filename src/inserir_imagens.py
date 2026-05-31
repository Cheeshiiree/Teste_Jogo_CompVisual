import cv2
import numpy as np
import pygame
import tkinter as tk
from tkinter import filedialog

def carregar_e_preparar_matriz(caminho_imagem):
    """Carrega uma imagem do disco via OpenCV, garantindo que ela vire uma matriz BGR."""
    matriz_bruta = cv2.imread(caminho_imagem, cv2.IMREAD_UNCHANGED)
    if matriz_bruta is None:
        print(f"Aviso: Não foi possível carregar a imagem em '{caminho_imagem}'")
        return None
    return matriz_bruta

def converter_matriz_para_surface(matriz_bgr_or_bgra):
    """Converte com segurança uma matriz do OpenCV (NumPy BGR/BGRA) em uma Surface do Pygame."""
    if matriz_bgr_or_bgra is None:
        return None

    if len(matriz_bgr_or_bgra.shape) > 2 and matriz_bgr_or_bgra.shape[2] == 4:
        imagem_rgb = cv2.cvtColor(matriz_bgr_or_bgra, cv2.COLOR_BGRA2RGBA)
        pixel_array = np.transpose(imagem_rgb, (1, 0, 2))
        surface = pygame.surfarray.make_surface(pixel_array)
        return surface.convert_alpha()
    else:
        imagem_rgb = cv2.cvtColor(matriz_bgr_or_bgra, cv2.COLOR_BGR2RGB)
        pixel_array = np.transpose(imagem_rgb, (1, 0, 2))
        surface = pygame.surfarray.make_surface(pixel_array)
        return surface.convert()

def carregar_background_pdi(caminho_imagem, largura_alvo, altura_alvo):
    """Carrega a imagem de fundo e já a redimensiona usando o OpenCV."""
    matriz = carregar_e_preparar_matriz(caminho_imagem)
    if matriz is not None:
        if len(matriz.shape) > 2 and matriz.shape[2] == 4:
            matriz = matriz[:, :, :3]
        matriz_redimensionada = cv2.resize(matriz, (largura_alvo, altura_alvo), interpolation=cv2.INTER_AREA)
        return matriz_redimensionada # <- Corrigido: Retorno adicionado com sucesso!
    return None
    
def selecionar_arquivo_background(largura_alvo, altura_alvo):
    """Abre uma janela nativa do sistema para escolher qualquer imagem do computador."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    caminho_escolhido = filedialog.askopenfilename(
        title="Selecione a Imagem de Fundo para o Laboratório PDI",
        filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp")]
    )
    root.destroy()

    if caminho_escolhido:
        print(f"Imagem selecionada com sucesso: {caminho_escolhido}")
        matriz = cv2.imread(caminho_escolhido, cv2.IMREAD_UNCHANGED)
        if matriz is not None:
            if len(matriz.shape) > 2 and matriz.shape[2] == 4:
                matriz = matriz[:, :, :3]
            matriz_redimensionada = cv2.resize(matriz, (largura_alvo, altura_alvo), interpolation=cv2.INTER_AREA)
            return matriz_redimensionada
            
    return None