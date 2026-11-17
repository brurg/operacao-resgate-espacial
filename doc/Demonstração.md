# Roteiro de Demonstração

## Objetivo

A demonstração teve como objetivo apresentar o funcionamento do sistema de gerenciamento de missões de evacuação espacial, destacando a distribuição automática de assentos, a seleção das naves, o tratamento das respostas dos comandantes e a realocação de vagas quando uma solicitação não é atendida integralmente.

O vídeo apresenta a execução do cenário descrito neste documento, incluindo as operações realizadas na interface e as atualizações produzidas pelo sistema ao longo da mobilização.

## Cenário utilizado

Foi utilizado um cenário em que uma missão precisava evacuar 20 pessoas, com nível de urgência **HIGH**.

Foram utilizadas três naves:

- **Nave Alpha:** disponibilizou inicialmente 12 assentos.
- **Nave Beta:** disponibilizou inicialmente 8 assentos.
- **Nave Gamma:** disponibilizou posteriormente 14 assentos para atender à necessidade restante. Sua capacidade total cadastrada era de 15 assentos.

O cenário permitiu demonstrar diferentes respostas dos comandantes e como o sistema reage à quantidade de assentos efetivamente confirmada.

## Sequência da demonstração

### Etapa 1 – Cadastro da missão e das naves

Foi cadastrada a missão com os seguintes dados:

- Nome: Aurora01
- Quantidade de pessoas: 20
- Urgência: HIGH

Também foi cadastrada a Nave Gamma, com capacidade total de 15 assentos, para ser utilizada posteriormente na realocação das vagas restantes.

### Etapa 2 – Cadastro das ofertas das naves

Foram cadastradas as ofertas iniciais:

- Nave Alpha: 12 assentos.
- Nave Beta: 8 assentos.

Após o cadastro das ofertas, o sistema executou automaticamente a estratégia de distribuição e gerou os pedidos de mobilização.

Foi possível observar que a quantidade solicitada considera a necessidade ainda não atendida pela missão, a oferta informada e a capacidade efetivamente disponível das naves.

### Etapa 3 – Confirmação parcial

Foi simulada a resposta do comandante da Nave Alpha, que confirmou apenas 7 dos 12 assentos solicitados.

O sistema registrou a resposta parcial e atualizou o comprometimento da capacidade da nave. Os 7 assentos confirmados passaram a ser considerados garantidos, enquanto os 5 assentos não confirmados deixaram de estar comprometidos.

### Etapa 4 – Recusa de solicitação

Em seguida, foi simulada a recusa do pedido pelo comandante da Nave Beta.

O sistema registrou a recusa e liberou a capacidade que estava comprometida com aquela solicitação. Como consequência, nenhum assento da Nave Beta foi considerado confirmado para a missão.

### Etapa 5 – Realocação das vagas restantes

Após as respostas anteriores, foi cadastrada a oferta da Nave Gamma, disponibilizando 14 assentos.

O sistema executou novamente a estratégia de distribuição e identificou que ainda eram necessários 13 assentos para completar a evacuação: 20 pessoas solicitadas menos os 7 assentos já confirmados.

Foi então gerado automaticamente um novo pedido para a Nave Gamma de 13 assentos.

### Etapa 6 – Confirmação final

Foi simulada a confirmação integral dos 13 assentos solicitados à Nave Gamma.

O sistema atualizou o pedido e contabilizou os novos assentos confirmados. Com isso, a quantidade total de assentos confirmados atingiu as 20 vagas necessárias.

### Etapa 7 – Verificação da conclusão

Ao final, foi apresentado o resumo atualizado da missão e seu histórico de eventos.

A missão foi marcada como concluída, pois todos os 20 assentos necessários haviam sido confirmados.

## Resultado obtido

Ao final da execução, foi obtido o seguinte resultado:

| Nave | Assentos solicitados | Assentos confirmados | Resultado |
|---|---:|---:|---|
| Nave Alpha | 12 | 7 | Parcial |
| Nave Beta | 8 | 0 | Recusado |
| Nave Gamma | 13 | 13 | Confirmado |
| **Total confirmado** | | **20** | **Missão concluída** |

Os pedidos foram realizados em momentos diferentes. Portanto, a soma dos assentos solicitados ao longo da demonstração não representa a quantidade de assentos comprometidos simultaneamente.

## Funcionalidades demonstradas

Durante a execução, foram demonstradas as seguintes funcionalidades:

- Cadastro e gerenciamento de missões.
- Cadastro de naves e ofertas de assentos.
- Seleção automática das naves e cálculo da quantidade solicitada.
- Priorização das missões conforme seu nível de urgência.
- Registro de confirmações totais, parciais e recusas.
- Atualização da capacidade comprometida das naves.
- Reexecução automática da estratégia após respostas aos pedidos.
- Realocação das vagas que permaneceram sem confirmação.
- Conclusão da missão somente após a confirmação de todos os assentos necessários.
- Registro e consulta dos eventos realizados durante o processo.

## Vídeo da demonstração

O vídeo a seguir apresenta a execução prática do cenário descrito neste documento, incluindo o cadastro da missão, as respostas dos comandantes, a redistribuição dos assentos e a conclusão da evacuação.

**Vídeo:** [demonstração](/doc/demonstracao/demonstracao.mp4)
