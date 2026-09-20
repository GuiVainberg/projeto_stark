1. IP hardcoded.
    - No formulário "Adicionar chave pública da sua organização", o primeiro campo obriga o usuário a restringir por ip.
    - Estranhei que esse campo sempre vem preenchido com o IP 66.103.24.20
    - Pesquisei o IP pelo ipinfo.io e vi que é um IP de SP e pertence a google LLC.
    - Como geralmente um projeto vai rodar dentro da infra da Stark, faz sentido ter ele como default, e o ip do candidato vira um caso de borda.
    - Me levantou uma questão sobre confidencialidade, por ser uma informação de um IP interno exposta a qualquer candidato.
    - Bastaria passar o IP da pessoa que está com o formulário aberto, algo que já vem na request.
    - Pesquisei e vi que tem uma funçãozinha no Flask que faz isso: request.remote_addr
    - Caso a Stark use um proxy por usar GCP, precisaria configurar um campo de ip original no header.
    - Por via das dúvidas, deixei o default e coloquei meu IP também.

2. "Continuar" sem public-key e string.
    - No formulário "Adicionar chave pública da sua organização", o botão de continuar desbloqueia apenas de marcar a checkbox.
    - O campo chave pública precisa ser obrigatório.
    - Além disso, eu posso escrever qualquer string no campo de IPs.
    - Python já tem uma lib nativa que verifica IP chamada ipaddress.

- Depois que vi o erro "Apenas representantes legais tem acesso a essa funcionalidade" que me toquei que estava no form errado. 
- Pensei que eu registraria a chave primeiro e nem me toquei, apesar do readme explicar certinho.
- Ainda acho provável que os pontos que eu levantei façam sentido.
- Não seria nem necessário a possibilidade de um usuário sem acesso poder fazer a requisição.


3. O campo "updated" de um saldo, quando usada a função starkBank.balance.get(), precisa ser tratado pro gmt-3 quando passado para o front.
    - Isso é algo que o front poderia fazer, mas o front é um cliente do contrato com o back e isso deveria vir do back.
    - Além disso, se tiver mais de um front (ex: IOS, Android e Web), todos terão que tratar esse campo, repetindo algo que poderia estar
    centralizado em um BFF.

4. "Issues 8 to 12 invoices every 3 hours to random people for 24 hours"
    - O teste deixa claro que as pessoas são aleatórias, então eu preciso 

5. invoice logs de status
    - Um invoice com status updated deveria continuar no fluxo de paid/canceled?
    - Olhando o contrato, vi que são coisas separadas. Existe o campo updated e o campo status sem a opção de updated.
    - Deve ser uma forma de manter o log dos updates de status.

6. Contrato do invoice
    - fineAmount e interestAmount implica que é necessário fazer uma conversão de float pra int. Python não tem tipagem forte, então existem alguns riscos.
    - "Fee charged in cents" implica em taxa fixa.
    - Para testar o descontos, preciso criar invoices vencidos. Não deve ser problema em um ambiente de sandbox, mas não deve ser possível em produção.
        - É possível criar um invoice com status "overdue" mas com um "due" no futuro?
    - Vale criar invoices com rules diferentes para ver o comportamento.
        - Quais são as possíveis rules? (allowedTaxIds)
    - Vale criar invoices com splits.
    - Quais são as possíveis tags?
        - Qualquer string, parece.
        - É um campo preenchido pelo cliente ou existe alguma lógica interna pra indexar melhor as queries?
    - Gostaria de entender melhor sobre a escolha do nome taxId em vez de document.
    
7. Nomeclatura entre IDs  
    - transactionIds deixa muito claro que tem uma diferença entre o ID da Ledger com o ID da Transfer. Esse é um tipo de nomeclatura que na minha experiência
    vale muito a pena ter cuidado logo no início. Conforme o número de times, produtos oferecidos, microsserviços e bancos de dado aumentam, pessoas diferentes
    entendem e colocam nomes diferentes para o mesmo dado ou nomes iguais para dados diferentes. 
        - Eu enxergo que esse é um problema ainda pior quando falamos de IDs, porque:
            - Uma pessoa não consegue bater o olho em um UUID e saber do que se trata.
            - Rotas de detalhes tem como único dado um /:id
        - Olhando aqui na API, vi que chamam o objeto da Ledger de Transaction, e esse é o contrato geral entre todos os produtos.
        - Vale ficar de olho porque uma Transaction é um nome genérico para qualquer transferência de dinheiro entre duas entidades.
        - Na Stone, eu e meus colegas tivemos dores de cabeça constantes com as nomeclaturas dos IDs vindo de diferentes serviços.
        - Por exemplo: O time que monta o extrato pode precisar bater numa rota de investimentos que pede o ID, mas não sabe se o que eles precisam
        é passar o ID da Ledger ou o ID da Transfer.

8. Contrato incompleto em Create Invoices
    - O campo split aparece na opção de Python mas não aparece nas outras linguagens.
    - Não encontrei o contrato de criar um split na doc online.

9. Já existe uma base de contas pra eu me basear?
    - Não.


Houston, we have a problem!
https://challenge-guilherme-moraes.sandbox.starkbank.com/corporate-card/analytics
GET https://sandbox.api.starkbank.com/v2/corporate-purchase-series/center?step=month&after=2026-04-23&before=2026-09-20 400 (Bad Request)
GET https://sandbox.api.starkbank.com/v2/corporate-purchase-series/category?step=month&after=2026-04-23&before=2026-09-20 400 (Bad Request)
GET https://sandbox.api.starkbank.com/v2/corporate-purchase-series?step=month&after=2026-04-23&before=2026-09-20 400 (Bad Request)
GET https://sandbox.api.starkbank.com/v2/corporate-purchase-series/cardholder?step=month&after=2026-04-23&before=2026-09-20 400 (Bad Request)

https://challenge-guilherme-moraes.sandbox.starkbank.com/corporate-card/holder
GET https://sandbox.api.starkbank.com/v2/corporate-holder?status=active&expand=centerName,rules 500 (Internal Server Error)