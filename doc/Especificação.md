# Operação Resgate Espacial

## Especificação do Sistema

O sistema tem como objetivo auxiliar a central de resgate espacial no gerenciamento de missões de evacuação, permitindo cadastrar missões, disponibilizar naves, enviar solicitações de reserva e acompanhar as respostas recebidas.

Cada missão representa uma operação de evacuação de uma estação espacial, cuja quantidade de pessoas deve ser informada pelo operador da central no momento do cadastro. O operador também é responsável pelo cadastro inicial das naves, informando seus nomes e capacidades totais.

Das naves cadastradas, os comandantes poderão disponibilizá-las para as missões existentes, informando a quantidade de assentos que podem oferecer, o tempo estimado de chegada e o prazo de validade da disponibilização. Essas informações serão registradas pelo sistema e utilizadas como opções para a estratégia de distribuição.

A estratégia de distribuição, será responsável por analisar as missões e as disponibilizações realizadas pelos comandantes, selecionando as naves e as quantidades de assentos mais adequadas para cada operação. Com base nessa seleção, o sistema enviará solicitações de reserva aos comandantes das naves selecionadas.

O sistema deverá manter o controle das vagas confirmadas, das solicitações ainda pendentes e da quantidade de pessoas que ainda precisam de transporte. Também deverá permitir cancelar ou expirar solicitações sem resposta e registrar os eventos relevantes ocorridos durante a missão.

A solução deverá garantir a consistência das informações mesmo diante de respostas duplicadas, atrasadas ou operações simultâneas, assegurando que somente vagas efetivamente confirmadas sejam consideradas reservadas.

### Escopo

1. Sistema de acompanhamento das missões, pedidos e naves.
2. Estratégia automática de distribuição de vagas.
3. API REST documentada pelo Swagger.
4. Testes automatizados e simulação de operações simultâneas.

### Atores

| Ator | Responsabilidade |
| ---- | ---------------- |
| Operador da central | Cadastrar missões e naves, criar pedidos e acompanhar os resgates |
| Comandante da nave | Consultar pedidos recebidos e informar a quantidade de vagas que poderá disponibilizar | 
| Sistema | Validar operações, atualizar estados, calcular necessidades e registrar eventos |

### Regras de Negócio

| ID | 	Regra de negócio |
| ---- | --------------- |
| RN01 | Toda missão deve possuir um identificador único |
| RN02 | Toda missão deve informar a estação e a quantidade de pessoas a evacuar |
| RN03 | A quantidade de pessoas de uma missão deve ser um número inteiro positivo |
| RN04 | Uma missão não pode ser cadastrada sem pessoas para evacuar |
| RN05 | Uma missão poderá receber disponibilizações de várias naves |
| RN06 | Uma missão será considerada concluída somente quando a quantidade total de vagas confirmadas for igual à quantidade de pessoas a evacuar |
| RN07 | Uma missão com vagas ainda não confirmadas não poderá ser considerada concluída |
| RN08 | Uma missão poderá permanecer em andamento enquanto houver pedidos pendentes ou necessidade de novas solicitações |
| RN09 | O estado da missão deverá ser atualizado conforme as operações realizadas em seus pedidos |
| RN10 | Toda nave deve possuir um identificador único |
| RN11 | Uma nave poderá participar de diferentes missões |
| RN12 | A mesma nave não pode ser disponibilizada mais de uma vez para a mesma missão |
| RN13 | Cada nave deverá possuir capacidade total, quantidade de vagas disponibilizadas, tempo estimado de chegada, o prazo de validade e seu status |
| RN14 | A quantidade de vagas disponibilizadas de uma nave para uma missão não poderá ultrapassar a capacidade total da nave |
| RN15 | A disponibilidade de uma nave deverá considerar as vagas já comprometidas em outras missões |
| RN16 | Uma nave indisponível ou sem vagas disponíveis não poderá receber novos pedidos |
| RN17 | Todo pedido deverá estar associado a uma missão e a uma nave |
| RN18 | A quantidade de vagas solicitada deverá ser um número inteiro positivo |
| RN19 | A quantidade de vagas solicitada para a nave não poderá ultrapassar as vagas disponibilizadas pela nave naquela missão |
| RN20 | A quantidade confirmada deverá ser um número inteiro entre zero e a quantidade solicitada |
| RN21 | Um pedido deverá iniciar com status PENDING |
| RN22 | A confirmação de todas as vagas solicitadas deverá encerrar o pedido como CONFIRMED |
| RN23 | A confirmação de uma quantidade maior que zero e menor que a solicitada deverá encerrar o pedido como PARTIAL |
| RN24 | A confirmação de zero vagas deverá encerrar o pedido como UNAVAILABLE |
| RN25 | Uma resposta parcial encerrará definitivamente o pedido, não permitindo confirmação posterior das vagas restantes |
| RN26 | Somente pedidos pendentes poderão ser cancelados ou expirados |
| RN27 | Pedidos confirmados, parcialmente confirmados, recusados, cancelados ou expirados não poderão ter seus resultados alterados |
| RN28 | Uma resposta recebida após o encerramento de um pedido não poderá modificar suas informações |
| RN29 | A quantidade confirmada de um pedido deverá ser contabilizada apenas uma vez |
| RN30 | A central deverá considerar as vagas confirmadas e as vagas de pedidos pendentes ao determinar a necessidade de novas solicitações |
| RN31 | Vagas pendentes não poderão ser contabilizadas como vagas garantidas |
| RN32 | A quantidade total de vagas confirmadas não poderá ultrapassar a quantidade de pessoas da missão |
| RN33 | A soma de vagas confirmadas e vagas pendentes não poderá ultrapassar a quantidade de pessoas da missão |
| RN34 | Pedidos cancelados, expirados ou recusados não deverão contribuir para o total de vagas pendentes |
| RN35 | Após uma confirmação parcial, recusa, cancelamento ou expiração, a quantidade não atendida deverá voltar a ser considerada na necessidade de mobilização |
| RN36 | O sistema deverá permitir continuar a mobilização enquanto existirem pessoas sem vagas confirmadas |
| RN37 | Operações simultâneas deverão preservar as regras de integridade da missão |
| RN38 | Respostas duplicadas deverão ser identificadas para impedir contabilização repetida |
| RN39 | O histórico de eventos deverá preservar o registro das operações realizadas |

## Requisitos 

### Requisitos Funcionais

| ID | Requisito funcional | Descrição |
| -- | ------------------- | --------- |
| RF01 | Cadastrar missão | Permitir cadastrar uma missão informando estação e quantidade de pessoas a evacuar |
| RF02 | Consultar missões | Permitir listar todas as missões cadastradas |
| RF03 | Consultar missão | Permitir consultar os detalhes de uma missão pelo identificador |
| RF04 | Cadastrar nave | Permitir cadastrar uma nave no sistema, informando nome e capacidade total |
| RF05 | Consultar naves | Permitir listar as naves cadastradas no sistema |
| RF06 | Consultar nave | Permitir consultar os dados de uma nave específica |
| RF07 | Disponibilizar nave para missão | Permitir disponibilizar uma nave a uma missão, informando as vagas. o tempo estimado de chegada e o prazo de validade da oferta |
| RF08 | Consultar naves da missão | Permitir consultar as naves disponibilizadas para determinada missão e suas respectivas informações |
| RF09 | Criar pedido de reserva | Automaticamente definir e solicitar vagas de uma nave disponível à missão |
| RF10 | Consultar pedidos | Permitir listar todos os pedidos relacionados a uma missão |
| RF11 | Consultar pedido | Permitir consultar os detalhes de um pedido específico |
| RF12 | Registrar resposta | Permitir registrar a resposta de uma nave, informando a quantidade de vagas confirmadas |
| RF13 | Atualizar status do pedido	| Atualizar automaticamente o status do pedido conforme a resposta recebida |
| RF14 | Cancelar pedido | Permitir cancelar um pedido que ainda não recebeu resposta |
| RF15 | Expirar pedido | Permitir encerrar um pedido que não recebeu resposta dentro do prazo estabelecido |
| RF16 | Consultar situação da missão | Apresentar o resumo das vagas confirmadas, pendentes e faltantes, além do status da missão |
| RF17 | Consultar histórico de eventos	| Permitir consultar os eventos e operações registrados durante uma missão |
| RF18 | Validar operações | Verificar se as operações solicitadas respeitam as regras de negócio e o estado atual das entidades |
| RF19 | Atualizar disponibilidade da nave | Permitir atualizar a disponibilidade de uma nave para uma missão, respeitando as reservas e os pedidos já existentes |

### Requisitos Não Funcionais

| ID | Requisito | Descrição |
| -- | --------- | --------- |
| RNF01 | Consistência dos dados | O sistema deve preservar a integridade das informações durante operações simultâneas |
| RNF02 | Idempotência | O recebimento repetido de uma mesma resposta não deve provocar contabilização duplicada |
| RNF03 | Integridade das reservas | O sistema deve impedir que a quantidade confirmada ultrapasse a quantidade solicitada ou a necessidade da missão |
| RNF04 | Imutabilidade dos pedidos encerrados | O resultado de um pedido encerrado não poderá ser alterado por novas respostas |
| RNF05 | Concorrência | Operações simultâneas sobre uma mesma missão devem ser sincronizadas para evitar condições de corrida |
| RNF06 | Documentação | A API deve possuir documentação interativa gerada pelo Swagger UI |
| RNF07 | Modularidade | A implementação deve separar as camadas de API, regras de negócio e persistência |
| RNF08 | Testabilidade | As regras de negócio devem permitir testes automatizados independentes da camada HTTP |

## Histórias de Usuário

| Nome | Ator | Funcionalidade | Critérios de Aceite |
|---|---|---|---|
| 1 - Criar missão | Operador | Criar uma missão informando a estação de origem e a quantidade de pessoas a serem evacuadas | Criada com sucesso de dados válidos e quantidade de pessoas superior a zero |
| 2 - Consultar missões | Operador | Visualizar as missões cadastradas | Deve retornar a lista de missões existentes, incluindo seus identificadores, estações, quantidades de pessoas e estados |
| 3 - Consultar missão | Operador | Consultar os detalhes de uma missão específica | Deve retornar os dados da missão informada ou erro caso ela não exista |
| 4 - Cadastrar nave | Operador | Cadastrar uma nave informando nome e capacidade total | Deve permitir o cadastro com dados válidos e rejeitar capacidades iguais ou inferiores a zero |
| 5 - Consultar naves | Operador | Listar e consultar as naves cadastradas | Deve retornar as naves existentes e seus dados e aviso caso não tenha nenhuma cadastrada |
| 6 - Disponibilizar nave para missão | Operador | Liberar naves a uma missão, informando a quantidade de assentos disponibilizados e o tempo estimado de chegada | Só associado se nave e a missão existirem; a quantidade disponibilizada deve ser positiva e não pode superar a capacidade total da nave; não deve permitir novas dsiponibilizações da mesma nave após a requisição do pedido para essa missão |
| 7 - Consultar naves da missão | Operador | Visualizar as naves disponibilizadas a uma missão | Deve retornar as naves vinculadas à missão, incluindo assentos liberados, previsão de chegada e estado |
| 8 - Criar solicitação | Operador | Solicitar uma quantidade de assentos a uma nave disponibilizada à missão | A quantidade solicitada deve ser positiva, não pode superar os assentos disponibilizados e não pode gerar solicitações acima da necessidade da missão, considerando assentos confirmados e pendentes |
| 9 - Consultar solicitações | Operador | Listar as solicitações realizadas para uma missão. | Deve retornar as solicitações e seus respectivos estados, quantidades solicitadas e confirmadas |
| 10 - Consultar solicitação | Operador | Consultar os detalhes de uma solicitação específica | Deve retornar os dados da solicitação ou erro caso ela não exista |
| 11 - Responder solicitação | Comandante | Informar quantos assentos pode confirmar em resposta a uma solicitação recebida | Deve aceitar confirmações entre zero e a quantidade solicitada; a solicitação deve ser encerrada como confirmada, parcial ou recusada, conforme a resposta |
| 12 - Cancelar solicitação | Operador | Cancelar uma solicitação que ainda não recebeu resposta | Deve permitir o cancelamento somente quando a solicitação estiver pendente; solicitações encerradas não podem ser alteradas |
| 13 - Expirar solicitação | Sistema / Operador | Expirar uma solicitação que não recebeu resposta dentro do prazo estabelecido | Deve permitir a expiração somente após o prazo definido e enquanto a solicitação estiver pendente |
| 14 - Consultar resumo da missão | Operador | Visualizar a situação das reservas e identificar quantos assentos ainda são necessários | Deve apresentar corretamente os assentos confirmados, pendentes e faltantes; a missão só deve ser concluída quando todos os assentos necessários estiverem confirmados |
| 15 - Consultar histórico de eventos | Operador | Consultar as operações e decisões realizadas durante uma missão | Deve apresentar os eventos registrados em ordem cronológica, preservando o histórico das operações |
| 16 - Impedir respostas duplicadas | Sistema | Evitar que mensagens repetidas ou atrasadas alterem solicitações já encerradas | Uma resposta duplicada não deve contabilizar assentos novamente; respostas recebidas após cancelamento, expiração ou outra resposta válida não devem modificar o estado da solicitação |
| 17 - Garantir consistência em operações simultâneas | Sistema | Controlar operações simultâneas para evitar inconsistências nas reservas | A soma dos assentos confirmados e pendentes não deve ultrapassar a quantidade de pessoas da missão, mesmo quando múltiplas operações ocorrerem simultaneamente |
