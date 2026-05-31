# 📂 Guia de Arquivos e Roadmap do Projeto — Vision Quest
> **Nota do Desenvolvedor:** Criei este guia para alinhar o grupo sobre o que cada arquivo faz, o que já foi construído e o mapa exato do que ainda precisamos implementar para fechar as diretrizes da disciplina de PDI.

---

## 🚦 1. Legenda de Status (Flags de Desenvolvimento)
* 🟢 `[STATUS: Implementado]` — Código finalizado e integrado.
* 🟡 `[STATUS: Em Edição / Protótipo]` — Arquivo funcional em fase de greyboxing ou ajustes.
* 🔵 `[STATUS: Planejado / Aguardando Criação]` — Estrutura mapeada que precisa ser codificada.
* 🔴 `[STATUS: Para Corrigir / Melhorar]` — Bug ou limitação técnica identificada que precisa de revisão.

---

## 🗂️ 2. Estrutura Atual dos Arquivos do Projeto

### 🖥️ 2.1 Lógica do Jogo, Menus e Interface (Pygame)

* **`src/main.py`** `[STATUS: 🟢 Implementado]`
  * **O que faz:** Ponto de entrada do jogo. Inicializa a janela e controla o loop de eventos principal.

* **`src/player.py`** `[STATUS: 🟡 Em Edição]`
  * **O que faz:** Gerencia o personagem, colisão física em plataformas e animações de sprites.

* **`src/menu/config.py`** `[STATUS: 🟢 Implementado]`
  * **O que faz:** Guarda as constantes de sistema (Resolução HD $1280 \times 720$, taxa de FPS e fontes).

* **`src/ui.py`** `[STATUS: 🔴 Para Corrigir / Expandir]`
  * **O que faz:** Controla a interface do usuário. 
  * **O que falta:** O menu atualmente está praticamente não funcional. Precisamos implementar o fluxo de telas real para navegar entre: *Menu Principal*, *Como Jogar (Guias)*, *Configurações*, *Sobre* e a tela de créditos com os *Conceitos de PDI Utilizados*.

---

### 🎨 2.2 Motores de Processamento de Imagem e Estatística (OpenCV / NumPy)

* **`src/processamento_imagem.py`** `[STATUS: 🟢 Implementado]`
  * **O que faz:** Biblioteca de funções matemáticas e filtros espaciais (Cinza, Blur, Ruído, Mediana e HSV).

* **`src/filtro_local.py`** `[STATUS: 🟢 Implementado]`
  * **O que faz:** Controla a **Lupa Mágica** de ROI circular em torno do mouse (suporta modo normal e invertido).

* **`src/histograma.py`** `[STATUS: 🔴 Para Corrigir]`
  * **O que faz:** Desenha o gráfico de distribuição de canais BGR na HUD através do clique do mouse.
  * **O que falta:** Atualmente ele só seleciona verticalmente de forma estática. Precisamos corrigir a interatividade para permitir o clique e arraste contínuo para seleção dinâmica de faixas de tons e adicionar a linha horizontal para precisão de leitura.

* **`src/logger_pdi.py`** `[STATUS: 🔴 Para Corrigir / Expandir]`
  * **O que faz:** Ferramenta de auditoria científica que gera o arquivo `historico_pdi.json`.
  * **O que falta:** Atualmente ele só guarda os dados isolados no instante do Reset. Precisamos expandir o sistema de logging para gravar o histórico completo de toda a sessão de testes do usuário (quais filtros ligou, quais transformações fez e quando clicou no histograma), criando um relatório completo para mostrar para a professora.

---

## 🧱 3. Mapeamento dos Scripts de Greyboxing (Laboratório)
Scripts isolados usados para validar as funções mais relevantes da disciplina que serão transportadas para o jogo final:

* 📐 **`src/greyboxing5.py` (Mecânica 3D via PyOpenGL):** `[STATUS: 🟢 Implementado]`
  * **Relevância:** Explora a integração 2D/3D. Renderiza um cubo giratório e calcula a projeção de um item 3D (pirâmide amarela) em sua face, detectando colisões de cliques do mouse 2D na projeção tridimensional do mundo para coletar o item.
* 🎥 **`src/greyboxing6.py` (Câmera Sidescrolling e Splash Screen):** `[STATUS: 🟢 Implementado]`
  * **Relevância:** Contém a tela inicial de Splash animada em ticks e o sistema de câmera móvel por deslocamento que segue a posição X do player pelo mapa.
* 🎛️ **`src/greyboxing8.py` (Central de Filtros e Transformações):** `[STATUS: 🟢 Implementado]`
  * **Relevância:** Valida a inversão inteligente dos sliders (Modo Objeto Local vs Modo Cena Global), inputs de teclado para Rotação (Q/E), Escala (R/T), Translação (Setas) e teclas de atalho de Debug (`X` e `Z`).

---

## 🚀 4. Módulos Futuros e Mapa de Desafios (O que falta fazer)

Para cumprir todas as diretrizes obrigatórias da UNIFEI, o projeto será expandido com os seguintes módulos:

### 🎮 4.1 Estruturas de Gameplay
* **`src/level.py`** `[STATUS: 🔵 Planejado]` — Interpretador que carregará o mapa das fases e posicionará os itens e objetivos através de matrizes.
* **`src/coletaveis.py`** `[STATUS: 🔵 Planejado]` — Lógica para as chaves e estruturas que o jogador precisa encontrar e recolher para progredir.
* **`src/inserir_imagens.py`** `[STATUS: 🔵 Planejado]` — Módulo responsável por carregar texturas e imagens customizadas do cenário ao invés das formas geométricas puras do laboratório.

### 🔬 4.2 Diretriz Obrigatória: Algoritmo Implementado "Na Mão"
* **`src/sobel_manual.py`** `[STATUS: 🔵 Planejado]`
  * **O que é:** Conforme as regras do projeto, precisamos de uma função construída do zero, sem usar o OpenCV. Implementaremos a **Convolução de Matrizes Manual** usando o NumPy para replicar o Operador Sobel de detecção de linhas através das máscaras clássicas de gradiente:
    $$Gx = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad Gy = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$

### 🧩 4.3 Mapeamento dos 5 Desafios Visuais do Jogo
Para estruturar o progresso linear do jogo, o mapa será dividido em 5 salas de quebra-cabeças técnicos:
1. **Desafio 1 (Brilho e Contraste):** Plataformas invisíveis camufladas com o mesmo tom do fundo (baixo contraste) que só ganham colisão física quando o jogador binariza a tela usando os sliders de ganho.
2. **Desafio 2 (Filtro Sobel Manual):** Barreiras ou chaves ocultas que só revelam seus contornos físicos quando o jogador ativa o modo de visão de contornos (Sobel desenvolvido na mão).
3. **Desafio 3 (Restauração Espacial):** Uma área corrompida por ruído Salt & Pepper que bloqueia a visão do jogador e causa dano contínuo; o quebra-cabeça é resolvido ativando o Filtro de Mediana local com a Lupa para limpar o caminho seguro.
4. **Desafio 4 (Manipulação de Cores e Histograma):** Lasers coloridos que impedem a passagem. O jogador deve clicar na cor correspondente do laser diretamente no Histograma BGR para neutralizar a barreira linear.
5. **Desafio 5 (Inspeção e Transformação Geométrica 3D):** Um pedestal que ativa um objeto 3D do PyOpenGL. O jogador deve rotacionar, mudar a escala e transladar o artefato tridimensional para alinhar sua sombra com o padrão da parede e abrir o portão final.