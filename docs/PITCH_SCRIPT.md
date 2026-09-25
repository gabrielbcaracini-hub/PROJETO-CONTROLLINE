# Roteiro de apresentação — cerca de 4 minutos

Fale olhando para a tela só quando for mostrar o resultado. O texto abaixo é o que se diz. Os colchetes são ação, não fala.

## Problema — 0:00 a 0:30

Uma linha de inspeção repete a mesma pergunta o dia inteiro: esta peça pode seguir? Quando a resposta fica na cabeça de quem mede, o limite muda de uma pessoa para outra. Peso quase certo passa. Cor escrita de outro jeito gera discussão. E, no fim do turno, ainda é preciso contar quantas foram reprovadas e por quê, e saber em qual caixa está o que foi aprovado.

## Proposta — 0:30 a 0:55

O LineControl faz essa parte. O operador informa o identificador, o peso, a cor e o comprimento. O programa aplica uma regra só: peso entre 95 e 105 gramas, cor azul ou verde, comprimento entre 10 e 20 centímetros. Se os três passam, a peça é aprovada e entra sozinha em uma caixa de 10. Se algum falha, a peça fica reprovada e o sistema guarda cada motivo.

## Funcionamento — 0:55 a 1:25

A regra não está na página. Está no Python, no mesmo serviço que o menu de terminal usa. A tela só mostra a decisão. Peça reprovada não ocupa caixa. Quando a caixa chega a 10, ela fecha e a próxima aprovada abre outra. Se alguém exclui uma peça aprovada, as que restam são reorganizadas pela ordem de cadastro. Assim não ficam duas caixas abertas nem uma caixa fechada pela metade.

## Demonstração — 1:25 a 3:05

[Abrir o dashboard.]

Aqui está o estado da linha: quantas peças entraram, quantas passaram, quantas falharam, a taxa de aprovação e as caixas abertas e fechadas. A atividade recente é a trilha do que acabou de acontecer.

[Ir em Cadastrar peça. Informar um ID novo, peso 100, cor azul, comprimento 15. Enviar.]

A ficha responde em texto: peça aprovada. Todos os critérios foram atendidos, e já aparece o número da caixa.

[Voltar e cadastrar outra: peso 130, cor vermelho, comprimento 25.]

Agora o resultado é peça reprovada. Os motivos estão listados: peso acima do permitido, cor não permitida e comprimento acima do permitido. Não depende só da cor vermelha da faixa. Está escrito.

[Abrir Caixas.]

A caixa aberta mostra a ocupação, por exemplo 7 de 10 peças. A fechada mostra 10 de 10 e o status fechada, com a lista do que está dentro.

[Abrir Relatórios.]

O consolidado repete os totais, o percentual e a quantidade de cada motivo. É o fechamento que, sem o sistema, alguém faria na mão no fim da apresentação.

## Tecnologias — 3:05 a 3:25

O backend é Python com Flask. Os dados ficam no SQLite, com SQLAlchemy e migração. A tela é HTML, CSS e JavaScript nossos, sem framework visual, para a estrutura ficar clara. Os testes são pytest: limites de peso e comprimento, cor, vários motivos juntos, fechamento da caixa, caixa nova e exclusão.

## Diferenciais — 3:25 a 3:40

A mesma regra serve a página e o terminal. O ID não se repete. A cor `Azul` ou `VERDE` é normalizada. Entrada inválida não vira defeito de fábrica: ela é recusada. Entrada válida fora do critério vira reprovação com motivo. Cada operação importante fica na auditoria.

## Resultados — 3:40 a 3:50

Com os dados de demonstração, o sistema já mostra peças aprovadas, peças reprovadas por motivos diferentes, uma caixa fechada e uma caixa ainda aberta. O fluxo inteiro cabe em uma passada: cadastrar, ler o resultado, abrir a caixa e fechar no relatório.

## Possibilidades futuras — 3:50 a 4:05

O próximo passo natural é trocar a digitação por leitura de balança, sensor de cor e medidor de comprimento, chamando o mesmo cadastro. Dá para avisar quando a caixa fechar. Um modelo de visão poderia apontar defeito que a régua não vê, mas os limites de 95 a 105 gramas continuariam explícitos, porque a regra da disciplina precisa ser auditável.

## Encerramento — 4:05 a 4:20

O LineControl mostra a lógica do controle de qualidade do começo ao fim: a peça entra, o programa decide, explica o motivo e guarda o que passou. Obrigado. Posso cadastrar mais uma peça ou abrir a auditoria se quiserem ver o registro da operação.
