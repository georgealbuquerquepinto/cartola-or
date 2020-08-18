
# CartolaOR

_Esta é uma aplicação que recomenda a escalação da rodada para o fantasy game Cartola FC através de um modelo matemático._

  

## Tecnologias:

*  [Python](https://www.python.org/)

*  [Google OR Tools](https://developers.google.com/optimization)

## Modelo matemático
Nome modelo matemático para cada jogador é levado em consideração sua média. Um jogador pode ter os seguintes acréscimos em seu valor:
* ![equation](https://latex.codecogs.com/gif.latex?1), se seu clube é o mandante da partida;
* ![equation](https://latex.codecogs.com/gif.latex?\frac{PG_{clube}}{P_{total}}), onde ![equation](https://latex.codecogs.com/gif.latex?PG_{clube}) são os pontos ganhos do seu clube e ![equation](https://latex.codecogs.com/gif.latex?P_{total}) é o somatório dos pontos ganhos de todos os clubes;
* ![equation](https://latex.codecogs.com/gif.latex?2-\frac{Pos_{clube}}{10}), onde ![equation](https://latex.codecogs.com/gif.latex?Pos_{clube}) é a posição de seu clube na tabela.

## Fontes de dados
* Mercado: API Cartola FC (https://api.cartolafc.globo.com/atletas/mercado);
* Partidas: API Cartola FC (https://api.cartolafc.globo.com/partidas/[RODADA]), onde [RODADA] é o numeral da rodada de 0 a 37;
* Classificação: UFMG (http://www.mat.ufmg.br/futebol/classificacao-geral_seriea/)

##### Notas

Esta aplicação está sendo usando neste ano de 2020 para observação do resultados no time CaiçaraPy.
