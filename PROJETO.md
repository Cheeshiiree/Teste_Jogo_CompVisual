# 🎮 Vision Quest — Documentação Oficial do Projeto

>  **Ambiente Acadêmico:** Universidade Federal de Itajubá (UNIFEI)

>  **Contexto:** Disciplina de Computação Visual / Processamento Digital de Imagens (PDI)

>  **Tecnologias Base:** Python 3, Pygame, OpenCV (cv2) e NumPy

>  **Fase Atual:** Prototipagem de Mecânicas Centrais (Greyboxing 8 Concluído)

  

---

  

## 📑 1. Visão Geral do Jogo & Justificativa Científica

  

### 🧠 1.1 O Conceito do Jogo

**Vision Quest** é um jogo de aventura e quebra-cabeças ópticos em plataforma 2D. A narrativa e as mecânicas giram em torno de um mundo cujas estruturas, perigos e caminhos foram corrompidos por ruídos matemáticos e distorções de frequência. O jogador assume o papel de um cientista visual que precisa interagir com o ambiente e modificar o seu próprio espectro de visão utilizando ferramentas baseadas em **filtros de Processamento Digital de Imagens (PDI)** para revelar plataformas camufladas, limpar interferências e desvendar puzzles.

  

### 🔬 1.2 Justificativa Acadêmica (O Porquê do Projeto)

Em ambientes de graduação, o ensino de Computação Visual e PDI costuma ser restrito a softwares estáticos de manipulação de fotos (como filtros de realce em imagens médicas ou de satélite). O *Vision Quest* inverte esse paradigma ao transformar conceitos abstratos de álgebra linear e matrizes em **laços dinâmicos de jogabilidade (gameplay loops)**.

  

* **A Matriz como Cenário:** O jogo demonstra na prática que uma imagem digitalizada nada mais é do que uma matriz tridimensional de pixels $f(x, y) = [R, G, B]$.

* **O Ruído como Obstáculo:** Fatores de degradação de imagem (como ruído impulsivo) tornam-se barreiras físicas no cenário.

* **A Convolução como Solução:** Filtros de vizinhança espacial (máscaras de convolução) funcionam como as chaves mecânicas para limpar o cenário e permitir o avanço do jogador.

  

---

  

## 🛠️ 2. Estado Atual do Desenvolvimento (O Que Já Foi Feito)

  

Até o momento, o grupo consolidou a arquitetura do motor e validou todas as diretrizes fundamentais por meio de **scripts de Greyboxing**. O estado atual do código conta com:

  

* **🧱 Modularização de Código (Clean Architecture):** Separação completa entre a renderização gráfica do jogo (`greyboxing8.py`) e o motor matemático de processamento de matrizes (`processamento_imagem.py`).

* **🖥️ Interface Humana Expandida (HD - 1280x720):** Substituição da antiga janela espremida por uma resolução moderna de alta definição, permitindo o encaixe perfeito de painéis e menus sem poluição visual.

* **🎯 Controle de Escopo Contextual (Regra de Ouro):**  * **Modo Objeto (Local):** Ao clicar em um sólido geométrico (retângulo, círculo ou triângulo), ele ganha foco com uma borda amarela de destaque. Os sliders de canais $R, G, B$ modificam as propriedades exclusivas daquela forma.

* **Modo Cena (Global):** Se o jogador clicar no fundo vazio do cenário, nenhuma forma fica em foco e os sliders passam a aplicar os filtros de Brilho, Contraste e Saturação sobre o buffer completo da imagem da tela.

* **📊 Histograma em Tempo Real:** Integração de uma rotina baseada em `cv2.calcHist()` que captura a matriz da tela de jogo a cada frame, calcula a distribuição de tons e plota um gráfico de linhas coloridas para os canais Azul, Verde e Vermelho diretamente na HUD.

* **⚡ Laboratório de Filtros Funcionais:** Botões estilizados mapeados com efeitos reais do OpenCV (Escala de Cinza, Sobel, Blur Gaussiano, Injeção de Ruído Salt & Pepper e Restauração por Filtro de Mediana).

  

---

  

## 🚀 3. Funcionalidades Planejadas & Mapeamento de Diretrizes

  

O projeto foi estruturado para cobrir o plano de ensino da disciplina de forma integral:

  

### 🎨 3.1 Operações de Intensidade e Espaço de Cor

* [x]  **Manipulação de Canais Isolados:** Alteração direta dos valores de cor através da separação e junção de canais RGB da forma selecionada.

* [x]  **Controle de Brilho Dinâmico:** Operações ponto a ponto somando ou subtraindo uma constante escalar da matriz ($f(x,y) + c$).

* [x]  **Ajuste de Contraste:** Multiplicação dos tons por um fator de ganho alfa ($\alpha \cdot f(x,y)$) para binarização e revelação de blocos camuflados.

* [x]  **Saturação no Espaço HSV:** Extração do canal *S* (Saturation) após converter a matriz BGR original para o espaço de cor HSV usando o OpenCV.

  

### 📐 3.2 Transformações Geométricas

Com um objeto em foco, o jogador consegue aplicar matrizes de transformação geométrica em tempo real através do teclado:

* [x]  **Translação:** Deslocamento espacial linear nos eixos X e Y usando as setas direcionais.

* [x]  **Escala:** Alteração proporcional e isométrica do tamanho dos vértices dos objetos através das teclas `R` (+) e `T` (-).

* [x]  **Rotação:** Multiplicação por matrizes trigonométricas de rotação angular ao redor do pivô central do objeto usando as teclas `Q` e `E`.

  

### 🔍 3.3 Filtros de Frequência, Ruído e Restauração

* [x]  **Filtros Passa-Baixa (Suavização):** Aplicação de um Kernel Gaussiano (`cv2.GaussianBlur`) para simular perda de foco da visão.

* [x]  **Filtros Passa-Alta (Realce):** Operador Sobel para detecção de gradientes verticais e horizontais, transformando blocos sólidos em linhas de contorno.

* [x]  **Ruído Impulsivo:** Algoritmo customizado em NumPy que injeta aleatoriamente pixels brancos (255) e pretos (0) para simular interferências estáticas na tela.

* [x]  **Filtro de Restauração (Mediana):** Injeção do operador de Mediana espacial (`cv2.medianBlur`) como mecânica de contra-ataque para eliminar completamente o ruído de Sal e Pimenta, provando a teoria de ordenação de vizinhança.

  

---

  

## ⏳ 4. Próximos Passos (O Que Falta Fazer)

  

Para transformar o nosso laboratório técnico em um jogo fluido e apresentável para a banca da UNIFEI, o grupo focará nas seguintes tarefas:

  

1. **👁️ A Lupa de Filtros (ROI - Region of Interest):** Desenvolver uma máscara lógica em NumPy para restringir a aplicação dos filtros do OpenCV apenas a uma área circular ao redor do mouse, funcionando como uma "lente de inspeção portátil".

2. **🔀 Fluxo de Telas (Game States):** Integrar a Splash Screen animada (carregando a imagem da caixa de suprimentos) com o Menu Principal e a tela de transição de níveis.

3. **🏃 Física de Plataforma (Sidescrolling):** Mesclar o sistema de câmera móvel (desenvolvido no Greybox 6) com um motor simples de gravidade, pulo e colisão de caixas para o jogador andar pelo mapa.

4. **🎨 Importação de Sprites Oficiais:** Substituir os blocos cinzas temporários de teste pelos arquivos de arte finais (`icon_janela.png`, frames do personagem, cenários de fundo).

  

---

  

## 📂 5. Organização Arquitetural do Repositório

  

O projeto segue rigorosamente a árvore de diretórios padrão de desenvolvimento profissional de jogos:

  

```text

Teste_Jogo_CompVisual/

│

├── .venv/ # Ambiente virtual isolado do Python

├── .gitignore # Filtro do Git (ignora bibliotecas pesadas e caches)

│

├── assets/ # Repositório central de arquivos de mídia

│ ├── bgm/ # Trilhas sonoras de fundo (Background Music)

│ ├── sfx/ # Efeitos sonoros de interações (Sound Effects)

│ └── sprites/ # Elementos visuais e gráficos do jogo

│ ├── background/ # Camadas de imagem para o fundo parallax

│ ├── player/ # Folhas de sprites e animações do personagem

│ ├── challenges/ # Obstáculos, espinhos e perigos (antiga pasta enemy)

│ ├── anims/ # Sequências de animações gerais do mundo

│ └── misc/ # Ícones da janela, artes da splash screen e rascunhos

│

├── src/ # Código-fonte oficial do produto final

│ ├── main.py # Ponto de entrada e gerenciador de estados do jogo

│ ├── player.py # Lógica de física, gravidade e movimentação do boneco

│ └── processamento_imagem.py # Funções puras e isoladas de OpenCV, NumPy e PDI

│

├── greyboxing/ # Laboratório de engenharia (Scripts de validação)

│ ├── greyboxing1_to_5.py # Testes de janelas, cliques de mouse e PyOpenGL 3D

│ ├── greyboxing6.py # Protótipo de câmera sidescrolling e HUD fixa

│ └── greyboxing7.py # Central de PDI,Sliders, Histograma e Filtros (Atual)

│

└── PROJETO.md # Documentação científica atualizada do projeto

  

```

---

## Imagens de esboço

<p align="center">
  <img src="https://drive.google.com/file/d/1DvogP4jvMedU6Od1TuOvR6un5AySzKKO/view?usp=sharing" width="650" alt="Ideia inicial do estilo visual do jogo">
</p>

<p align="center">
  <img src="https://drive.google.com/file/d/15PfUpp2r7RDdI0WTntLcp-C6048KVKGe/view?usp=drive_link" width="650" alt="Design de Interface no Tldraw">
</p>

<p align="center">
  <img src="https://drive.google.com/file/d/1jMGZU0EfWHTGkPUDU5943tboyb5ZCPJX/view?usp=drive_link" width="650" alt="Design de Interface no Tldraw para o ambiente de testes">
</p>
---
