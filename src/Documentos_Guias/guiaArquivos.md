# Guia dos arquivos do projeto

## Arquivos Greybox

### Greyboxing
- Esse arquivo contém os códigos relacionados à técnica de greyboxing, que é uma abordagem de design de níveis em jogos onde os níveis são criados usando formas simples e blocos para testar a jogabilidade antes de adicionar detalhes visuais.
- Ele inclui scripts para criar e manipular os níveis de greybox, bem como para testar a jogabilidade e a mecânica do jogo.
- Tomei a liberdade de usar essa técnica para criar uma especie de laboratório para as funções vistas nas aulas sem preucoupação ainda com visual e level design, focando apenas na funcionalidade e mecânica do jogo.

- `Greyboxing.py`:

### Visão Geral do Projeto

Este projeto é um jogo 2D de plataforma que utiliza **Pygame** para a estrutura base (renderização, eventos, etc.) e **OpenCV** para aplicar efeitos de processamento de imagem em tempo real na cena do jogo. A mecânica central envolve o uso de "filtros" de imagem como uma ferramenta para resolver desafios e quebra-cabeças visuais.

### Estrutura dos Arquivos

Abaixo está a descrição dos principais arquivos e diretórios do projeto.

---

#### Arquivos Principais e de Lógica do Jogo

*   **`main.py`** `[STATUS: Implementado]`
    *   **O que faz?** É o coração do jogo, o ponto de entrada principal.
    *   **Responsabilidades:**
        *   Inicializa o Pygame e a janela principal.
        *   Contém o loop de jogo principal, que gerencia eventos, atualiza a lógica e renderiza os gráficos.
        *   **Importante:** É aqui que a "mágica" do PDI (Processamento Digital de Imagens) acontece. A cada quadro, ele captura a tela do jogo, a converte em uma matriz de imagem que o OpenCV consegue entender e, em seguida, aplica os filtros selecionados.

*   **`player.py`** `[STATUS: Em Edição]`
    *   **O que faz?** Atualmente, este arquivo está vazio, mas sua intenção é abrigar a classe `Player`, que controlará o personagem do jogador (movimentação, estado, sprites, etc.).

*   **`menu/config.py`** `[STATUS: Implementado]`
    *   **O que faz?** Contém configurações iniciais da janela e do Pygame.
    *   **Responsabilidades:**
        *   Define a largura e altura da tela.
        *   Centraliza a janela na tela do computador.
        *   Inicializa módulos do Pygame, como o de fontes.

---

#### Arquivos de Processamento de Imagem (OpenCV)

Estes são os arquivos mais relevantes para a disciplina de PDI.

*   **`processamento_imagem.py`** `[STATUS: Implementado]`
    *   **O que faz?** É uma biblioteca de funções de PDI. Cada função recebe uma imagem (matriz NumPy) e retorna uma nova imagem com um filtro aplicado.
    *   **Filtros implementados:**
        *   `aplicar_escala_cinza`: Converte a imagem para tons de cinza.
        *   `aplicar_sobel`: Detecta bordas na imagem.
        *   `aplicar_blur`: Desfoca a imagem.
        *   `injetar_ruido_salt_pepper`: Adiciona ruído "sal e pimenta".
        *   `aplicar_filtro_mediana`: Remove o ruído "sal e pimenta".
        *   `ajustar_brilho_contraste_saturação`: Altera propriedades de cor e intensidade.

*   **`filtro_local.py`** `[STATUS: Implementado]`
    *   **O que faz?** Implementa o efeito de "lupa de PDI".
    *   **Como funciona:**
        *   Cria uma área circular ao redor do mouse.
        *   Aplica os filtros de `processamento_imagem.py` apenas dentro dessa área (ou fora dela, se o modo estiver invertido).
        *   Isso permite que o jogador inspecione partes específicas da cena com um filtro, sem afetar a tela inteira.

*   **`histograma.py`** `[STATUS: Implementado]`
    *   **O que faz?** Cria e gerencia um histograma de cores interativo que é exibido na tela.
    *   **Funcionalidades:**
        *   Analisa a imagem da cena e plota a distribuição de tons de azul, verde e vermelho.
        *   Permite que o jogador clique em uma faixa de tom no gráfico para selecioná-la, o que pode ser usado como gatilho para alguma mecânica de jogo.

---

#### Arquivos de Teste e Utilitários

*   **`greyboxing[1-10].py`** `[STATUS: Em Edição / Para Revisão]`
    *   **O que são?** São scripts de teste isolados, usados para prototipar e validar as funcionalidades de PDI sem a complexidade do jogo completo.
    *   **Exemplo (`greyboxing1.py`):** Cria uma cena simples com formas geométricas e permite ligar/desligar um filtro de tons de cinza para ver o resultado em tempo real. É uma ótima forma de testar um novo filtro antes de integrá-lo ao `main.py`.
    *   **Destaques:**
        *   **`greyboxing5.py`**: Explora a integração 2D/3D para uma mecânica de coleta de itens. Simula a coleta de um objeto 3D (pirâmide) em uma face de um cubo 3D usando OpenGL, detectando cliques do mouse na projeção 2D do item. Essencial para entender a interação entre elementos 2D (interface) e 3D (mundo do jogo) e como um item 3D pode ser manipulado ou ativado através de uma interface 2D no jogo final.
        *   **`greyboxing6.py`**: Foca na configuração da interface do usuário (HUD), ícones da janela e um sistema básico de câmera sidescrolling. Implementa a splash screen inicial, define ícones para a barra de tarefas e a janela, e gerencia um painel de HUD fixo na tela com um botão interativo. Este greyboxing é fundamental para a estrutura visual e de navegação do jogo.
        *   **`greyboxing8.py`**: Representa a "Central de Filtros Avançada" do jogo. Integra sliders para ajuste de cores globais (RGB), brilho, contraste e saturação, além de um histograma interativo e a funcionalidade de "lupa de PDI" (definida em `filtro_local.py`). Este script é crucial para a mecânica central do jogo, permitindo ao jogador manipular a cena com diversos filtros em tempo real e registrar experimentos usando `logger_pdi.py`.

*   **`logger_pdi.py`** `[STATUS: Implementado]`
    *   **O que faz?** É uma ferramenta de análise e depuração.
    *   **Como funciona:**
        *   Salva um arquivo chamado `historico_pdi.json`.
        *   Cada vez que um filtro é aplicado ou um evento relevante ocorre, ele registra dados importantes nesse arquivo, como:
            *   A data e hora.
            *   Os valores dos sliders e do histograma.
            *   Estatísticas matemáticas da imagem *antes* e *depois* da transformação (como a média de cores).
        *   **Utilidade:** Permite analisar o impacto numérico de cada filtro, o que é perfeito para relatórios e para entender profundamente o que o código está fazendo.

---

#### Diretórios de Recursos

*   **`assets/`** `[STATUS: Em Edição]`
    *   Contém todos os recursos visuais e sonoros do jogo, como sprites de personagens, cenários, músicas de fundo (BGM) e efeitos sonoros (SFX).

*   **`src/Documentos_Guias/`** `[STATUS: Implementado]`
    *   Onde esta e outras documentações do projeto devem ser armazenadas.

---

#### Módulos Essenciais Futuros

Estes módulos ainda não foram criados, mas são planejados para o desenvolvimento futuro do jogo.

*   **`inimigo.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Classe base para diferentes tipos de inimigos, com comportamento, movimentação e interação com o jogador.

*   **`fase.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Gerenciamento da lógica de fases do jogo, incluindo carregamento de cenários, posicionamento de inimigos e itens, e transições de tela.

*   **`gerenciador_assets.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Carregamento e gerenciamento otimizado de todos os recursos (sprites, áudios) para evitar gargalos de performance.

*   **`ui.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Abstração de elementos de interface do usuário (botões, caixas de texto, menus) para facilitar a criação de GUIs complexas.

*   **`save_system.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Implementação de um sistema para salvar e carregar o progresso do jogador, configurações e outros dados persistentes.

*   **`desafios/desafio_contraste.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Lógica específica para um desafio que exige a manipulação de contraste para revelar elementos ocultos.

*   **`desafios/desafio_lupa.py`** `[STATUS: Aguardando Criação]`
    *   **O que fará?** Lógica específica para um desafio que utiliza a funcionalidade de lupa de PDI para resolver um quebra-cabeça.