# Vision Quest: The Filter Chronicles

Um jogo de plataforma 2D interativo e linear desenvolvido como projeto prático para a disciplina de **Introdução à Computação Visual (CMC005) - UNIFEI**. O objetivo do jogo é guiar o personagem através de um corredor de desafios onde a progressão e a revelação de itens dependem diretamente da aplicação de técnicas de Processamento Digital de Imagens e Computação Gráfica.

---

## 🎮 Mecânicas do Jogo e Diretrizes Atendidas

O projeto foi projetado para cobrir os requisitos obrigatórios solicitados no escopo:

* **Objetos Gráficos e Interface:** O jogo conta com elementos 2D (personagem, plataformas, HUD) e uma cena de inspeção com objetos 3D renderizados em tempo real.
* **Transformações Geométricas:** Uso de translação, rotação e escalonamento para inspecionar ou manipular elementos do cenário.
* **Desafio 1 (Brilho e Contraste):** O jogador altera as propriedades de brilho e contraste da tela através de controles para revelar itens ocultos no cenário.
* **Desafio 2 (Filtro de Linhas - Sobel Manual):** Ativação de um modo de visão que aplica a detecção de bordas de Sobel **implementada manualmente (sem funções prontas da biblioteca)** para destacar os contornos de plataformas ou chaves invisíveis.
* **Desafio 3 (Manipulação de Cores e Histograma):** O jogador interage com o histograma de cores da cena capturada para neutralizar barreiras ou lasers coloridos.
* **Desafio 4 (Filtro Espacial Local):** Uma "Lupa Mágica" controlada pelo cursor do mouse que aplica um filtro de suavização/mediana localmente, afetando apenas uma parte específica da cena para revelar o caminho seguro.

---

## 🛠️ Pré-requisitos e Instalação

Antes de executar o projeto no VS Code, certifique-se de ter o Python instalado e as bibliotecas necessárias.

### 1. Clonar o Repositório
```bash
#git clone [https://github.com/Cheeshiiree/Vision-Quest.git](https://github.com/Cheeshiiree/Vision-Quest.git)
#cd Vision-Quest
#git clone [https://github.com/Cheeshiiree/Teste_Jogo_CompVisual.git](https://github.com/Cheeshiiree/Teste_Jogo_CompVisual.git)
#cd Teste_Jogo_CompVisual
```

###2. Criar um Ambiente Virtual (opcional, mas recomendado)
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

###3. Instalar as Dependências
Instale os pacotes sugeridos pelas diretrizes através do terminal:  Bash
```bash
pip install pygame PyOpenGL opencv-python numpy scikit-image
```
### 4. Estrutura de Arquivos Sugerida
Para manter o desenvolvimento organizado no VS Code, utilize a seguinte árvore de diretórios:
```plaintext
<!-- Vision-Quest/ -->
Teste_Jogo_CompVisual/
│
├── src/
│   ├── __init__.py
│   ├── main.py             # Loop principal do Pygame e gerenciamento de estados
│   ├── player.py           # Física de movimento, pulo e colisões do personagem
│   ├── level.py            # Definição do mapa, plataformas e gatilhos dos desafios
│   ├── filters.py          # Implementação dos filtros (OpenCV e o Sobel Manual)
│   └── renderer_3d.py      # Lógica de renderização e transformações do PyOpenGL
│
├── assets/                 # Sprites, fontes e efeitos sonoros
│
├── README.md               # Documentação do projeto
└── requirements.txt        # Lista de dependências do Python
```

### 🚀 Como Executar o Projeto de Teste
* ** Abra a pasta raiz do projeto no VS Code.Certifique-se de que o interpretador Python esteja selecionado corretamente.
* **Abra o arquivo src/main.py.
* **Execute o arquivo diretamente pelo VS Code ou através do terminal integrado:
```Bash
python src/main.py
```

### ⏱️ Datas Importantes e Entrega
**Entrega da aplicação:** Até o dia 15/06, às 23h59, via SIGAA.  
**Apresentações:** Dias 16/06 e 18/06 (Duração máxima de 15 minutos por grupo, com a participação de todos os integrantes).  
**Contato da Disciplina:** isadrummond@unifei.edu.br.  

---
## 📜 Instalações necessárias para rodar o projeto
* **Python 3.x**: Instale usando o site oficial [python.org](https://www.python.org/downloads/).
* **Pygame**: Para a criação do jogo e gerenciamento de eventos.
```bash
pip install pygame
```
* **PyOpenGL**: Para renderização 3D em tempo real.
```bash
pip install PyOpenGL
```
* **OpenCV**: Para processamento de imagens e aplicação de filtros.
```bash
pip install opencv-python
```
* **NumPy**: Para manipulação de arrays e operações matemáticas.
```bash
pip install numpy
```
* **Scikit-Image**: Para filtros adicionais e manipulação de imagens.
```bash
pip install scikit-image
```
* **Pygame Pgzero**: Para teste de algumas funções.
```bash
pip install pgzero
```