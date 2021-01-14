import requests
from bs4 import BeautifulSoup
from ortools.linear_solver import pywraplp

gol_id = 1
lat_id = 2
zag_id = 3
mei_id = 4
ata_id = 5
tec_id = 6

def mercadoAberto():
  url_status_mercado = 'https://api.cartolafc.globo.com/mercado/status'

  status_mercado = requests.get(url_status_mercado).json()['status_mercado']

  return status_mercado == 1

def getClassificacao():
  CLUBES = {
    'ATHLETICO-PR' : { 'id': 293 },
    'ATLÉTICO-GO'  : { 'id': 373 },
    'ATLÉTICO-MG'  : { 'id': 282 },
    'BAHIA'        : { 'id': 265 },
    'BOTAFOGO'     : { 'id': 263 },
    'BRAGANTINO'   : { 'id': 280 },
    'CEARÁ'        : { 'id': 354 },
    'CORINTHIANS'  : { 'id': 264 },
    'CORITIBA'     : { 'id': 294 },
    'FLAMENGO'     : { 'id': 262 },
    'FLUMINENSE'   : { 'id': 266 },
    'FORTALEZA'    : { 'id': 356 },
    'GOIÁS'        : { 'id': 290 },
    'GRÊMIO'       : { 'id': 284 },
    'INTERNACIONAL': { 'id': 285 },
    'PALMEIRAS'    : { 'id': 275 },
    'SANTOS'       : { 'id': 277 },
    'SPORT'        : { 'id': 292 },
    'SÃO PAULO'    : { 'id': 276 },
    'VASCO DA GAMA': { 'id': 267 }
  }

  url = 'http://www.mat.ufmg.br/futebol/classificacao-geral_seriea/'

  html_content = requests.get(url).text
  bs = BeautifulSoup(html_content, 'lxml')

  tabela = bs.find('table', attrs={'id': 'tabelaCL'}).tbody.find_all('tr')
  classificacao = []

  for i in range(len(tabela)):
    clube = {}
    linha = []

    for td in tabela[i].find_all('td'):
      linha.append(td.text.replace('\n', ' ').strip())
    
    clube['nome']  = linha[1]
    clube['clube'] = CLUBES[str(linha[1])]['id']
    clube['pos']   = linha[0]
    clube['pts']   = linha[2]
    
    classificacao.append(clube)

  return classificacao

def getMercado():
  url_mercado  = 'https://api.cartolafc.globo.com/atletas/mercado'
  url_partidas = 'https://api.cartolafc.globo.com/partidas/%s'
  
  mercado = requests.get(url_mercado)
  
  atletas  = mercado.json()['atletas']
  clubes   = mercado.json()['clubes']
  rodada   = int(atletas[0]['rodada_id'])
  partidas = requests.get(url_partidas % (rodada + 1)).json()['partidas']

  classificacao = getClassificacao()

  return atletas, clubes, partidas, classificacao

def solver(CLUBES, GOL, LAT, ZAG, MEI, ATA, TEC, cartoletas, ptsTotal):
  # Definição do solver
  solver = pywraplp.Solver('simple_lp_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

  # Declaração da variável binárias que representam os jogadores por posição
  # A variável recebe 1, se o jogador foi selecionado, ou 0, caso contrário
  GOL_b = {}
  LAT_b = {}
  ZAG_b = {}
  MEI_b = {}
  ATA_b = {}
  TEC_b = {}

  # Definição das variáveis binárias dos goleiros
  for i in range(len(GOL)):
    GOL_b[i] = solver.BoolVar('GOL_b[{}]'.format(i))

  # Definição das variáveis binárias dos laterais
  for i in range(len(LAT)):
    LAT_b[i] = solver.BoolVar('LAT_b[{}]'.format(i))

  # Definição das variáveis binárias dos zagueiros
  for i in range(len(ZAG)):
    ZAG_b[i] = solver.BoolVar('ZAG_b[{}]'.format(i))

  # Definição das variáveis binárias dos meias
  for i in range(len(MEI)):
    MEI_b[i] = solver.BoolVar('MEI_b[{}]'.format(i))

  # Definição das variáveis binárias dos atacantes
  for i in range(len(ATA)):
    ATA_b[i] = solver.BoolVar('ATA_b[{}]'.format(i))

  # Definição das variáveis binárias dos técnicos
  for i in range(len(TEC)):
    TEC_b[i] = solver.BoolVar('TEC_b[{}]'.format(i))

  # Variável binária para definir se o escalação possui laterais.
  # A variável recebe 1, se será escalado laterais, ou 0, caso contrário
  z = solver.BoolVar('z')

  # Restrições de quantidade de jogadores por posição
  # A escalação deve ter 1 goleiro
  solver.Add(solver.Sum(GOL_b[i] for i in range(len(GOL_b))) == 1)
  # A escalação deve ter 0 ou 2 laterais
  solver.Add(solver.Sum(LAT_b[i] for i in range(len(LAT_b))) == 2 * z)
  # A escalação deve ter no mínimo 2 zagueiros
  solver.Add(solver.Sum(ZAG_b[i] for i in range(len(ZAG_b))) >= 2)
  # A escalação deve ter no máximo 3 zagueiros
  solver.Add(solver.Sum(ZAG_b[i] for i in range(len(ZAG_b))) <= 3)
  # A escalação deve ter no mínimo 2 meias
  solver.Add(solver.Sum(MEI_b[i] for i in range(len(MEI_b))) >= 3)
  # A escalação deve ter no máximo 5 meias
  solver.Add(solver.Sum(MEI_b[i] for i in range(len(MEI_b))) <= 5)
  # A escalação deve ter no mínimo 1 atacante
  solver.Add(solver.Sum(ATA_b[i] for i in range(len(ATA_b))) >= 1)
  # A escalação deve ter no máximo 3 atacantes
  solver.Add(solver.Sum(ATA_b[i] for i in range(len(ATA_b))) <= 3)
  # A escalação deve ter 1 técnico
  solver.Add(solver.Sum(TEC_b[i] for i in range(len(TEC_b))) == 1)

  # Restrição para a defesa ter pelo menos 3 jogadores
  solver.Add(
    solver.Sum(LAT_b[i] for i in range(len(LAT_b))) +
    solver.Sum(ZAG_b[i] for i in range(len(ZAG_b))) >= 3
  )

  # Restrição para definir a escalação com 12 jogadores
  solver.Add(
    solver.Sum(GOL_b[i] for i in range(len(GOL_b))) +
    solver.Sum(LAT_b[i] for i in range(len(LAT_b))) +
    solver.Sum(ZAG_b[i] for i in range(len(ZAG_b))) +
    solver.Sum(MEI_b[i] for i in range(len(MEI_b))) +
    solver.Sum(ATA_b[i] for i in range(len(ATA_b))) +
    solver.Sum(TEC_b[i] for i in range(len(TEC_b))) == 12)

  # Restrição para limitar o preço da escalação
  solver.Add(
    solver.Sum(GOL[i]['preco_num'] * GOL_b[i] for i in range(len(GOL_b))) +
    solver.Sum(LAT[i]['preco_num'] * LAT_b[i] for i in range(len(LAT_b))) +
    solver.Sum(ZAG[i]['preco_num'] * ZAG_b[i] for i in range(len(ZAG_b))) +
    solver.Sum(MEI[i]['preco_num'] * MEI_b[i] for i in range(len(MEI_b))) +
    solver.Sum(ATA[i]['preco_num'] * ATA_b[i] for i in range(len(ATA_b))) +
    solver.Sum(TEC[i]['preco_num'] * TEC_b[i] for i in range(len(TEC_b))) <= cartoletas)

  # Função objetivo
  solver.Maximize(
    solver.Sum((GOL[i]['media_num'] + (CLUBES[str(GOL[i]['clube'])]['casa']) + (CLUBES[str(GOL[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(GOL[i]['clube'])]['pos'] / 10.0))) * GOL_b[i] for i in range(len(GOL_b))) +
    solver.Sum((LAT[i]['media_num'] + (CLUBES[str(LAT[i]['clube'])]['casa']) + (CLUBES[str(LAT[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(LAT[i]['clube'])]['pos'] / 10.0))) * LAT_b[i] for i in range(len(LAT_b))) +
    solver.Sum((ZAG[i]['media_num'] + (CLUBES[str(ZAG[i]['clube'])]['casa']) + (CLUBES[str(ZAG[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(ZAG[i]['clube'])]['pos'] / 10.0))) * ZAG_b[i] for i in range(len(ZAG_b))) +
    solver.Sum((MEI[i]['media_num'] + (CLUBES[str(MEI[i]['clube'])]['casa']) + (CLUBES[str(MEI[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(MEI[i]['clube'])]['pos'] / 10.0))) * MEI_b[i] for i in range(len(MEI_b))) +
    solver.Sum((ATA[i]['media_num'] + (CLUBES[str(ATA[i]['clube'])]['casa']) + (CLUBES[str(ATA[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(ATA[i]['clube'])]['pos'] / 10.0))) * ATA_b[i] for i in range(len(ATA_b))) +
    solver.Sum((TEC[i]['media_num'] + (CLUBES[str(TEC[i]['clube'])]['casa']) + (CLUBES[str(TEC[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(TEC[i]['clube'])]['pos'] / 10.0))) * TEC_b[i] for i in range(len(TEC_b)))
  )

  # Resolvendo o problema
  solucao = solver.Solve()

  # Exibindo a solução
  print('\033[1mSOLUÇÃO\033[0m')
  print('Valor da função objetivo = %.2f' % solver.Objective().Value())
  print('Tempo = ', solver.WallTime(), ' ms')

  esquema = {
    'defesa': 0,
    'meia': 0,
    'ataque': 0
  }
  custoEscalacao = 0
  capitao = {
    'pontos': 0,
    'jogador': None,
    'clube': None,
    'pos': None
  }

  print('┌─────┬──────────────────────┬─────────────────┬───────┐')
  print('│\033[1m POS \033[0m│\033[1m %-20s \033[0m│\033[1m %-15s \033[0m│ \033[1m%s \033[0m│' % ('JOGADOR', 'TIME', 'PREÇO'))
  print('├─────┼──────────────────────┼─────────────────┼───────┤')

  for i in range(len(GOL)):
    if GOL_b[i].solution_value() > 0:
      print('│ GOL │ %-20s │ %-15s │ %5.2f │' % (GOL[i]['apelido'], CLUBES[str(GOL[i]['clube'])]['nome'], GOL[i]['preco_num']))
      
      custoEscalacao += GOL[i]['preco_num']
      pts = GOL[i]['media_num'] + (CLUBES[str(GOL[i]['clube'])]['casa']) + (CLUBES[str(GOL[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(GOL[i]['clube'])]['pos'] / 10.0))
      
      if pts >= capitao['pontos']:
        capitao['pontos'] = pts
        capitao['jogador'] = GOL[i]['apelido']
        capitao['clube'] = CLUBES[str(GOL[i]['clube'])]['nome']
        capitao['pos'] = 'GOL'

  for i in range(len(LAT)):
    if LAT_b[i].solution_value() > 0:
      print('│ LAT │ %-20s │ %-15s │ %5.2f │' % (LAT[i]['apelido'], CLUBES[str(LAT[i]['clube'])]['nome'], LAT[i]['preco_num']))
      
      esquema['defesa'] += 1      
      custoEscalacao += LAT[i]['preco_num']      
      pts = LAT[i]['media_num'] + CLUBES[str(LAT[i]['clube'])]['casa'] + (CLUBES[str(LAT[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(LAT[i]['clube'])]['pos'] / 10.0))

      if pts >= capitao['pontos']:
        capitao['pontos'] = pts
        capitao['jogador'] = LAT[i]['apelido']
        capitao['clube'] = CLUBES[str(LAT[i]['clube'])]['nome']
        capitao['pos'] = 'LAT'

  for i in range(len(ZAG)):
    if ZAG_b[i].solution_value() > 0:
      print('│ ZAG │ %-20s │ %-15s │ %5.2f │' % (ZAG[i]['apelido'], CLUBES[str(ZAG[i]['clube'])]['nome'], ZAG[i]['preco_num']))

      esquema['defesa'] += 1
      custoEscalacao += ZAG[i]['preco_num']
      pts = ZAG[i]['media_num'] + CLUBES[str(ZAG[i]['clube'])]['casa'] + (CLUBES[str(ZAG[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(ZAG[i]['clube'])]['pos'] / 10.0))

      if pts >= capitao['pontos']:
        capitao['pontos'] = pts
        capitao['jogador'] = ZAG[i]['apelido']
        capitao['clube'] = CLUBES[str(ZAG[i]['clube'])]['nome']
        capitao['pos'] = 'ZAG'

  for i in range(len(MEI)):
    if MEI_b[i].solution_value() > 0:
      print('│ MEI │ %-20s │ %-15s │ %5.2f │' % (MEI[i]['apelido'], CLUBES[str(MEI[i]['clube'])]['nome'], MEI[i]['preco_num']))
      
      esquema['meia'] += 1
      custoEscalacao += MEI[i]['preco_num']
      pts = MEI[i]['media_num'] + CLUBES[str(MEI[i]['clube'])]['casa'] + (CLUBES[str(MEI[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(MEI[i]['clube'])]['pos'] / 10.0))

      if pts >= capitao['pontos']:
        capitao['pontos'] = pts
        capitao['jogador'] = MEI[i]['apelido']
        capitao['clube'] = CLUBES[str(MEI[i]['clube'])]['nome']
        capitao['pos'] = 'MEI'
  
  for i in range(len(ATA)):
    if ATA_b[i].solution_value() > 0:
      print('│ ATA │ %-20s │ %-15s │ %5.2f │' % (ATA[i]['apelido'], CLUBES[str(ATA[i]['clube'])]['nome'], ATA[i]['preco_num']))
      
      esquema['ataque'] += 1
      custoEscalacao += ATA[i]['preco_num']
      pts = ATA[i]['media_num'] + CLUBES[str(ATA[i]['clube'])]['casa'] + (CLUBES[str(ATA[i]['clube'])]['pts'] / ptsTotal) + (2.0 - (CLUBES[str(ATA[i]['clube'])]['pos'] / 10.0))

      if pts >= capitao['pontos']:
        capitao['pontos'] = pts
        capitao['jogador'] = ATA[i]['apelido']
        capitao['clube'] = CLUBES[str(ATA[i]['clube'])]['nome']
        capitao['pos'] = 'ATA'
  
  for i in range(len(TEC)):
    if TEC_b[i].solution_value() > 0:
      print('│ TEC │ %-20s │ %-15s │ %5.2f │' % (TEC[i]['apelido'], CLUBES[str(TEC[i]['clube'])]['nome'], TEC[i]['preco_num']))
      
      custoEscalacao += TEC[i]['preco_num']

  print('└─────┴──────────────────────┴─────────────────┴───────┘')

  print('Esquema: {}-{}-{}'.format(esquema['defesa'], esquema['meia'], esquema['ataque']))
  print('Preço total: %.2f' % custoEscalacao)
  print('Capitão: %s %s (%s)' % (capitao['pos'], capitao['jogador'], capitao['clube']))

def main():
  if mercadoAberto():
    # Recebe dados do mercado
    atletas, clubes, partidas, classificacao = getMercado()

    # Ler a quantidade de cartoletas disponíveis
    cartoletas = float(input('Digite a quantidade de cartoletas disponíveis: '))

    GOL = []
    LAT = []
    ZAG = []
    MEI = []
    ATA = []
    TEC = []
    CLUBES = {}
    ptsTotal = 0

    # Ler dados dos clubes
    for item in clubes:
      C = {
        'nome': clubes[item]['nome'],
        'abreviacao': clubes[item]['abreviacao'],
        'pos': 0,
        'pts': 0,
        'casa': 0
      }
      
      CLUBES[item] = C
    
    # Ler dados das partidas
    for item in partidas:
      CLUBES[str(item['clube_casa_id'])]['casa'] = 1

    # Ler dados da classificação
    for item in classificacao:
      CLUBES[str(item['clube'])]['pos'] = int(item['pos'])
      CLUBES[str(item['clube'])]['pts'] = int(item['pts'])
      ptsTotal += int(item['pts'])

    if ptsTotal == 0:
      ptsTotal = 1
    
    # Ler dados dos jogadores
    for item in atletas:
      J = {
        'id'        : item['atleta_id'],
        'apelido'   : item['apelido'],
        'status_id' : int(item['status_id']),
        'pontos_num': float(item['pontos_num']),
        'preco_num' : float(item['preco_num']),
        'media_num' : float(item['media_num']),
        'posicao_id': int(item['posicao_id']),
        'clube'     : int(item['clube_id'])
      }

      # Seleciona jogadores com status Provável
      if int(J['status_id']) == 7:
        if int(J['posicao_id']) == gol_id:
          GOL.append(J)
        elif int(J['posicao_id']) == lat_id:
          LAT.append(J)
        elif int(J['posicao_id']) == zag_id:
          ZAG.append(J)
        elif int(J['posicao_id']) == mei_id:
          MEI.append(J)
        elif int(J['posicao_id']) == ata_id:
          ATA.append(J)
        elif int(J['posicao_id']) == tec_id:
          TEC.append(J)

    solver(CLUBES, GOL, LAT, ZAG, MEI, ATA, TEC, cartoletas, ptsTotal)
  else:
    print('O mercado não está disponível no momento!')

if __name__ == '__main__':
  main()