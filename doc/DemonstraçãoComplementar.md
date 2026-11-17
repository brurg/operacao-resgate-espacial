# Demonstração Complementar – Comportamentos da Estratégia

## Objetivo

Esta demonstração complementar tem como objetivo apresentar o comportamento da estratégia de distribuição de assentos em um cenário com múltiplas missões e naves.

Diferentemente da demonstração principal, que concentra a execução em uma única missão, este cenário explora situações em que diferentes níveis de urgência disputam a capacidade disponível da frota.

Ao longo da execução, são demonstrados os critérios de priorização, a seleção das naves, o controle de capacidade comprometida, a reavaliação de pedidos e a redistribuição de assentos diante de respostas dos comandantes.

Também são verificadas situações excepcionais, como cancelamentos, expirações e tentativas de responder novamente a pedidos já encerrados.

## Cenário utilizado

Foram consideradas três missões:

| Missão | Pessoas | Urgência |
|---|---:|---|
| Aurora | 12 | LOW |
| Boreal | 10 | MEDIUM |
| Centauri | 15 | HIGH |

Também foram utilizadas quatro naves:

| Nave | Capacidade | ETA |
|---|---:|---:|
| Alpha | 10 | 60 min |
| Beta | 8 | 30 min |
| Gamma | 12 | 120 min |
| Delta | 15 | 90 min |

As ofertas são cadastradas para as missões conforme a disponibilidade apresentada em cada etapa. A capacidade efetivamente disponível é considerada pela estratégia, levando em conta os assentos já comprometidos por outros pedidos.

## Sequência da demonstração

### Etapa 1 – Cadastro das missões e naves

Foram cadastradas as missões Aurora, Boreal e Centauri, com diferentes quantidades de pessoas e níveis de urgência.

Também foram cadastradas as quatro naves, com capacidades e tempos estimados de chegada distintos.

Essa configuração permite observar como a estratégia diferencia as missões e as naves de acordo com seus critérios de seleção.

### Etapa 2 – Priorização das missões

Com as missões cadastradas, foi executada a estratégia de distribuição.

Foi observado que a missão Centauri, classificada como HIGH, recebe prioridade sobre Boreal e Aurora, independentemente da ordem de criação.

Entre missões com o mesmo nível de urgência, a mais antiga é considerada primeiro.

Essa etapa demonstra que a estratégia não distribui os assentos apenas pela ordem de cadastro das ofertas: ela considera a prioridade global das missões.

### Etapa 3 – Seleção das naves conforme a urgência

Foram disponibilizadas ofertas das diferentes naves e observada a ordenação realizada pela estratégia.

Para a missão HIGH, o menor ETA é priorizado.

Para a missão MEDIUM, são considerados conjuntamente o tempo estimado de chegada e a capacidade disponível, com pesos iguais.

Para a missão LOW, a maior capacidade disponível é priorizada, utilizando o menor ETA como critério de desempate.

Essa etapa permite comparar os diferentes critérios de seleção aplicados conforme a urgência da missão.

### Etapa 4 – Comprometimento de capacidade por pedidos pendentes

Após a geração dos primeiros pedidos, foi executada novamente a estratégia antes de receber todas as respostas dos comandantes.

Foi observado que os assentos associados aos pedidos pendentes são considerados temporariamente comprometidos.

Dessa forma, o sistema não utiliza a mesma capacidade repetidamente para gerar novas solicitações.

Também foi possível observar a diferença entre assentos pendentes e confirmados: os primeiros representam compromissos temporários, enquanto somente os confirmados são considerados garantidos para a missão.

### Etapa 5 – Resposta parcial e redistribuição

Um dos comandantes respondeu parcialmente a um pedido, confirmando uma quantidade inferior à solicitada.

O sistema registrou a resposta, manteve somente os assentos confirmados como comprometidos e liberou a quantidade não atendida.

Em seguida, a estratégia foi executada novamente, considerando a necessidade restante da missão e a capacidade que voltou a ficar disponível.

Foi possível observar a geração de novas solicitações para atender às vagas ainda não confirmadas.

### Etapa 6 – Recusa e liberação de capacidade

Outro comandante recusou um pedido pendente.

O sistema registrou a recusa, liberou a capacidade anteriormente comprometida e reavaliou a distribuição.

A estratégia passou a considerar outras naves disponíveis para atender à necessidade restante.

### Etapa 7 – Cancelamento de pedido pendente

Foi gerado um novo pedido e, antes de receber uma resposta do comandante, foi realizado seu cancelamento.

O sistema atualizou o estado do pedido para CANCELLED e deixou de considerar seus assentos como comprometidos.

Após o cancelamento, a estratégia pôde utilizar a capacidade liberada em uma nova distribuição.

### Etapa 8 – Expiração de pedido pendente

Também foi verificado o comportamento de um pedido que não recebeu resposta dentro do prazo de 3 horas

Após a operação de expiração, o pedido passou para o estado EXPIRED e sua capacidade deixou de ser considerada comprometida.

A estratégia pôde então procurar outras alternativas para atender às vagas restantes.

### Etapa 9 – Repriorização e preempção de pedidos pendentes

Foi considerada uma situação em que uma missão de maior urgência precisava de capacidade que estava comprometida por um pedido pendente de uma missão menos urgente.

A estratégia reavaliou a distribuição e, quando necessário, cancelou pedidos pendentes de menor prioridade para liberar capacidade para a missão prioritária.

Foi verificado que assentos já confirmados não são retirados, e que pedidos de mesma prioridade não são cancelados apenas por esse critério.

Essa etapa demonstra que a estratégia considera a prioridade global das missões mesmo após a geração dos primeiros pedidos.

## Comportamentos demonstrados

| Comportamento | Verificação realizada |
|---|---|
| Priorização por urgência | Missões HIGH antes de MEDIUM e LOW |
| Desempate por criação | Missão mais antiga primeiro |
| Seleção de naves HIGH | Menor ETA |
| Seleção de naves MEDIUM | Equilíbrio entre ETA e capacidade |
| Seleção de naves LOW | Maior capacidade |
| Controle de pedidos pendentes | Capacidade temporariamente comprometida |
| Confirmação parcial | Liberação dos assentos não confirmados |
| Recusa | Liberação da capacidade |
| Cancelamento | Encerramento e liberação do pedido |
| Expiração | Encerramento e liberação do pedido |
| Redistribuição | Geração de novos pedidos |
| Preempção | Liberação de pedidos pendentes de menor prioridade |
