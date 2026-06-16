# Laboratório de Computação Visual — PDI com Pygame e OpenCV

Projeto interativo desenvolvido em **Python** para demonstrar conceitos de **Computação Visual** e **Processamento Digital de Imagens (PDI)** em tempo real. A aplicação une uma interface gráfica feita com **Pygame**, processamento com **OpenCV/NumPy**, filtros manuais e um ambiente sandbox onde é possível aplicar efeitos, transformar objetos 2D/3D e analisar histogramas de cor.

## Visão geral

A aplicação abre com uma tela de splash e, em seguida, apresenta um menu principal com acesso ao laboratório, instruções, configurações, informações do projeto e uma página de **Conceitos e Códigos**. O modo claro/escuro afeta apenas as telas de menu e documentação; o **sandbox permanece fixo no modo escuro**, mantendo o visual original do laboratório.

No sandbox, o usuário pode manipular objetos 2D e um artefato 3D, aplicar filtros espaciais, testar filtros manuais, usar uma lupa local, inverter a lupa, alterar canais de cor, brilho, contraste e saturação, além de interagir com um histograma bidimensional.

## Funcionalidades principais

- Menu principal com navegação entre telas.
- Tela de configurações com ajuste de volume, mute, resolução e tema claro/escuro.
- Sandbox visual com cenário, formas 2D e artefato 3D.
- Tema claro/escuro nos menus e telas informativas.
- Sandbox travado em tema escuro para preservar o visual do laboratório.
- Página **Conceitos e Códigos** com rolagem e explicações dos algoritmos utilizados.
- Splash screen inicial e ícone customizado da janela.
- Música de fundo com troca automática de faixa, quando os arquivos `.ogg` estão disponíveis.
- Exportação de logs de experimento ao resetar o laboratório.

## Filtros e recursos de PDI disponíveis

Na HUD inferior do sandbox, a seção **LENS (Filtros & Ruídos)** disponibiliza:

| Recurso | Tipo | Descrição |
|---|---|---|
| Cinza | OpenCV/PDI | Converte a cena para escala de cinza. |
| Sobel OpenCV | OpenCV | Detecta bordas usando implementação de biblioteca. |
| Desfocar | OpenCV | Aplica suavização/blur na imagem. |
| S&P | OpenCV/PDI | Injeta ruído sal e pimenta. |
| Mediana | OpenCV/PDI | Aplica filtro de mediana para reduzir ruídos. |
| Inverter | OpenCV | Inverte os valores dos pixels da cena. |
| Modo Lupa | Manual/local | Aplica efeitos apenas em uma região circular ao redor do mouse. |
| Inv Lupa | Manual/local | Inverte a lógica da lupa, afetando a área externa ou interna conforme o modo. |
| Img Fundo | Interface | Permite selecionar outra imagem de fundo. |
| Reset | Sistema | Restaura filtros, objetos e ajustes do laboratório. |
| Sobel Man | Manual | Executa o Sobel manual implementado no projeto. |
| Pixelar | Manual | Divide a imagem em blocos e substitui cada bloco pela cor média. |
| Ruído RGB | Manual | Soma ruído aleatório independente nos canais B, G e R. |

## Controles do sandbox

### Objetos 2D

- Clique em uma forma 2D para selecioná-la.
- Arraste com o mouse para mover.
- Use as setas do teclado para transladar.
- Use `Q` e `E` para rotacionar.
- Use `R` para aumentar a escala/tamanho.
- Use `T` para reduzir a escala/tamanho.

### Artefato 3D

- Clique no artefato 3D para selecioná-lo.
- Arraste o mouse para rotacionar livremente.
- Use as setas para transladar.
- Use `Q` e `E` para rotação adicional.
- Use `R` e `T` para aumentar ou reduzir a escala.

### Atalhos gerais

| Tecla | Ação |
|---|---|
| `X` | Regenera o laboratório e sorteia um novo modelo 3D. |
| `Z` | Reseta o laboratório e exporta um log do experimento. |
| `ESC` | Volta para o menu principal. |

### Página Conceitos e Códigos

A página de conceitos possui rolagem para acomodar explicações e trechos de código.

| Controle | Ação |
|---|---|
| Roda do mouse | Rola a página. |
| `↑` / `W` | Sobe o conteúdo. |
| `↓` / `S` | Desce o conteúdo. |
| `Page Up` | Sobe uma página. |
| `Page Down` | Desce uma página. |
| `Home` | Vai para o topo. |
| `End` | Vai para o final. |
| `ESC` | Retorna ao menu. |

## Conceitos demonstrados

O projeto foi organizado para apresentar conceitos práticos de computação visual:

- Representação de imagens como matrizes NumPy.
- Conversão entre `RGB` usado pelo Pygame e `BGR` usado pelo OpenCV.
- Aplicação de filtros globais e locais.
- Operações por canal de cor.
- Máscaras circulares para lupa local.
- Filtro Sobel manual por convolução.
- Pixelização manual por blocos e média de cor.
- Ruído RGB aditivo manual.
- Ajuste de brilho, contraste e saturação.
- Histograma por canal e ganho seletivo por faixa de intensidade.
- Transformações geométricas em objetos 2D.
- Projeção e rotação manual de objetos 3D.

## Estrutura sugerida do projeto

```text
Teste_Jogo_CompVisual/
├── assets/
│   ├── bgm/
│   │   └── *.ogg
│   └── sprites/
│       └── misc/
│           ├── Classroom 11.png
│           ├── icon_janela.png
│           └── splash_logo.png
├── src/
│   ├── greyboxing.py
│   ├── ui.py
│   ├── processamento_imagem.py
│   ├── filtro_local.py
│   ├── histograma.py
│   ├── sobel_manual.py
│   ├── filtros_manuais.py
│   ├── inserir_imagens.py
│   └── logger_pdi.py
└── README.md
```

## Papel de cada módulo

| Arquivo | Função |
|---|---|
| `greyboxing.py` | Arquivo principal. Inicializa o Pygame, controla o loop, eventos, sandbox, filtros e renderização. |
| `ui.py` | Controla menus, configurações, tela de sobre, conceitos/códigos, temas e paletas. |
| `processamento_imagem.py` | Agrupa filtros e ajustes de imagem usados no laboratório. |
| `filtro_local.py` | Implementa a lupa local e a lupa invertida. |
| `histograma.py` | Calcula, desenha e permite interação com o histograma. |
| `sobel_manual.py` | Implementa o filtro Sobel manual. |
| `filtros_manuais.py` | Implementa o pixelar manual e o ruído RGB manual. |
| `inserir_imagens.py` | Carrega e converte imagens de fundo entre matriz e superfície. |
| `logger_pdi.py` | Salva logs dos experimentos realizados no sandbox. |

## Requisitos

- Python 3.10 ou superior.
- Pygame.
- NumPy.
- OpenCV para Python.

Instalação das dependências principais:

```bash
pip install pygame numpy opencv-python
```

## Como executar

Execute o projeto a partir da raiz do repositório, para que os caminhos relativos da pasta `assets/` funcionem corretamente:

```bash
python src/greyboxing.py
```

Também é possível validar a sintaxe dos arquivos principais antes de executar:

```bash
python -m py_compile src/greyboxing.py src/ui.py src/filtros_manuais.py
```

## Observações importantes

- A pasta `assets/` precisa estar no caminho esperado, pois o projeto carrega splash screen, ícone, imagem de fundo e músicas por caminhos relativos.
- Caso não existam músicas `.ogg` em `assets/bgm/`, o laboratório continua funcionando, apenas sem trilha sonora.
- Caso a splash screen ou o ícone não sejam encontrados, o programa apenas exibe um aviso e continua a execução.
- O modo claro/escuro foi pensado para os menus e páginas informativas. O sandbox permanece escuro de propósito, para manter contraste com a HUD e os filtros visuais.

## Integrantes

Projeto desenvolvido para a disciplina **COM242 — Computação Visual / Processamento Digital de Imagens**.

- Anna Beatryz Costa
- Emilly Vitória Pereira da Silva
- Julia Barcellos Paiva
- Rafaela Cristina de Moraes Mendes

## Licença

Este repositório é voltado para fins acadêmicos e demonstração de conceitos de PDI. Caso deseje publicar formalmente o projeto, recomenda-se adicionar uma licença como MIT, Apache 2.0 ou outra definida pelo grupo.
