# Operação Resgate Espacial

Sistema de gerenciamento e distribuição de solicitações de resgate espacial, desenvolvido para coordenar missões de evacuação, disponibilidade de naves e confirmação de assentos.

O sistema permite que a central de operações cadastre missões, receba ofertas de naves, distribua solicitações de assentos e acompanhe as respostas dos comandantes até que todas as pessoas tenham vagas confirmadas.

## Funcionalidades

- Cadastro e consulta de missões de resgate.
- Cadastro e consulta de naves.
- Registro da disponibilidade de assentos por nave em cada missão.
- Distribuição automática de solicitações de resgate.
- Priorização das missões de acordo com sua urgência.
- Classificação das naves considerando tempo de chegada e capacidade disponível.
- Confirmação total ou parcial de assentos pelos comandantes.
- Registro de recusas, cancelamentos e expiração de solicitações.
- Reavaliação automática da distribuição quando há alterações nas disponibilidades.
- Acompanhamento de assentos confirmados, pendentes e ainda necessários.
- Histórico de eventos das missões.

## Tecnologias utilizadas

- **Backend:** Python e FastAPI.
- **Frontend:** React e Vite.
- **Comunicação:** API REST.
- **Execução:** Docker e Docker Compose.
- **Armazenamento:** estruturas em memória no backend.

Python: escolhido por sua sintaxe simples e facilidade de desenvolvimento, permitindo implementar as regras de negócio e a lógica de distribuição de vagas de maneira organizada.

FastAPI: utilizado para desenvolver o backend e disponibilizar uma API REST. A ferramenta oferece validação de dados, organização por rotas e geração automática de documentação interativa por meio do Swagger UI.

React: escolhido para construir uma interface dinâmica e componentizada, permitindo separar as funcionalidades de cada perfil do sistema e facilitar a manutenção da aplicação.

Vite: utilizado como ferramenta de desenvolvimento e inicialização do frontend, proporcionando configuração simplificada e atualização rápida durante o desenvolvimento.

Docker e Docker Compose: utilizados para padronizar a execução do projeto e facilitar a inicialização dos serviços, reduzindo diferenças entre ambientes de desenvolvimento.

## Como executar o projeto

### Pré-requisitos

- Docker.
- Docker Compose.

### Inicialização

Inicie os serviços:

```bash
docker compose up --build
```

Após a inicialização, o serviço estará disponível em http://localhost:5173/.

### Encerramento

Para interromper os serviços:

```bash
docker compose down
```
### Execução sem Docker

Caso prefira executar o projeto sem Docker, é necessário ter Python e Node.js instalados na máquina.

**Backend**

Na raiz do projeto, crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

No Windows, a ativação pode ser feita com:

```powershell
venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o servidor FastAPI: 
```bash
uvicorn backend.main:app --reload
```

**Frontend**

Em outro terminal, acesse a pasta do frontend e instale as dependências:

```bash
cd frontend
npm install
npm run dev
```

Após a inicialização, o frontend estará disponível em http://localhost:5173/.

## Documentação da API

A API foi desenvolvida com FastAPI e disponibiliza documentação interativa automaticamente.

Com o backend em execução, é possível ver em:

- **Swagger UI:** `http://localhost:8000/doc`

As rotas estão organizadas por recursos, incluindo:

- Missões.
- Naves.
- Disponibilidade de naves nas missões.
- Solicitações de resgate.
- Eventos das missões.

## Estratégia de distribuição de vagas

A distribuição automática considera a urgência das missões e as características das naves disponíveis.

### Priorização das missões

As missões são processadas na seguinte ordem:

1. **HIGH:** alta urgência.
2. **MEDIUM:** média urgência.
3. **LOW:** baixa urgência.

Missões com a mesma urgência são ordenadas pela data de criação, priorizando as mais antigas.

### Seleção das naves

O critério de seleção varia conforme a urgência:

- **HIGH:** prioriza a nave com menor tempo estimado de chegada (ETA), utilizando a capacidade como critério de desempate.
- **MEDIUM:** considera igualmente o tempo de chegada e a capacidade disponível, por meio de uma pontuação.
- **LOW:** prioriza a nave com maior capacidade disponível, utilizando o ETA como critério de desempate.

### Cálculo das vagas solicitadas

O sistema considera três quantidades:

- Assentos confirmados: vagas efetivamente garantidas.
- Assentos pendentes: vagas solicitadas que ainda aguardam resposta.
- Assentos não comprometidos: vagas que ainda podem ser solicitadas.

Os pedidos pendentes são considerados compromissos temporários, pois ainda podem ser aceitos pelos comandantes. Assim, o sistema evita solicitar novamente os mesmos assentos enquanto aguarda uma resposta.

A quantidade solicitada de cada nave é limitada pela necessidade da missão, pela oferta registrada e pela capacidade disponível da nave.

### Disponibilidade, respostas e reavaliação

Os comandantes podem confirmar todas as vagas solicitadas, confirmar apenas uma parte ou recusar o pedido.

A disponibilidade das naves é controlada pelo sistema conforme os assentos são comprometidos por solicitações e confirmações. Assim, quando uma nave disponibiliza vagas para uma missão, essa quantidade não pode ser alterada manualmente após o cadastro da oferta. Entretanto, sua capacidade disponível diminui à medida que novos pedidos são realizados e assentos são confirmados, respeitando também os compromissos assumidos com outras missões.

Quando uma solicitação é respondida, cancelada ou expirada, a estratégia é reavaliada para verificar se ainda são necessárias vagas adicionais e redistribuir a capacidade que eventualmente foi liberada.

Uma missão só é considerada concluída quando todos os assentos necessários estão efetivamente confirmados. Assentos pendentes não são contabilizados como garantidos.

Os detalhes dos critérios, fórmulas e decisões de implementação estão descritos em [doc/Estratégia.md](doc/Estratégia.md).

## Consistência e concorrência

As operações que alteram os dados são protegidas por mecanismos de sincronização para evitar inconsistências durante acessos simultâneos dentro de uma mesma instância do backend.

Como os dados são mantidos em memória, essa proteção não substitui mecanismos de transação e sincronização distribuída necessários em uma implantação com múltiplas instâncias.

## Documentação complementar

Os documentos detalhados do projeto estão organizados na pasta [`doc/`](doc/).

- [Especificação do projeto](doc/Especificação.md) — requisitos e funcionalidades solicitadas para o sistema.
- [Arquitetura do sistema](doc/Arquitetura.md) — organização dos componentes e comunicação entre frontend e backend.
- [Estratégia de distribuição](doc/Estratégia.md) — critérios de priorização, seleção de naves, cálculo de vagas e reavaliação das solicitações.

## Demonstração e validação

### Testes automatizados

O projeto utiliza **pytest** para validar o funcionamento das regras de negócio e dos endpoints da API. A suíte combina testes de serviço, testes de integração com `TestClient`, testes parametrizados e cenários de concorrência.

Os testes foram organizados por responsabilidade: missões, naves, ofertas de assentos, solicitações de resgate, estratégia de distribuição e concorrência. Foram utilizadas fixtures para reutilizar dados e isolar os cenários, controle do relógio para testar prazos de forma previsível e snapshots para verificar se operações inválidas preservam o estado dos repositórios.

Também foram desenvolvidos testes concorrentes com `ThreadPoolExecutor` e `Barrier`, buscando identificar condições de corrida que poderiam causar excesso de reservas, confirmações duplicadas ou inconsistências na quantidade de assentos.

Para executar na raiz do projeto:

```bash
python -m pytest -v
```

A documentação detalhada dos cenários, organizada por arquivo de teste, está disponível em **[Casos de teste e escolhas técnicas](doc/CasosTeste.md)**.

### Demonstração

Para demonstrar o funcionamento do sistema, foi utilizado um cenário de evacuação com múltiplas naves, incluindo confirmações parciais e recusas de solicitações, seguido da redistribuição automática dos assentos restantes até a conclusão da missão.

O cenário utilizado, juntamente com a sequência de operações e os resultados esperados, está descrito em **[Demonstração de Funcionamento](doc/Demonstração.md)**. 

Além desta foi criada uma demonstração complementar para analisar outros casos da distribuição da estratégia, descrito em **[Demonstração Complementar](doc/DemonstraçãoComplementar.md)**. 

A demonstração prática do sistema está disponível nos vídeos na pasta **[Vídeos da Demonstração](doc/demonstracao)**.
