# Controle de qualidade e armazenamento em uma linha simulada

Trabalho de Algoritmos e Lógica de Programação. O texto explica a solução do LineControl sem inventar citações. As referências bibliográficas da entrega devem ser acrescentadas pelo autor, no padrão pedido pela disciplina, somente com obras que tenham sido de fato consultadas.

## 1. Contextualização da automação industrial

Uma linha de produção repete a mesma verificação muitas vezes. Medir peça por peça no papel funciona em um exercício pequeno e deixa de funcionar quando o volume cresce, quando mais de uma pessoa confere o mesmo lote ou quando o critério muda e cada um lembra de um número diferente. Automação industrial, neste trabalho, não significa um robô físico. Significa transferir uma decisão repetitiva e bem definida para um programa que aplica a mesma regra em toda peça.

O recorte escolhido é o fim da inspeção e o começo do armazenamento. A peça já existe, com peso, cor e comprimento. O sistema decide se ela segue para a caixa ou se fica retida, e registra o motivo. Esse recorte cabe em um trabalho de lógica e ainda mostra um problema real: separar o que pode ser expedido do que precisa voltar para o processo.

## 2. Controle automatizado de qualidade

O critério de aprovação é uma conjunção. A peça passa somente quando o peso está entre 95 g e 105 g, a cor é azul ou verde e o comprimento está entre 10 cm e 20 cm. Os limites entram na conta. Peso 95 g aprova. Peso 94,99 g reprova.

Se qualquer condição falha, o resultado é reprovado. Não basta guardar um único motivo. Uma peça pode estar leve, na cor errada e curta ao mesmo tempo. Guardar só o primeiro problema esconderia os outros e a correção no chão de fábrica ficaria incompleta. Por isso cada critério gera a própria mensagem, sempre na mesma ordem: peso, cor e comprimento. A ordem fixa ajuda a comparar relatórios de dias diferentes.

Há uma diferença importante entre dado inválido e peça reprovada. Texto no campo de peso, número negativo ou campo vazio não descreve uma peça. Esses casos são recusados antes de gravar. Já o peso 80 g descreve uma peça real que não atende ao critério. Ela é gravada como reprovada. Misturar as duas situações faria o relatório de qualidade contar erro de digitação como defeito de fabricação.

## 3. Importância da lógica computacional

O critério cabe em poucos condicionais. O valor do programa está em aplicar esses condicionais sem exceção e em guardar o caminho da decisão. Uma pessoa cansada pode aceitar 106 g “porque está perto”. O programa não faz esse arredondamento informal, a menos que a regra seja escrita assim. Neste projeto ela não é.

A lógica também organiza o que vem depois da decisão. Peça aprovada ocupa um lugar em uma caixa de capacidade 10. Peça reprovada não ocupa. Quando a décima peça entra, a caixa fecha e a seguinte abre outra. Essa sequência é um algoritmo de enchimento, não uma escolha visual da tela. Se a regra ficasse só no HTML, o menu de terminal e um futuro sensor aplicariam outra conta.

Centralizar os números 95, 105, 10, 20 e a capacidade 10 em um único módulo evita que uma página use 100 g como máximo enquanto o relatório ainda fala em 105 g. Mudar o critério passa a ser uma alteração localizada, coberta por teste.

## 4. Estruturação lógica da solução

A solução separa quatro responsabilidades.

O domínio recebe peso, cor e comprimento e devolve aprovado ou a lista de motivos. Ele também calcula, a partir da lista ordenada de peças aprovadas, quais IDs cabem em cada caixa. Essas funções não conhecem Flask nem SQLite. Dá para testá-las com uma lista na memória.

A aplicação é quem cadastra, exclui, lista e monta o relatório. Ela abre a transação, chama o domínio, grava e confirma. Se um passo falha, desfaz o conjunto. A interface web e o menu de terminal chamam essa mesma classe. Nenhum dos dois repete o intervalo de peso.

A infraestrutura traduz isso para tabelas: peças, motivos, caixas e auditoria. A rota só lê o pedido HTTP, chama o caso de uso e escolhe o template.

O fluxo visível para quem apresenta é curto. O formulário envia o ID, o peso, a cor e o comprimento. O serviço normaliza a cor e o ID, valida o número e avalia. Se aprovada, o plano de caixas é recalculado. A ficha mostra o resultado em texto, não só em cor: PEÇA APROVADA ou PEÇA REPROVADA, com os motivos e a caixa quando houver.

## 5. Benefícios

O primeiro benefício é a repetição fiel do critério. Duas peças iguais recebem o mesmo resultado, independente de quem digitou.

O segundo é a explicação. Reprovar sem motivo obriga o operador a medir de novo no escuro. A lista “peso acima do permitido” e “cor não permitida” diz o que olhar.

O terceiro é a organização física simulada. A caixa mostra 7 / 10 ou 10 / 10 fechada. Na apresentação, encher a caixa deixa de ser uma frase e vira um estado visível: a caixa muda de aberta para fechada e a próxima peça aprovada aparece em uma caixa nova.

O quarto é o relatório. Somar aprovadas, reprovadas e motivos à mão é o tipo de tarefa que a lógica substitui bem. O percentual de aprovação sai dos mesmos registros que a tela de peças usa, então o número do dashboard e o número do relatório não divergem por terem sido calculados em lugares diferentes.

## 6. Desafios

O desafio mais visível é a exclusão. Se uma peça sai de uma caixa já fechada, há dois caminhos. O primeiro trata a caixa fechada como lote histórico: ela permaneceria fechada mesmo com nove peças, ou a exclusão dessa peça seria proibida. O segundo recalcula o armazenamento das peças que continuam aprovadas.

Este trabalho segue o segundo caminho. A ordem é determinística: data de cadastro e, no empate, o ID. Assim não existem duas caixas abertas nem uma caixa fechada pela metade. O custo é que o conteúdo de uma caixa fechada pode mudar se uma peça mais antiga for excluída. Para uma linha simulada, em que a caixa ainda não foi expedida de verdade, essa consistência é mais fácil de explicar e de testar do que um lote imutável com buracos.

Outro desafio é a entrada humana. `Azul`, `AZUL` e `azul` precisam ser a mesma cor. Vírgula e ponto precisam ser aceitos como separador decimal, porque o teclado em português usa os dois. Ao mesmo tempo, `10.555` não deve ser silenciosamente arredondado para 10,56 e passar a valer outro lado do limite. O sistema pede no máximo duas casas.

Também é um desafio não transformar o trabalho em uma plataforma. Autenticação, fila de sensores e painel de usuários não foram pedidos. Incluí-los criaria dados pessoais e código que a apresentação não exercita.

## 7. Persistência e rastreabilidade

As peças ficam no SQLite por meio do SQLAlchemy. O ID informado pelo operador é único e é a chave da peça. Os motivos ficam em tabela própria, um registro por falha, o que permite contar “cor não permitida” com uma agregação em vez de interpretar um texto livre.

Peso e comprimento são gravados com duas casas decimais em texto numérico. O SQLite não tem um tipo decimal nativo. Guardar a medida como número de ponto flutuante poderia fazer um valor de fronteira deixar de ser exatamente 95,00. O tipo usado na aplicação converte na entrada e na leitura e preserva a escala.

Cada cadastro, exclusão, criação de caixa, fechamento e reorganização gera uma linha de auditoria com ação, entidade, identificador, data e uma descrição curta. O registro não depende da peça continuar existindo. Por isso a exclusão não apaga a história de que aquela peça foi cadastrada e depois removida.

A migração do esquema fica no Alembic. O banco de teste dos testes automatizados é outro, em memória, para a suíte não escrever no arquivo usado na demonstração.

## 8. Segurança

O sistema é acadêmico e local, mas a entrada vem de um formulário. A validação do navegador melhora o uso e não é a barreira: o servidor repete a checagem. As consultas passam pelo ORM. Os templates escapam o texto por padrão. Os formulários que alteram dados levam token CSRF. A exclusão não é um link de GET, porque um GET não deve apagar registro.

Não há criptografia do arquivo SQLite. A biblioteca que faria isso pede componente nativo e não acrescenta proteção relevante enquanto o arquivo está na mesma máquina de quem apresenta, sem usuários concorrentes e sem dado pessoal. A proteção adotada é minimizar o que se grava, manter o arquivo fora do versionamento e não pedir nome, e-mail ou identificador de operador. A limitação fica declarada em vez de simulada.

Erros de regra, como ID repetido, voltam para o formulário com mensagem. Falha inesperada desfaz a transação, para não sobrar peça sem motivo ou caixa com quantidade diferente das peças vinculadas.

## 9. Possibilidade de integração com sensores

Hoje o peso, a cor e o comprimento são digitados. Em uma linha real, esses três valores nasceriam de instrumentos: balança, sensor de cor ou câmera, e um medidor de comprimento. O encaixe natural é manter a função de avaliação como está e trocar a origem dos números. Um serviço receberia a leitura, montaria o mesmo cadastro e chamaria o caso de uso que o formulário já chama.

Isso só é honesto se a leitura passar pela mesma validação. Sensor com falha pode enviar vazio, negativo ou um número absurdo. Esses casos continuam sendo entrada inválida, não peça reprovada. O motivo de reprovação fica reservado ao critério de qualidade.

## 10. Expansão com IoT

Internet das coisas, neste contexto, seria cada estação publicar a medição e o sistema de qualidade assinar esse evento. A caixa poderia, no sentido contrário, avisar um indicador físico quando fechasse. O algoritmo de capacidade 10 não precisaria mudar. Mudariam o transporte da mensagem e a confirmação de que a leitura chegou uma única vez. Sem essa confirmação, a mesma peça poderia ser cadastrada duas vezes e ocupar dois lugares na caixa.

O protótipo não abre socket nem fala com placa. A separação entre o caso de uso e a página deixa esse passo para um trabalho posterior, quando houver equipamento de verdade para demonstrar.

## 11. Expansão com inteligência artificial

Uma câmera poderia sugerir a cor ou apontar um defeito que o critério numérico não vê, como uma rachadura. O lugar adequado para esse resultado é um sinal a mais na avaliação, com a mesma disciplina: o modelo devolve uma classificação e o sistema registra o motivo em texto compreensível. Não basta uma probabilidade solta na tela.

Também não cabe substituir os limites 95 g e 105 g por um modelo opaco neste trabalho. O critério foi dado pela disciplina e precisa ser auditável. Um classificador poderia conviver com a regra, por exemplo marcando “suspeita visual” além do peso, mas a aprovação pelos três critérios continuaria explícita. Qualquer uso de modelo exigiria conjunto de exemplos real, o que este projeto não possui e não inventa.

## 12. Conclusão

O LineControl mostra um ciclo curto de automação: medir, decidir, explicar e guardar. A lógica cabe em regras fechadas e testadas. A interface existe para esse ciclo ser acompanhado na apresentação, do cadastro até a caixa cheia e o relatório. A persistência guarda a decisão e a trilha. O que ficou de fora — sensor, rede e modelo estatístico — tem um ponto de encaixe claro justamente porque a regra não está espalhada pela página nem pelo menu de terminal.
