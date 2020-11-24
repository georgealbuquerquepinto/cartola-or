# :tophat: CartolaOR

_Esta é uma aplicação que recomenda a escalação da rodada para o fantasy game Cartola FC através de um modelo matemático._

## 💻 Sobre

O cartoleiro precisa tomar decisões para tentar maximizar a sua pontuação em cada rodada. Estas decisões podem ser:

  * Escolher os melhores jogadores por posição.
  * Escolher o melhor esquema tático para cada rodada.
  * Escolher os jogadores que estejam dentro dos limites de cartoletas existentes na carteira.

Tomar estas decisões é um grande desafio. Em nossa solução atual, buscamos desenvolver um modelo matemático de otimização considerando esquemas táticos disponíveis no Cartola FC. Para solucionar estes problemas estamos utilizando programação linear inteira.  

## 🚀 Tecnologias

*  [Python](https://www.python.org/)

*  [Google OR Tools](https://developers.google.com/optimization)

## :1234: Modelo matemático
* Restrições:
  * O custo da escalação é restrito ao limite de cartoletas disponíveis;

  - A escalação tem:
    - exatamente 11 jogadores e 1 técnico, onde 1 jogador é um goleiro;

    - no mínimo 2 e no máximo 3 zagueiros;

    - ou 0 ou 2 laterais;

    - A defesa (laterais e zagueiros) tem no mínimo 3 e no máximo 5 jogadores;

    - no mínimo 3 e no máximo 5 meio-campistas;

    - no mínimo 1 e no máximo 3 atacantes.

* O objetivo do modelo matemático é maximizar o somatório do valor dos jogadores. Para cada jogador é levado em consideração sua média de pontuação. Além disso cada jogador pode ter os seguintes acréscimos em seu valor:
  - ![equation](https://latex.codecogs.com/gif.latex?1), se seu clube é o mandante da partida;
  - ![equation](https://latex.codecogs.com/gif.latex?\frac{PG_{clube}}{P_{total}}), onde ![equation](https://latex.codecogs.com/gif.latex?PG_{clube}) são os pontos ganhos do seu clube e ![equation](https://latex.codecogs.com/gif.latex?P_{total}) é o somatório dos pontos ganhos de todos os clubes;
  - ![equation](https://latex.codecogs.com/gif.latex?2-\frac{Pos_{clube}}{10}), onde ![equation](https://latex.codecogs.com/gif.latex?Pos_{clube}) é a posição de seu clube na tabela.

* O jogador com maior valor na escalação é escolhido o capitão do time.

## :file_cabinet: Fontes de dados
* Mercado (média, status, preço de cada jogador): API Cartola FC (https://api.cartolafc.globo.com/atletas/mercado);
* Partidas: API Cartola FC (https://api.cartolafc.globo.com/partidas/[RODADA]), onde [RODADA] é o numeral da rodada de 0 a 37;
* Classificação do campeonato: UFMG (http://www.mat.ufmg.br/futebol/classificacao-geral_seriea/)

## :bar_chart: Resultados
| Rodada | Pontuação | Variação (Cartoletas)|
|--:|--:|--:|
|01|34.53|-3.85|
|02|30.81|15.43|
|03|27.78|-7.28|
|04|2.59|-9.7|
|05|46.74|-3.98|
|06|31.84|-4.65|
|07|33.65|-2.38|
|08|37.19|-1.63|
|09|109.50|8.37|
|10|23.30|-9.30|
|11|29.23|-3.98|
|12|30.95|-2.93|
|13|46.79|1.74|
|14|104.63|7.97|
|15|35.81|-1.68|
|16|22.95|-3.58|
|17|23.53|-3.95|
|18|75.03|3.23|
|19|18.35|-3.71|
|20|21.78|-4.08|
|21|40.93|1.70|
|22|22.99|-3.43|

##### :paperclip: Notas

Esta aplicação está sendo usando neste ano de 2020 para observação do resultados no time CaiçaraPy.
