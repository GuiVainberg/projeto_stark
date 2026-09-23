# Desafio Técnico Stark Bank: Invoice → Webhook → Transfer

## O que este projeto faz

Emite de 8 a 12 invoices a cada 3 horas, por 24 horas, para destinatários aleatórios. Ao receber a
confirmação de crédito de cada invoice via webhook, transfere o valor líquido (amount − fee) para a
conta indicada no desafio.

## Estrutura

```
app/            código-fonte (webhook, serviço de transfer, log/idempotência, emissor de invoices, cliente Stark, scheduler)
tests/          testes unitários, um arquivo por módulo de app/
keys/           chaves ECDSA (a privada não vai pro repositório)
```

## Como rodar

```bash
pip install -r requirements.txt
```

Configurar `.env` com `privateKeyPath` e `projectID`.

Rode esses três processos, em terminais separados, todos a partir da raiz do projeto:

```bash
python app/webhook.py                                  # recebe os webhooks
ngrok http 5000 --url <seu-domínio>                     # expõe o webhook
python app/scheduler.py                                 # dispara as invoices a cada 3h
```

## Testes

```bash
python -m unittest discover -s tests -t .
```

21 testes com mock.

Cobertura: emissão de invoice, geração de CPF/CNPJ válido, handler do webhook, cálculo do valor líquido da transfer e leitura de variável de ambiente obrigatória.

## Decisões de arquitetura

### Escolha de framework pra API

Pesquisando, fiquei na dúvida se usava FastAPI ou Flask. Pra esse projeto, o SDK da Stark é síncrono, são só dois endpoints 
e não tem necessidade de schema. Considerei que é um projeto simples que ele ficaria melhor se fosse enxuto, então escolhi o Flask. 

### Separação de responsabilidades

O webhook começou como um único arquivo criando a rota HTTP. Fui adicionando controle de idempotência, decisão de
negócio, montagem de dados e persistência de log ao mesmo tempo. Preferi dividir em:

- `webhook.py`: só a rota Flask, orquestra as chamadas.
- `transfer_service.py`: decide quando e como criar a transfer.
- `event_log.py`: idempotência (`processed_ids`) e persistência do log de eventos.
- `invoice_factory.py`: geração das invoices.

### Idempotência e persistência

Um `set()` em memória barra o evento caso ele já tenha chegado, garantindo a idempotência junto com o `external_id` na Transfer. Testando um `external_id` duplicado,
descobri que a Transfer é criada e nasce com `status=failed`, sem nenhum `transaction_ids`.

O `set()` no começo vivia só em memória, então se o processo reiniciasse esquecia tudo que já tinha
processado. Pensei se valia a pena criar um DB pra persistência, mas por conta do prazo apertado e pesquisando um pouco, criei a função `load_processed_ids()` para repovoar esse `set()`. A função lê o event_id de cada linha do `webhook.log` assim que o `webhook.py` sobe.

### Resiliência: retry com backoff 

Para erros 5xx ou problemas de conexão, fiz a função `create_transfer_with_retry` com backoff de 0.5s, 1s e 2s, garantindo
que o erro seja apenas um problema momentâneo do servidor ou da minha conexão.

### Refatoração dos dados de invoice 

O `tax_id` inicial era fixo pra todo invoice e isso não cobria de verdade o "pessoas aleatórias" do
enunciado. Troquei por geração de CPF/CNPJ usando a biblioteca `validate-docbr` e geração de nomes
com a biblioteca `Faker`.

Essa refatoração foi feita após iniciar o scheduler.py, que roda por 24h gerando os invoices há cada 3h. 
Optei por não reiniciar o processo pra aplicar a refatoração para não comprometer o prazo, então a corrida registrada
abaixo ainda usa os dados antigos (nome fixo entre 4 opções, tax_id fixo). O código atual do repositório
já é a versão nova.


## Bugs e inconsistências encontrados

1. **Bug de tipo no SDK ao usar Flask.** `request.data` chega como `bytes`, e o `parse_and_verify` do
   `starkcore` repassa isso direto pro `Ecdsa.verify`, que assume `str` e tenta fazer `.encode()`. O
   resultado é `AttributeError: 'bytes' object has no attribute 'encode'`. Corrigi do meu lado com
   `request.data.decode("utf-8")` antes do parse. Rastreei a causa raiz até o pacote `ellipticcurve`, e
   tenho um fix pro upstream (`starkinfra/core-python`) pronto pra abrir depois do processo.

2. **500 Internal Server Error e 400 Bad Request no dashboard de Corporate Card do sandbox.**
   `/v2/corporate-holder` devolve 500, e quatro rotas de `/v2/corporate-purchase-series/*` devolvem 400.
   Reproduz só navegando nas telas correspondentes do painel.

3. **`account_type` diferente entre a documentação e o SDK.** A doc lista como opcional (`checking` como
   default), mas o SDK Python exige ele como posicional obrigatório no `Transfer.__init__`.


## Resultados da corrida de 24h

Isso aqui é parcial, a corrida ainda está rodando no momento desse commit, com 3 dos 8 ciclos
concluídos.

- Invoices emitidos: 25
- Invoices pagos/creditados: 23
- Transfers realizadas: 23 (sucesso: 23, falha: 0)
- Duplicatas detectadas: 0, auditei por `event_id` (todos únicos) e por `external_id`→`transfer_id`
  (relação 1 para 1, nenhum `external_id` gerou mais de uma transfer)

Atualizo os números finais dos 8 ciclos aqui quando a corrida terminar (~14h47 do dia seguinte ao
início).

## O que eu aprendi

Percebi que webhook nesse projeto exige pensar em duas camadas de idempotência. Isso porque segue 
o padrão at-least-once, então eventos duplicados são esperados. Vi que se eu mandar o transfer.create 
com um external_id repetido, a API sempre devolve um objeto Transfer com status=failed, então não
adianta olhar só quando estoura uma exception. Por isso fiz um `set()` que guarda os ids dos eventos 
em memória, checa se o id foi processado e se não, usa esse valor como external_id pra mandar pra transfer.

Uma coisa que peguei no caminho e não esperava era que dois processos webhook conseguem escutar a mesma porta 
no Windows sem erro. O processo que rodei no dia 21 tinha ficado de pé e eu subi outro dia 22 que não tomou erro. 
Os dois ficaram ouvindo a mesma porta mas claramente concorrendo, e o do dia 21 acabou capturando antes, o que 
acabou me atrapalhando em visualizar as chamadas.

Como optei por focar mais no aprendizado, na compreensão da API e dos processos do time de TI da Stark,
fiz a escolha de não automatizar nenhuma configuração ou escrever a solução mais robusta para produção. 
Dessa forma algumas escolhas como usar um Banco de Dados, colocar o programa na núvem, escolher design 
pattern e implementar um padrão de desenvolvimento específico foram despriorizados.

Isso me permitiu absorver muito mais a cultura de código e fluxo de trabalho do time da Stark, mas houve
um trade-off de coisas que poderiam ter ficado melhores. Por exemplo, o código `stark_client.py` ficou fora 
de uma função, o que trava teste isolado e mock quando dou import. Só percebi isso na hora de escrever os 
testes, que optei por deixar para o fim em vez de seguir um TDD clássico.

Também houve momentos que fiquei explorando e pensando em soluções que fugiam do escopo desse desafio, como
a decisão de negócio de algumas telas do ambiente de sandbox, a reflexão sobre o nome transactionId e o review
da documentação.

## Se tivesse mais tempo

- Deploy em Cloud Run (GCP) como bônus, aproveitando stack já usada pela equipe de engenharia
  da Stark.
- Aplicar Terraform após subir na nuvem.
- Banco de dados para persistência mais segura dos eventos.
- Refatorar o objeto de invoice e dos testes pra gerar casos de split, com discount, atrasados etc
- Refatorar o stark_client.py pra não rodar código no import
- Teste de integração leve pra exercitar a verificação de assinatura real
- Abrir o PR de correção no `starkinfra/core-python`.
- Usar o Github Actions para CI rodar os testes automaticamente a cada push
