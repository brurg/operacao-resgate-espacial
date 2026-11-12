# Enunciado Processo Seletivo

## Especificações 

1. A quantidade de pessoas a evacuar deve ser informada como entrada de cada missão.
2. Naves com diferentes capacidades e tempos de chegada.
3. Central deve distribuir pedidos entre as naves e acompanhar as confirmações até garantir um assento para cada pessoa.
4. Uma nave pode confirmar toda a quantidade solicitada, confirmar apenas parte dela ou recusar. 
5. Nem todos comandantes respondem na mesma hora.
6. Essencial saber se ainda falta pedir ajuda.
7. Não deve mobilizar naves além do necessário.
8. Não deve contar com vagas que ninguém confirmou.
9. Uma confirmação parcial encerra a resposta daquele pedido: outro pedido para as vagas que não foram confirmadas.
10. Cancelar um pedido ainda sem resposta ou encerrá-lo por falta de resposta.
11. A reserva de transporte só está completa quando há vagas confirmadas para todas as pessoas da missão.
12. Uma nave não pode confirmar mais vagas do que recebeu no pedido.
13. Preservar decisões encerradas. Depois de respondido, cancelado ou expirado, um pedido não pode ter seu resultado alterado por uma nova resposta.
14. Mensagens repetidas, atrasadas ou fora de ordem e operações simultâneas não podem distorcer o andamento do resgate.
15. Uma missão não pode ser criada com zero pessoas;
16. Uma nave pode participar de mais de uma missão;
17. Não podem ser cadastradas mais naves após o recebimento da missão;.

## Funções do Sistema 

1. Cadastro de missão;
2. Receber informação das naves disponíveis;
3. Mostrar informação das naves disponíveis;
4. Consultar uma nave;
5. Consultar missões;
6. Consultar informação da missão;
7. Enviar pedido de reserva de X lugares pras naves;
8. Receber respostas das naves;
9. Atualizar status dos pedidos;
10. Consultar informação dos pedidos;
11. Consultar pedido;
12. Cancelar pedido;
13. Expirar pedido;
14. Consultar o histórico de eventos da missão;

## Elementos e atributos

Missão = id, estação, qntde de pessoas, status (reservada, pendente, cancelada)
Nave = id, capacidade total, vagas disponiveis, tempo estimado de chegada, status (cheia, disponível) 
Pedido = id, nave, quantidade de pessoas, vagas confirmadas, em aguardo de confirmação ou recusadas, status (confirmado, pendente, parcial, indisponível, cancelado)

## Estratégia de distribuição das vagas

Cabe ao sistema decidir quais naves acionar e quantas vagas pedir a cada uma, considerando as informações disponíveis e as regras da missão.
Explique no README os critérios escolhidos, as premissas assumidas e como sua solução lida com mudanças de disponibilidade ao longo do resgate.
Envios de pedidos e respostas das naves podem ocorrer em paralelo. Explique, ou implemente, como você garante a consistência nessas situações.

## Caso de teste

Demonstração em que a missão precise da ajuda de várias naves. 
Uma delas confirma menos vagas do que o solicitado e outra recusa. 
A central deve conseguir acompanhar a situação e buscar a ajuda que ainda falta.

Escolha os dados da demonstração e os cenários de teste. Mostre como você verifica que a solução cumpre os compromissos da central, inclusive quando a comunicação não acontece como esperado.

## Enunciado completo

### Operação Resgate Espacial

#### O sinal de emergência

Uma tempestade solar está a caminho da estação Aurora. Os escudos não vão resistir, e as pessoas a bordo precisam de transporte para sair de lá. 
A quantidade de pessoas a evacuar deve ser informada como entrada de cada missão.

Há naves nas proximidades, com diferentes capacidades e tempos de chegada. A central precisa coordenar a ajuda dos comandantes: alguns confirmam todas as vagas solicitadas, outros oferecem apenas parte delas, e outros recusam. Nem todos respondem na mesma hora.

Sua missão: construir o sistema da central de resgate, distribuindo pedidos entre as naves e acompanhando as confirmações até garantir um assento para cada pessoa.

#### O problema da central

Hoje, a equipe coordena o resgate pelo rádio e registra as respostas em uma planilha. Com vários operadores trabalhando ao mesmo tempo, é difícil saber se ainda falta pedir ajuda, se basta aguardar as respostas ou se o transporte de todos já está garantido.

Mobilizar naves além do necessário pode prejudicar outros resgates. Por outro lado, contar com vagas que ninguém confirmou pode deixar pessoas para trás. A central precisa de informações confiáveis para tomar essas decisões.

O escopo termina na confirmação das reservas. Não é necessário simular voos, embarques, rotas ou a tempestade solar.

#### O que o sistema deve fazer

##### Receber uma missão de resgate

Permitir cadastrar uma missão, identificando a estação e a quantidade de pessoas que precisam de transporte. A central também recebe informações sobre as naves disponíveis, incluindo a capacidade oferecida e o tempo estimado de chegada.

##### Acompanhar o resgate

Permitir que um operador consulte a situação da missão e dos pedidos enviados às naves. As informações apresentadas devem ajudá-lo a entender o que já está garantido, o que ainda depende de resposta e se é necessário buscar mais ajuda. Defina como representar e apresentar esse acompanhamento.

##### Coordenar os pedidos

Enviar pedidos de vagas às naves e processar suas respostas. Uma nave pode confirmar toda a quantidade solicitada, confirmar apenas parte dela ou recusar. Uma confirmação parcial encerra a resposta daquele pedido: a central precisará buscar em outro pedido as vagas que não foram confirmadas.

Também deve ser possível cancelar um pedido ainda sem resposta ou encerrá-lo por falta de resposta. O sistema deve permitir continuar a mobilização quando a ajuda obtida não for suficiente.

#### Compromissos da central

Evitar pedidos em excesso. Ao solicitar novas vagas, a central precisa considerar tanto as confirmações recebidas quanto os pedidos que ainda podem ser aceitos.
Concluir com segurança. A reserva de transporte só está completa quando há vagas confirmadas para todas as pessoas da missão.
Respeitar o que foi solicitado. Uma nave não pode confirmar mais vagas do que recebeu no pedido. Quantidades informadas devem ser válidas para o contexto.
Preservar decisões encerradas. Depois de respondido, cancelado ou expirado, um pedido não pode ter seu resultado alterado por uma nova resposta.
Manter informações confiáveis. Mensagens repetidas, atrasadas ou fora de ordem e operações simultâneas não podem distorcer o andamento do resgate. Operações inválidas não devem comprometer os dados já registrados.
As escolhas de modelagem e os mecanismos usados para cumprir esses compromissos fazem parte da solução.

#### Estratégia de mobilização

Cabe ao sistema decidir quais naves acionar e quantas vagas pedir a cada uma, considerando as informações disponíveis e as regras da missão.

Defina e implemente uma estratégia. Explique no README os critérios escolhidos, as premissas assumidas e como sua solução lida com mudanças de disponibilidade ao longo do resgate.

#### Demonstração da solução

Prepare uma demonstração em que a missão precise da ajuda de várias naves. Durante a mobilização, uma delas confirma menos vagas do que o solicitado e outra recusa. A central deve conseguir acompanhar a situação e buscar a ajuda que ainda falta.

Escolha os dados da demonstração e os cenários de teste. Mostre como você verifica que a solução cumpre os compromissos da central, inclusive quando a comunicação não acontece como esperado.

#### Requisitos técnicos e limites do exercício

Linguagem à sua escolha (Java, Python, C#, TypeScript…).
A persistência pode ser em memória.
Não é obrigatório criar interface gráfica, API HTTP, serviço de mensagens ou integração externa. Chamadas de métodos e simulações são suficientes.
Envios de pedidos e respostas das naves podem ocorrer em paralelo. Explique, ou implemente, como você garante a consistência nessas situações.
Cancelamento e expiração podem ser simulados. Não é necessário implementar temporizadores reais.
Capacidades e estimativas de chegada podem ser fornecidas como dados de entrada. O controle global da frota entre diferentes missões fica fora do escopo.
Você pode usar ferramentas de IA (ChatGPT, Copilot, Claude etc.) para resolver o exercício. Esteja preparado para explicar suas decisões e o funcionamento da solução entregue.
 
#### Entregáveis

Código-fonte em repositório Git ou arquivo compactado.
Testes automatizados cobrindo os cenários que você considera relevantes.
README com instruções para executar a demonstração e os testes, decisões de design e premissas assumidas.
 
#### Diferenciais

Incentivamos que você vá além do que foi pedido, com funcionalidades extras que façam sentido para o problema.

Alguma ambiguidade? Assuma o que fizer mais sentido e registre a premissa no README. Queremos entender como você transforma as necessidades da central em uma solução e como sustenta suas decisões.
