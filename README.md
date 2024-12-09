# Automação de PDFs <img width=35px src="assets/img/portugues.png">

## Descrição:

Este é um script bem simples que desenvolvi em uma situação muito específica que me ocorreu no trabalho, se quiser saber sobre o que me levou a isso, confira o post que fiz no [LinkedIn](https://matheuspsiqueira.github.io/Portfolio/).

## Como funciona:

Depois de colocar os pdfs em uma pasta junto com o executável e iniciar o programa, ele começa criando a pasta com o nome do arquivo, depois desmembra o pdf todo, considerando titulo, número da página e assunto. Ele identifica o título da página escrito de forma diferente do texto, assim ele classifica e desmembra.

## Tecnologias Utilizadas:

Durante o desenvolvimento, me preocupei em fazer algo prático e que não me tomasse muito tempo, pensando nisso, Python era a melhor opção. Algumas bibliotecas foram utilizadas e estão listadas no requirements.txt.

## Como Testar:

Basta baixar o executável e colocar em uma pasta onde tenha apenas os pdfs que queira desmembrar. Após isso, o script inicia instalando os pacotes (caso necessário) e logo depois começa a desmembrar. Aguarde até o final para abrir as pastas que ele criou.

## Observações:

O programa está em fase inicial, então pode ser que ocorram erros. 
O script não está 100% calibrado, aconselho verificar todos os pdfs desmembrados.
