# Demonstração Complementar – Estratégia de Distribuição

## 1. Cadastrar as missões

Na área do Operador, acesse **Cadastrar missão** e cadastre:

| Missão | Estação | Passageiros | Urgência |
|---|---|---:|---|
| Aurora | Estação Aurora | 12 | LOW |
| Boreal | Estação Boreal | 10 | MEDIUM |
| Centauri | Estação Centauri | 15 | HIGH |

## 2. Cadastrar as naves

Na área do Operador, acesse **Cadastrar nave**:

| Nave | Capacidade |
|---|---:|
| Alpha | 10 |
| Beta | 8 |
| Gamma | 12 |
| Delta | 15 |

## 3. Cadastrar as disponibilidades

Na área do Comandante, acesse **Disponibilizar assentos** e cadastre as ofertas conforme a tabela.

| Missão | Nave | Assentos oferecidos | ETA |
|---|---|---:|---:|
| Centauri | Beta | 8 | 30 min |
| Centauri | Alpha | 7 | 60 min |
| Boreal | Gamma | 7 | 120 min |
| Boreal | Alpha | 3 | 60 min |
| Aurora | Delta | 10 | 90 min |
| Aurora | Gamma | 5 | 120 min |

Preencha a previsão de chegada de forma que os ETAs correspondam aos valores indicados.

**Conferência da capacidade:**

| Nave | Total oferecido | Capacidade |
|---|---:|---:|
| Alpha | 10 | 10 |
| Beta | 8 | 8 |
| Gamma | 12 | 12 |
| Delta | 10 | 15 |

## 4. Executar a estratégia e conferir a distribuição

Execute a estratégia e observe a ordem de atendimento das missões e a seleção das naves.

| Missão | Ordem esperada das naves | Distribuição esperada |
|---|---|---|
| Centauri (HIGH) | Beta → Alpha | 8 + 7 = 15 |
| Boreal (MEDIUM) | Gamma → Alpha | 7 + 3 = 10 |
| Aurora (LOW) | Delta → Gamma | 10 + 2 = 12 |

Verifique:
- Centauri é atendida primeiro por possuir urgência HIGH.
- Boreal é atendida antes de Aurora.
- HIGH prioriza o menor ETA.
- MEDIUM considera ETA e capacidade disponível.
- LOW prioriza a maior capacidade disponível.

## 5. Verificar os pedidos pendentes

Antes de responder aos pedidos, acesse **Solicitações**.

**Resultado esperado:**
- Os pedidos aparecem com status PENDING.
- Os assentos solicitados ficam temporariamente comprometidos.
- A capacidade comprometida não deve ser utilizada novamente pela estratégia.

## 6. Realizar uma confirmação parcial

Na área do Comandante, selecione um pedido de 8 assentos e confirme apenas 5.

**Resultado esperado:**
- O pedido passa para PARTIAL.
- Somente 5 assentos permanecem comprometidos.
- Os 3 assentos não confirmados são liberados.
- A estratégia pode considerar novamente a capacidade liberada.

## 7. Recusar um pedido

Selecione outro pedido pendente e clique em **Recusar**.

**Resultado esperado:**
- O pedido passa para UNAVAILABLE.
- A capacidade anteriormente comprometida é liberada.
- A estratégia pode utilizar essa capacidade em novas solicitações.

## 8. Cancelar um pedido

Na área do Operador, acesse **Solicitações** e cancele um pedido ainda PENDING.

**Resultado esperado:**
- O pedido passa para CANCELLED.
- Seus assentos deixam de ser considerados comprometidos.
- A capacidade pode ser utilizada em uma nova distribuição.

## 9. Verificar a preempção

Criação de uma missão Urgente em que precise de capacidade comprometida por um pedido PENDING de uma missão menos urgente.

**Resultado esperado:**
- O pedido pendente de menor prioridade foi cancelado para liberar capacidade.
- A missão de maior urgência passa a ter prioridade na distribuição.
- Como acabaria a capacidade da nave ele foi totalmente cancelado por não ter mais disponibilidade.
- Assentos já confirmados não são retirados.

## Vídeo da demonstração

O vídeo a seguir apresenta a execução prática do cenário descrito neste documento, 

**Vídeo:** [demonstração_complementar](/doc/demonstracao/demonstracao_complementar.mp4)
