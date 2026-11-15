# Citizen Assist AI

## Integrantes

| Nome completo            |   RM   |
|--------------------------|--------|
| Davi Teodoro Novais      | 571022 |
| Lourenço Borges da Silva | 569515 |
| Matheus Jorge Santana    | 574166 |

**1CCPQ**

## Público e problema

O Citizen Assist AI orienta jovens que estão se preparando para o primeiro emprego e precisam descobrir como obter ou consultar a Carteira de Trabalho Digital, o CPF e o título de eleitor. Pelo terminal, a pessoa pode digitar uma dúvida ou navegar por categoria. Cada orientação informa os documentos necessários, o canal de atendimento, a fonte oficial, a data de verificação e o aviso de que o assistente não é um canal oficial.

### ODS relacionados

- **ODS 8 — Trabalho decente e crescimento econômico.** A orientação sobre a Carteira de Trabalho Digital ajuda jovens a se preparar para o ingresso no trabalho formal. [Nações Unidas Brasil](https://brasil.un.org/pt-br/sdgs/8)
- **ODS 16 — Paz, justiça e instituições eficazes.** A indicação de fontes oficiais facilita o acesso à informação pública e aos serviços de documentação e cidadania. [Nações Unidas Brasil](https://brasil.un.org/pt-br/sdgs/16)

## Como executar

Use Python 3.10 ou superior. O projeto usa apenas a biblioteca padrão.

1. Clone o repositório e entre na pasta do projeto.

   ```sh
   git clone https://github.com/mathsant-js/citizen-assist.git

   cd citizen-assist
   ```

2. Inicie o programa.

   ```sh
   python main.py
   ```

| Opção | O que faz |
| --- | --- |
| `1` | Busca uma orientação pela pergunta. Se a busca não encontrar uma resposta, reformule ou digite `0` para voltar. |
| `2` | Lista categorias e orientações numeradas. Use `0` para voltar nas listas. |
| `3` | Mostra os indicadores do histórico. |
| `4` | Exporta os atendimentos para `data/atendimentos.csv`. |
| `0` | Solicita uma nota de facilidade de 1 a 5 e encerra o programa. |

Após consultar uma orientação, responda `s` ou `n` para informar se ela resolveu a dúvida. Digite as perguntas sem dados pessoais.

## Estrutura do código

| Arquivo | Responsabilidade |
| --- | --- |
| [`main.py`](main.py) | Carrega a base, cria o assistente e coordena o menu. |
| [`orientacao.py`](orientacao.py) | `Orientacao` representa um registro da base. O método `exibir()` apresenta os dados e o aviso de limitação. |
| [`base_conhecimento.py`](base_conhecimento.py) | `BaseConhecimento` lê o JSON em `carregar()`, organiza as categorias em `categorias()` e `por_categoria()` e calcula o ranking em `pontuar()` e `buscar()`. |
| [`assistente.py`](assistente.py) | `Assistente` conduz os fluxos de `perguntar()` e `navegar()`, registra os atendimentos em `registrar()`, calcula `indicadores()` e grava o CSV em `exportar_csv()`. |

`Assistente` contém um objeto `BaseConhecimento`, que contém uma lista de objetos `Orientacao`. Essa composição permite que o atendimento use a base sem precisar ler o JSON a cada pergunta.

### Base de conhecimento e fontes

O arquivo [`data/base_conhecimento.json`](data/base_conhecimento.json) tem 10 orientações em três categorias. Cada orientação é um dicionário com `id`, `categoria`, `titulo`, `palavras_chave`, `resposta`, `documentos`, `onde`, `fonte` e `verificado_em`. A data de conferência fica junto à fonte em cada registro.

| Categoria | Orientações | Fontes oficiais |
| --- | --- | --- |
| Carteira de Trabalho Digital | Primeiro acesso, instalação, consulta de contrato e correção de dados. | [Serviço no gov.br](https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho) · [Perguntas frequentes do Ministério do Trabalho e Emprego](https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho/perguntas-frequentes-carteira-de-trabalho-digital) |
| CPF | Primeira inscrição, consulta da situação cadastral e emissão do comprovante de inscrição. | [Inscrição no CPF](https://www.gov.br/pt-br/servicos/inscrever-no-cpf) · [Consulta da situação cadastral](https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp) · [Impressão do comprovante de inscrição](https://solucoes.receita.fazenda.gov.br/Servicos/CPF/ImpressaoComprovante/ConsultaImpressao.asp) |
| Título de Eleitor | Primeiro título, consulta da situação eleitoral e acesso ao e-Título. | [Carta de serviços do TSE](https://www.tse.jus.br/servicos-eleitorais/servicos/carta-de-servicos-ao-eleitor) · [Consulta da situação eleitoral](https://www.tse.jus.br/institucional/corregedoria-geral-eleitoral/sistemas-e-servicos-1/consulta-situacao-eleitoral) · [Aplicativo e-Título](https://www.tse.jus.br/servicos-eleitorais/servicos/aplicativo-e-titulo) |

### Busca e pontuação

`normalizar()` converte pergunta, títulos e palavras-chave para minúsculas, remove acentos e trata a pontuação como separador. Cada palavra-chave distinta presente na pergunta vale **3 pontos**. Cada palavra distinta da pergunta com pelo menos quatro caracteres que também aparece no título vale **1 ponto**.

`buscar()` retorna uma lista de tuplas `(pontos, orientacao)` em ordem decrescente. Em caso de empate, prevalece a ordem da base. O assistente mostra a primeira colocada e lista os títulos de até duas alternativas com pelo menos 3 pontos.

| Pontuação da melhor orientação | Resultado |
| --- | --- |
| 6 ou mais | Confiança alta |
| 3 a 5 | Confiança média |
| 0 a 2 | Sugestão de reformular ou navegar por categoria |

Em **“Qual é a situação do CPF?”**, a orientação “Consultar a situação do CPF” soma **3** pela palavra-chave `situacao do cpf` e **1** pela palavra `situacao` no título. A pontuação total é **4**, com confiança média.

### Histórico, indicadores e exportação

Cada atendimento em `data/historico.json` guarda `data`, `origem`, `pergunta`, `id_orientacao`, `encontrou`, `ajudou`, `tentativas` e `tempo_segundos`. As notas de facilidade ficam no mesmo arquivo, em `notas_facilidade`. O tempo tem uma casa decimal. O CSV exporta os campos dos atendimentos com `csv.DictWriter`.

| Indicador | Como é calculado |
| --- | --- |
| Respostas encontradas | Percentual de atendimentos em que uma orientação foi exibida. |
| Taxa de acerto | Percentual das orientações exibidas que receberam feedback `s`. |
| Tempo médio para encontrar | Média do tempo decorrido até encontrar ou selecionar uma orientação, sem incluir a resposta ao feedback. |
| Tentativas por atendimento | Média de buscas válidas ou seleções de orientação por atendimento registrado. |
| Facilidade de uso | Média das notas de 1 a 5 dadas na saída pelo menu. |
| Dúvidas sem solução | Perguntas de atendimentos sem solução e orientações acessadas por categoria que receberam feedback `n`. |

## Limitações e privacidade

- A busca depende dos termos cadastrados e cobre os assuntos da base local. Perguntas genéricas, sinônimos ausentes ou intenções parecidas podem exigir reformulação. A confiança indica a pontuação da busca.
- O programa rejeita texto com `@`, oito ou mais dígitos ou formas explícitas de se apresentar, como “meu nome é” e “me chamo”. Esse filtro é heurístico. Durante os testes, use perguntas sem informações pessoais e revise os registros antes de compartilhá-los.
- As orientações refletem as fontes nas datas registradas. Consulte o canal oficial para confirmar os requisitos antes de solicitar um serviço.
