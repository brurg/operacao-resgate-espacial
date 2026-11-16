# Documentação dos testes automatizados

Os testes foram implementados com **pytest** e verificam regras de negócio, validações, integração da API, integridade dos dados e comportamento sob concorrência.

## Organização dos arquivos

Os testes ficam no diretório `tests/`:

```text
tests/
├── conftest.py
├── test_mission.py
├── test_mission_ship.py
├── test_ship.py
├── test_rescue_request.py
├── test_strategy.py
└── test_concurrency.py
```

A organização separa os testes por responsabilidade do sistema. Assim, cada arquivo concentra os cenários relacionados a uma parte da aplicação.

## Casos de teste por arquivo

### `test_mission.py` — Missões

Verifica a criação, consulta, validação e conclusão das missões.

| Caso de teste | O que verifica |
|---|---|
| `test_create_valid_mission` | Criação de uma missão válida e preenchimento dos dados esperados. |
| `test_default_urgency_is_medium` | Aplicação de urgência média quando nenhuma urgência é informada. |
| `test_invalid_people_rejected_without_mutation` | Rejeição de quantidades de pessoas inválidas (zero, negativas, fracionárias, texto ou valor nulo) e preservação do estado do sistema. |
| `test_invalid_urgency_rejected` | Rejeição de uma urgência fora dos valores aceitos, sem alterar os dados. |
| `test_list_and_get_missions` | Consulta da lista de missões e de uma missão específica. |
| `test_mission_only_completes_after_all_confirmations` | Confirma que a missão só é concluída quando todos os assentos necessários foram confirmados. |
| `test_insufficient_seats_do_not_complete_mission` | Verifica que confirmação parcial, recusa, cancelamento ou expiração não concluem uma missão com assentos ainda pendentes de atendimento. |
| `test_mission_events_are_filtered_and_chronological` | Verifica a filtragem dos eventos por missão e sua ordenação cronológica. |

### `test_ship.py` — Naves

Verifica o cadastro e a consulta de naves.

| Caso de teste | O que verifica |
|---|---|
| `test_register_valid_ship` | Cadastro de uma nave com dados válidos. |
| `test_invalid_capacity_rejected` | Rejeição de capacidades nulas, negativas, fracionárias ou com tipo inválido, sem modificar o estado. |
| `test_list_get_and_missing_ship` | Listagem, consulta individual e tratamento de nave inexistente. |

### `test_mission_ship.py` — Ofertas de assentos

Verifica a associação entre naves e missões por meio das ofertas de assentos.

| Caso de teste | O que verifica |
|---|---|
| `test_offer_triggers_distribution_and_can_be_queried` | Criação de uma oferta, acionamento da distribuição automática e consulta da oferta. |
| `test_invalid_offer_schema` | Rejeição, na camada da API, de quantidades inválidas de assentos. |
| `test_offer_service_rejects_invalid_quantity` | Rejeição de quantidades inválidas diretamente na camada de serviço. |
| `test_offer_requires_existing_entities` | Impede ofertas associadas a missão ou nave inexistente. |
| `test_offer_cannot_exceed_total_capacity` | Impede que a oferta ultrapasse a capacidade total da nave. |
| `test_duplicate_ship_offer_in_same_mission_rejected` | Impede ofertas duplicadas da mesma nave para a mesma missão. |
| `test_completed_mission_rejects_offer` | Impede novas ofertas para uma missão já concluída. |
| `test_same_ship_serves_different_missions_with_shared_capacity` | Verifica a participação de uma mesma nave em missões diferentes respeitando a capacidade disponível compartilhada. |

### `test_rescue_request.py` — Solicitações de resgate

Verifica o ciclo de vida das solicitações: criação, consulta, resposta, cancelamento, expiração e contabilização de assentos.

| Caso de teste | O que verifica |
|---|---|
| `test_create_request_and_queries` | Criação e consulta de solicitações, incluindo a informação de urgência da missão associada na resposta da API. |
| `test_invalid_request_schema` | Rejeição de quantidades inválidas na entrada da API. |
| `test_invalid_request_service_quantity` | Rejeição de quantidades inválidas diretamente no serviço. |
| `test_request_business_errors` | Tratamento de erros de negócio durante a criação de solicitações, como entidades ou condições incompatíveis. |
| `test_requested_offer_cannot_receive_duplicate_request` | Impede a criação de uma solicitação duplicada para uma oferta que já possui solicitação correspondente. |
| `test_completed_mission_rejects_request` | Impede solicitações para missões concluídas. |
| `test_cannot_request_above_remaining_ship_capacity` | Impede solicitar mais assentos do que a capacidade restante da nave, considerando compromissos pendentes e confirmados. |
| `test_response_totals_and_capacity` | Verifica os totais e a capacidade após respostas completas, parciais ou recusas. |
| `test_invalid_response_schema` | Rejeição de respostas com formato ou quantidade inválida na API. |
| `test_invalid_response_service_quantity` | Rejeição de quantidades inválidas diretamente no serviço. |
| `test_response_above_requested_is_http_400` | Impede que a nave confirme mais assentos do que os solicitados. |
| `test_cancel_pending_request` | Verifica o cancelamento de uma solicitação pendente. |
| `test_expiration_boundary` | Verifica o comportamento da expiração antes, exatamente no limite e depois do prazo, considerando datas com e sem fuso horário. |
| `test_expiration_requires_deadline` | Impede a expiração quando não existe prazo definido. |
| `test_final_states_are_immutable` | Garante que solicitações em estados finais não sejam alteradas por novas respostas, cancelamentos ou expirações. |
| `test_missing_request_mutations_are_rejected` | Rejeita tentativas de alterar solicitações inexistentes. |
| `test_summary_separates_guaranteed_pending_and_uncommitted` | Confere a separação entre assentos confirmados, pendentes e ainda não comprometidos. |
| `test_missing_summary_and_capacity_errors` | Verifica o tratamento de missão inexistente e erros relacionados ao resumo ou à capacidade. |

### `test_strategy.py` — Estratégia de distribuição

Verifica os critérios de priorização das missões, classificação das naves e distribuição/reaproveitamento dos assentos.

| Caso de teste | O que verifica |
|---|---|
| `test_ranking_with_uncommitted_capacity` | Verifica a ordem das naves para cada nível de urgência, considerando a capacidade não comprometida. |
| `test_medium_score_uses_exact_half_time_half_capacity` | Confere que a pontuação de urgência média combina igualmente os critérios de tempo estimado e capacidade. |
| `test_ranking_tiebreakers` | Verifica os critérios de desempate no ranqueamento. |
| `test_strategy_selects_best_ship_before_creating_requests` | Confirma que a estratégia considera a classificação das naves antes de criar solicitações. |
| `test_global_priority_high_medium_low_even_with_targeted_call` | Garante que a prioridade global das missões seja respeitada, mesmo quando a estratégia é acionada para uma missão específica. |
| `test_same_urgency_uses_creation_time_not_insertion_order` | Verifica que missões com a mesma urgência são ordenadas pela data de criação, e não pela ordem em que foram inseridas nos dados. |
| `test_local_request_change_rechecks_global_priority` | Verifica se uma resposta parcial, recusa, cancelamento ou expiração provoca uma nova avaliação das prioridades. |
| `test_allocation_is_minimum_of_need_offer_and_available_capacity` | Garante que a quantidade solicitada não ultrapasse a necessidade restante, a oferta da nave ou sua capacidade disponível. |
| `test_confirmed_and_pending_seats_prevent_duplicate_mobilization` | Impede mobilização duplicada ao considerar assentos confirmados e solicitações pendentes. |
| `test_completed_mission_never_mobilizes_spare_offer` | Impede novas mobilizações quando a missão já recebeu todos os assentos necessários. |
| `test_unfulfilled_seats_generate_new_request_automatically` | Verifica a geração de novas solicitações quando uma resposta deixa assentos sem atendimento. |
| `test_released_capacity_can_serve_another_mission` | Verifica o reaproveitamento da capacidade liberada por uma solicitação encerrada. |
| `test_new_high_offer_reallocates_lower_pending_request` | Verifica a realocação de compromissos pendentes de menor prioridade para atender uma nova oferta destinada a uma missão de alta prioridade. |
| `test_reallocation_releases_lowest_priority_and_newest_first` | Confere a ordem de liberação dos compromissos pendentes durante a realocação. |
| `test_reallocation_preserves_equal_priority_and_received_confirmations` | Garante que a realocação preserve missões de mesma prioridade e assentos já confirmados. |
| `test_rescue_scenario_partial_refusal_and_recovery_to_completion` | Simula um fluxo de resgate com resposta parcial, recusa e recuperação até a conclusão. |
| `test_eta_timezone_past_and_no_hard_180_minute_limit` | Verifica o tratamento de ETA com fuso horário, valores no passado e ausência de um limite rígido de 180 minutos. |
| `test_ranking_uses_available_capacity_instead_of_original_offer` | Garante que o ranqueamento considere a capacidade efetivamente disponível, e não apenas a quantidade originalmente oferecida. |

### `test_concurrency.py` — Concorrência

Verifica se operações simultâneas podem causar inconsistências na capacidade das naves, na necessidade das missões ou no estado das solicitações.

| Caso de teste | O que verifica |
|---|---|
| `test_two_missions_cannot_overcommit_one_ship` | Impede que duas missões comprometam simultaneamente mais assentos do que uma nave possui. |
| `test_two_offers_cannot_overcommit_one_mission` | Impede que ofertas concorrentes ultrapassem a quantidade de pessoas que precisam ser resgatadas. |
| `test_simultaneous_duplicate_responses_count_once` | Garante que respostas simultâneas à mesma solicitação não sejam contabilizadas duas vezes. |
| `test_responses_to_different_requests_cannot_exceed_need` | Impede que respostas simultâneas a solicitações diferentes confirmem mais assentos do que a missão necessita. |
| `test_terminal_decision_cannot_be_overwritten_by_racing_response` | Garante que uma decisão final, como confirmação parcial, recusa, cancelamento ou expiração, não seja sobrescrita por uma resposta concorrente. |
| `test_parallel_strategy_calls_do_not_duplicate_requests` | Verifica se chamadas simultâneas da estratégia não criam solicitações duplicadas. |

## Recursos compartilhados em `conftest.py`

O arquivo `conftest.py` centraliza recursos utilizados por diferentes arquivos de teste.

| Fixture | Finalidade |
|---|---|
| `isolated_repositories` | Mantém os testes isolados, limpando os repositórios antes e depois da execução de cada teste. |
| `clock` | Permite controlar o horário utilizado pela aplicação nos testes que dependem de datas e prazos. |
| `now` | Fornece um horário controlado para criação de registros e comparação de datas. |
| `client` | Disponibiliza o `TestClient` para realizar requisições HTTP à API. |
| `make_mission` | Cria missões de teste com parâmetros configuráveis. |
| `make_ship` | Cria naves de teste com capacidade configurável. |
| `make_offer` | Cria ofertas de assentos entre uma missão e uma nave. |
| `pending_request` | Prepara uma solicitação pendente para testes de resposta, cancelamento, expiração e concorrência. |
| `snapshot` | Captura o estado dos repositórios para verificar se uma operação alterou indevidamente os dados. |
| `run_concurrently` | Executa duas operações de forma concorrente, com sincronização para aproximar o início das operações. |

## Escolhas técnicas e justificativas

### Testes unitários e testes da API

Foram utilizados dois níveis complementares:

- **Testes de serviço:** chamam diretamente funções da camada de serviço para verificar regras de negócio de forma isolada.
- **Testes da API:** utilizam `TestClient` para enviar requisições aos endpoints e verificar códigos HTTP, validações e conteúdo das respostas.

### Parametrização

O recurso `@pytest.mark.parametrize` é utilizado quando uma mesma regra precisa ser verificada com diferentes entradas ou condições, aumentando a variedade de cenários testados.

### Fixtures e isolamento

As fixtures do `conftest.py` padronizam a preparação de missões, naves, ofertas e solicitações. A limpeza dos repositórios entre os testes evita dependência da ordem de execução e impede que dados de um cenário interfiram em outro.

### Controle do tempo

A fixture `clock` permite simular horários específicos sem depender do relógio real da máquina. Isso torna reproduzíveis os testes de vencimento de solicitações, comparação de prazos e ordenação temporal.

### Verificação de integridade com snapshots

Em operações inválidas, alguns testes comparam o estado dos repositórios antes e depois da tentativa. Assim, não verificam apenas se a aplicação rejeitou a operação, mas também se ela evitou alterações parciais ou indevidas nos dados.

### Testes de concorrência

Os testes de concorrência utilizam `ThreadPoolExecutor` e `Barrier` para executar operações em paralelo e sincronizar seu início. Alguns cenários são repetidos para aumentar a possibilidade de identificar condições de corrida.

Essa abordagem verifica regras importantes, como não ultrapassar a capacidade das naves, não confirmar mais assentos do que a missão precisa e não contabilizar duas vezes respostas simultâneas.

## Execução dos testes

Com as dependências instaladas, execute na raiz do projeto:

```bash
python -m pytest -v
```