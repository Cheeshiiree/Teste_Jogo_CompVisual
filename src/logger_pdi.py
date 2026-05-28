import json
import os
from datetime import datetime
import numpy as np

def salvar_log_experimento(tipo_evento, matriz_antes, matriz_depois, tom_histograma, sliders):
    """
    Registra em um arquivo JSON o estado numérico das matrizes e da HUD antes e depois
    de uma transformação ou reset, carimbado com data e hora.
    """
    caminho_json = "historico_pdi.json"
    
    # 1. Captura carimbo de data e hora atual
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Extrai estatísticas matemáticas da matriz ANTES (Matriz OpenCV BGR)
    media_b_antes = float(np.mean(matriz_antes[:, :, 0]))
    media_g_antes = float(np.mean(matriz_antes[:, :, 1]))
    media_r_antes = float(np.mean(matriz_antes[:, :, 2]))
    
    # Recorte central 3x3 para exemplificar análise de pixel de vizinhança
    h, w = matriz_antes.shape[:2]
    recorte_antes = matriz_antes[h//2-1:h//2+2, w//2-1:w//2+2, 2].tolist() # Canal Vermelho

    # 3. Extrai estatísticas matemáticas da matriz DEPOIS
    media_b_depois = float(np.mean(matriz_depois[:, :, 0]))
    media_g_depois = float(np.mean(matriz_depois[:, :, 1]))
    media_r_depois = float(np.mean(matriz_depois[:, :, 2]))
    recorte_depois = matriz_depois[h//2-1:h//2+2, w//2-1:w//2+2, 2].tolist()

    # 4. Monta o dicionário estruturado com foco nos conceitos da disciplina
    novo_registro = {
        "timestamp": timestamp,
        "evento": tipo_evento,
        "hud_status": {
            "tom_selecionado_histograma": tom_histograma,
            "valores_sliders_porcentagem": {s.nome: f"{int(s.valor * 100)}%" for s in sliders}
        },
        "analise_matriz_cena": {
            "valores_medios_bgr_antes": [round(media_b_antes, 2), round(media_g_antes, 2), round(media_r_antes, 2)],
            "valores_medios_bgr_depois": [round(media_b_depois, 2), round(media_g_depois, 2), round(media_r_depois, 2)],
            "vizinhança_3x3_centro_antes_canal_R": recorte_antes,
            "vizinhança_3x3_centro_depois_canal_R": recorte_depois
        }
    }

    # 5. Carrega o banco pseudo-JSON existente ou cria um novo se não existir
    if os.path.exists(caminho_json):
        try:
            with open(caminho_json, "r", encoding="utf-8") as f:
                dados_banco = json.load(f)
        except:
            dados_banco = []
    else:
        dados_banco = []

    # Adiciona o novo log ao histórico e salva
    dados_banco.append(novo_registro)
    
    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(dados_banco, f, indent=4, ensure_ascii=False)
        
    print(f"Banco PDI Atualizado! Evento [{tipo_evento}] registrado em '{caminho_json}'.")