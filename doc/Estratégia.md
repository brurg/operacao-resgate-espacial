# Estratégia de Distribuição de Vagas

## Objetivo

A estratégia de distribuição tem como objetivo selecionar automaticamente quais naves devem ser acionadas e quantos assentos devem ser solicitados para cada uma, considerando a quantidade de pessoas que precisam ser evacuadas, a capacidade disponível das naves, o tempo estimado de chegada e a urgência das missões.

O algoritmo busca garantir que todas as pessoas tenham assentos confirmados, evitando solicitações desnecessárias e considerando tanto os pedidos que ainda aguardam resposta quanto as confirmações já recebidas.

## Critérios de priorização das missões

As missões são processadas de acordo com seus níveis de urgência, nesta ordem:

1. **HIGH:** prioridade alta.
2. **MEDIUM:** prioridade média.
3. **LOW:** prioridade baixa.

A estratégia considera todas as missões não concluídas em cada execução, permitindo reavaliar a distribuição globalmente sempre que houver uma nova oferta de nave ou uma alteração no estado de um pedido. 

## Critérios de seleção das naves

A seleção das naves considera o nível de urgência da missão.
Dentro de cada nível de urgência, as missões mais antigas são processadas primeiro.

### Missões HIGH

Para missões de alta urgência, as naves são ordenadas pelo menor tempo estimado de chegada.

Em caso de empate, a nave com maior capacidade efetiva é priorizada.

O objetivo é priorizar a chegada mais rápida possível do transporte.

### Missões MEDIUM

Para missões de urgência média, é utilizada uma pontuação que considera igualmente o tempo estimado de chegada e a capacidade oferecida pela nave.

São calculados dois indicadores:

**Pontuação de tempo:**

T = 1 / (1 + ETA / 180)

Em que ETA representa o tempo estimado de chegada em minutos. O valor de 180 minutos é utilizado como referência para normalização da pontuação.

**Pontuação de capacidade:**

C = capacidade efetiva da nave / maior capacidade efetiva entre as ofertas avaliadas

A pontuação final é:

Score = 0,5 × T + 0,5 × C

As naves são ordenadas pela maior pontuação. Em caso de empate, são priorizadas aquelas com menor tempo de chegada e, depois, maior capacidade.

Essa combinação busca equilibrar rapidez e aproveitamento da capacidade disponível.

### Missões LOW

Para missões de baixa urgência, as naves são ordenadas pela maior capacidade efetiva.

Em caso de empate, é priorizada a nave com menor tempo estimado de chegada.

O objetivo é concentrar os pedidos em naves com maior capacidade, reduzindo a quantidade de mobilizações necessárias.

## Cálculo da quantidade de assentos solicitados

Antes de criar um pedido, o sistema calcula a quantidade de assentos que ainda precisa ser obtida.

São consideradas três informações:

- Quantidade total de pessoas da missão.
- Quantidade de assentos já confirmados.
- Quantidade de assentos comprometidos por pedidos pendentes.

A quantidade ainda não comprometida é calculada por:

Assentos restantes = Total de pessoas - Assentos confirmados - Assentos pendentes

Para cada nave selecionada, a quantidade solicitada corresponde ao menor valor entre:

- Assentos ainda necessários para a missão.
- Assentos oferecidos pela nave.
- Capacidade atualmente disponível na nave.

Dessa forma, o sistema não solicita mais assentos do que a missão precisa nem ultrapassa a capacidade disponível da nave.

Pedidos pendentes são considerados compromissos temporários, pois ainda podem ser aceitos pelos comandantes. Portanto, o sistema não solicita novamente os mesmos assentos enquanto aguarda uma resposta.

## Controle de capacidade das naves

A capacidade comprometida de uma nave é calculada considerando os pedidos associados a ela:

- **PENDING:** compromete toda a quantidade solicitada.
- **CONFIRMED:** compromete a quantidade confirmada.
- **PARTIAL:** compromete somente a quantidade confirmada.
- **UNAVAILABLE:** não compromete capacidade.
- **CANCELLED:** não compromete capacidade.
- **EXPIRED:** não compromete capacidade.

A capacidade disponível corresponde à capacidade total da nave menos a quantidade de assentos comprometidos.

Uma nave pode participar de diferentes missões. O sistema considera os compromissos registrados para a mesma nave ao verificar sua capacidade disponível.

## Reavaliação e realocação de pedidos

A estratégia é executada automaticamente após eventos que podem alterar a distribuição das vagas:

- Cadastro de uma missão.
- Disponibilização de assentos por uma nave.
- Resposta a um pedido.
- Cancelamento de um pedido.
- Expiração de um pedido.

Em cada execução, todas as missões não concluídas são reavaliadas de acordo com a ordem de urgência.

Quando uma missão de maior prioridade precisa de capacidade que está comprometida por pedidos pendentes de missões de menor prioridade, o sistema pode cancelar esses pedidos automaticamente para liberar os assentos.

A realocação segue estas regras:

1. Somente pedidos com status PENDING podem ser cancelados automaticamente.
2. Pedidos de missões de menor prioridade são considerados primeiro para liberação de capacidade.
3. O pedido cancelado permanece registrado no histórico, com status CANCELLED.
4. A oferta da nave é disponibilizada novamente para permitir uma nova solicitação.
5. A missão de maior prioridade recebe primeiro a capacidade liberada.
6. Depois, a estratégia tenta atender novamente as missões de menor prioridade com a capacidade restante.

Pedidos confirmados, parciais, recusados, cancelados ou expirados não são alterados.

Essa decisão permite adaptar a distribuição quando surgem missões mais urgentes, preservando as respostas já recebidas dos comandantes.

## Tratamento das respostas

Quando um comandante responde a um pedido, o sistema encerra aquele pedido e atualiza a capacidade comprometida da nave.

- **Confirmação total:** todos os assentos solicitados são confirmados.
- **Confirmação parcial:** somente a quantidade informada é confirmada. O restante deixa de estar comprometido e deverá ser obtido por outros pedidos.
- **Recusa:** nenhum assento é confirmado e toda a capacidade comprometida é liberada.
- **Cancelamento:** um pedido ainda pendente é encerrado e sua capacidade é liberada.
- **Expiração:** um pedido pendente cujo prazo terminou é encerrado e sua capacidade é liberada.

Após uma resposta que não conclua a missão, a estratégia é executada novamente para buscar os assentos que ainda faltam.

## Conclusão da missão

Uma missão somente é considerada concluída quando a quantidade de assentos confirmados é igual à quantidade de pessoas que precisam ser evacuadas.

Pedidos pendentes não são considerados vagas garantidas.

Assim, mesmo que existam solicitações aguardando resposta, a missão permanece em andamento até que todas as vagas necessárias estejam efetivamente confirmadas.

## Premissas adotadas

Para definir o comportamento da estratégia, foram adotadas as seguintes premissas:

- A prioridade HIGH, MEDIUM e LOW determina a ordem de atendimento entre missões.
- Dentro de cada nível de urgência, missões mais antigas são processadas primeiro.
- Os critérios de seleção das naves variam conforme a urgência da missão.
- O tempo estimado de chegada é fornecido como informação da oferta da nave.
- O valor de 180 minutos é uma referência matemática para o cálculo da pontuação das missões MEDIUM, não um limite máximo de chegada.
- Pedidos pendentes podem ser cancelados automaticamente para realocar capacidade a missões mais urgentes.
- Respostas já recebidas e decisões encerradas são preservadas.
- A estratégia considera a capacidade comprometida por pedidos de uma mesma nave, inclusive quando associada a diferentes missões.
- A persistência dos dados é realizada em memória.
- A disponibilidade informada por uma nave no cadastro da oferta é considerada válida durante o processamento dos pedidos. Caso o comandante não consiga atender à quantidade solicitada, essa situação é representada por uma confirmação parcial ou recusa.
- Alterações operacionais espontâneas na capacidade de uma nave após a confirmação dos assentos não são simuladas pelo sistema. As vagas já confirmadas são consideradas compromissos garantidos.
liberados e deixam de ser considerados na capacidade reservada da nave. Em seguida, a estratégia de distribuição pode ser executada novamente para buscar outras alternativas e atender à necessidade restante da missão.
- Cada pedido tem um prazo de 3 horas, representando o intervalo máximo de espera antes do pedido expirar.

## Consistência e concorrência

As operações que modificam o estado compartilhado do sistema são protegidas por um mecanismo de exclusão mútua (`RLock`).

Esse mecanismo evita que operações simultâneas de criação, cancelamento, resposta ou realocação alterem os mesmos dados de forma inconsistente dentro de um único processo da aplicação.

Além disso, cada pedido possui um estado que determina quais operações ainda são permitidas. Somente pedidos pendentes podem receber respostas, ser cancelados ou expirar. Após o encerramento, novas respostas são rejeitadas.