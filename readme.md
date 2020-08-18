
# CartolaOR

_Esta é uma aplicação que recomenda a escalação da rodada para o fantasy game Cartola FC através de um modelo matemático._

  

## Tecnologias:

*  [Python](https://www.python.org/)

*  [Google OR Tools](https://developers.google.com/optimization)

## Modelo matemático
Nome modelo matemático para cada jogador é levado em consideração sua média. Um jogador pode ter os seguintes acréscimos em seu valor:
* $1$, se seu clube é o mandante da partida;
* $\frac{PG_{clube}}{P_{total}}$, onde $PG_{clube}$ são os pontos ganhos do seu clube e $P_{total}$ é o somatório dos pontos ganhos de todos os clubes;
* $2-\frac{P_{clube}}{10}$, onde $P_{clube}$ é a posição de seu clube na tabela.

## Fontes de dados
* Mercado: API Cartola FC (https://api.cartolafc.globo.com/atletas/mercado);
* Partidas: API Cartola FC (https://api.cartolafc.globo.com/partidas/[RODADA]), onde [RODADA] é o numeral da rodada de 0 a 37;
* Classificação: UFMG (http://www.mat.ufmg.br/futebol/classificacao-geral_seriea/)

##### Notas

Esta aplicação está sendo usando neste ano de 2020 para observação do resultados no time CaiçaraPy.
