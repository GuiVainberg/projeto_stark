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


3. starkBank.balance.get() precisa ser tratado pro gmt-3.