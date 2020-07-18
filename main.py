from __future__ import print_function
from ortools.linear_solver import pywraplp
import json

def main():
  jogadores     = json.load(open('data/2019/br2019_01.json'))
  jogadores_pos = json.load(open('data/2019/br2019_02.json'))
  classificacao = json.load(open('data/2019/classificacao_01.json'))
  rodada        = json.load(open('data/2019/jogos_01.json'))

  G = []
  L = []
  Z = []
  M = []
  A = []
  T = []
  JOG = {}
  CL = {}
  ptsTotal = 0

  # Cartoletas disponíveis
  C = 114.6

  # Ler dados de classificação
  for item in classificacao:
    time = {
      'pos' : None,
      'pts' : None,
      'casa': None
    }
    
    time['pos'] = int(item['pos'])
    time['pts'] = int(item['pts'])
    clube = item['clube']
    ptsTotal += time['pts']

    CL[clube] = time

  if ptsTotal == 0:
    ptsTotal = 1

  # Ler dados de jogos
  for item in rodada:
    clube = item['clube']

    CL[clube]['casa'] = int(item['casa'])
  
  # Ler dados de jogadores
  for item in jogadores:
    J = {
      'apelido'   : None,
      'status_id' : None,
      'pontos_num': None,
      'preco_num' : None,
      'media_num' : None,
      'posicao_id': None,
      'clube'     : None,
      'id'        : None
    }
    
    J['apelido']    = item['apelido']
    J['status_id']  = int(item['status_id'])
    J['pontos_num'] = float(item['pontos_num'])
    J['preco_num']  = float(item['preco_num'])
    J['media_num']  = float(item['media_num'])
    J['posicao_id'] = int(item['posicao_id'])
    J['clube']      = item['clube']
    J['id']         = item['atleta_id']

    if int(J['status_id']) == 7:
      if int(J['posicao_id']) == 1:
        G.append(J)
      elif int(J['posicao_id']) == 2:
        L.append(J)
      elif int(J['posicao_id']) == 3:
        Z.append(J)
      elif int(J['posicao_id']) == 4:
        M.append(J)
      elif int(J['posicao_id']) == 5:
        A.append(J)
      elif int(J['posicao_id']) == 6:
        T.append(J)
  
  # Ler dados de pontuação e vaiação
  for item in jogadores_pos:
    J = {
      'pontos_num'  : None,
      'variacao_num': None
    }
    
    J['pontos_num']    = float(item['pontos_num'])
    J['variacao_num']  = float(item['variacao_num'])

    JOG[item['atleta_id']] = J

  # Cria solver
  solver = pywraplp.Solver('simple_lp_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

  Gb = {}
  Lb = {}
  Zb = {}
  Mb = {}
  Ab = {}
  Tb = {}

  # Variáveis binárias para goleiros
  for i in range(len(G)):
    Gb[i] = solver.BoolVar('Gb[{}]'.format(i))

  # Variáveis binárias para laterais
  for i in range(len(L)):
    Lb[i] = solver.BoolVar('Lb[{}]'.format(i))

  # Variáveis binárias para zagueiros
  for i in range(len(Z)):
    Zb[i] = solver.BoolVar('Zb[{}]'.format(i))

  # Variáveis binárias para meias
  for i in range(len(M)):
    Mb[i] = solver.BoolVar('Mb[{}]'.format(i))

  # Variáveis binárias para atacantes
  for i in range(len(A)):
    Ab[i] = solver.BoolVar('Ab[{}]'.format(i))

  # Variáveis binárias para técnicos
  for i in range(len(T)):
    Tb[i] = solver.BoolVar('Tb[{}]'.format(i))

  # Variável binária para definir se o time possui laterais
  z = solver.BoolVar('z')

  # Restrições de quantidade de jogadores por posição
  solver.Add(solver.Sum(Gb[i] for i in range(len(Gb))) == 1)
  solver.Add(solver.Sum(Lb[i] for i in range(len(Lb))) == 2 * z)
  solver.Add(solver.Sum(Zb[i] for i in range(len(Zb))) >= 2)
  solver.Add(solver.Sum(Zb[i] for i in range(len(Zb))) <= 3)
  solver.Add(solver.Sum(Mb[i] for i in range(len(Mb))) >= 3)
  solver.Add(solver.Sum(Mb[i] for i in range(len(Mb))) <= 5)
  solver.Add(solver.Sum(Ab[i] for i in range(len(Ab))) >= 1)
  solver.Add(solver.Sum(Ab[i] for i in range(len(Ab))) <= 3)
  solver.Add(solver.Sum(Tb[i] for i in range(len(Tb))) == 1)

  # Restrição para a defesar ter pelo menos 3 jogadores
  solver.Add(
    solver.Sum(Lb[i] for i in range(len(Lb))) +
    solver.Sum(Zb[i] for i in range(len(Zb))) >= 3
  )

  # Restrição para definir o time com 12 membros
  solver.Add(
    solver.Sum(Gb[i] for i in range(len(Gb))) +
    solver.Sum(Lb[i] for i in range(len(Lb))) +
    solver.Sum(Zb[i] for i in range(len(Zb))) +
    solver.Sum(Mb[i] for i in range(len(Mb))) +
    solver.Sum(Ab[i] for i in range(len(Ab))) +
    solver.Sum(Tb[i] for i in range(len(Tb))) == 12)

  # Restrição para limitar o preço do time
  solver.Add(
    solver.Sum(G[i]['preco_num'] * Gb[i] for i in range(len(Gb))) +
    solver.Sum(L[i]['preco_num'] * Lb[i] for i in range(len(Lb))) +
    solver.Sum(Z[i]['preco_num'] * Zb[i] for i in range(len(Zb))) +
    solver.Sum(M[i]['preco_num'] * Mb[i] for i in range(len(Mb))) +
    solver.Sum(A[i]['preco_num'] * Ab[i] for i in range(len(Ab))) +
    solver.Sum(T[i]['preco_num'] * Tb[i] for i in range(len(Tb))) <= C)

  # Função objetivo
  solver.Maximize(
    solver.Sum((G[i]['media_num'] + (CL[G[i]['clube']]['casa']) + (CL[G[i]['clube']]['pts'] / ptsTotal) + (2.0 - (CL[G[i]['clube']]['pos']/10.0))) * Gb[i] for i in range(len(Gb))) +
    solver.Sum((L[i]['media_num'] + (CL[L[i]['clube']]['casa']) + (CL[L[i]['clube']]['pts'] / ptsTotal) + (2.0 - (CL[L[i]['clube']]['pos']/10.0))) * Lb[i] for i in range(len(Lb))) +
    solver.Sum((Z[i]['media_num'] + (CL[Z[i]['clube']]['casa']) + (CL[Z[i]['clube']]['pts'] / ptsTotal) + (2.0 - (CL[Z[i]['clube']]['pos']/10.0))) * Zb[i] for i in range(len(Zb))) +
    solver.Sum((M[i]['media_num'] + (CL[M[i]['clube']]['casa']) + (CL[M[i]['clube']]['pts'] / ptsTotal) + (2.0 - (CL[M[i]['clube']]['pos']/10.0))) * Mb[i] for i in range(len(Mb))) +
    solver.Sum((A[i]['media_num'] + (CL[A[i]['clube']]['casa']) + (CL[A[i]['clube']]['pts'] / ptsTotal) + (2.0 - (CL[A[i]['clube']]['pos']/10.0))) * Ab[i] for i in range(len(Ab))) +
    solver.Sum((T[i]['media_num'] + (CL[T[i]['clube']]['casa']) + (CL[T[i]['clube']]['pts'] / ptsTotal) + (2.0 - (CL[T[i]['clube']]['pos']/10.0))) * Tb[i] for i in range(len(Tb)))
  )

  # Solver
  sol = solver.Solve()

  print('Solução:')
  print('Valor da função objetivo = %.2f' % solver.Objective().Value())
  print('Tempo = ', solver.WallTime(), ' ms')
  
  cont_def = 0
  cont_mei = 0
  cont_ata = 0
  preco_total = 0
  variacao = 0
  pontuacao = 0

  print('┌─────┬──────────────────────┬─────────────────┬───────┐')
  print('│\033[1m POS \033[0m│\033[1m %-20s \033[0m│\033[1m %-15s \033[0m│ \033[1m%s \033[0m│' % ('JOGADOR', 'TIME', 'PREÇO'))
  print('├─────┼──────────────────────┼─────────────────┼───────┤')

  for i in range(len(G)):
    if Gb[i].solution_value() > 0:
      print('│ GOL │ %-20s │ %-15s │ %5.2f │' % (G[i]['apelido'], G[i]['clube'], G[i]['preco_num']))
      preco_total += G[i]['preco_num']
      pontuacao += JOG[G[i]['id']]['pontos_num']
      variacao += JOG[G[i]['id']]['variacao_num']

  for i in range(len(L)):
    if Lb[i].solution_value() > 0:
      print('│ LAT │ %-20s │ %-15s │ %5.2f │' % (L[i]['apelido'],L[i]['clube'],L[i]['preco_num']))
      cont_def += 1
      preco_total += L[i]['preco_num']
      pontuacao += JOG[L[i]['id']]['pontos_num']
      variacao += JOG[L[i]['id']]['variacao_num']

  for i in range(len(Z)):
    if Zb[i].solution_value() > 0:
      print('│ ZAG │ %-20s │ %-15s │ %5.2f │' % (Z[i]['apelido'],Z[i]['clube'],Z[i]['preco_num']))
      cont_def += 1
      preco_total += Z[i]['preco_num']
      pontuacao += JOG[Z[i]['id']]['pontos_num']
      variacao += JOG[Z[i]['id']]['variacao_num']

  for i in range(len(M)):
    if Mb[i].solution_value() > 0:
      print('│ MEI │ %-20s │ %-15s │ %5.2f │' % (M[i]['apelido'],M[i]['clube'],M[i]['preco_num']))
      cont_mei += 1
      preco_total += M[i]['preco_num']
      pontuacao += JOG[M[i]['id']]['pontos_num']
      variacao += JOG[M[i]['id']]['variacao_num']
  
  for i in range(len(A)):
    if Ab[i].solution_value() > 0:
      print('│ ATA │ %-20s │ %-15s │ %5.2f │' % (A[i]['apelido'],A[i]['clube'],A[i]['preco_num']))
      cont_ata += 1
      preco_total += A[i]['preco_num']
      pontuacao += JOG[A[i]['id']]['pontos_num']
      variacao += JOG[A[i]['id']]['variacao_num']
  
  for i in range(len(T)):
    if Tb[i].solution_value() > 0:
      print('│ TEC │ %-20s │ %-15s │ %5.2f │' % (T[i]['apelido'],T[i]['clube'],T[i]['preco_num']))
      preco_total += T[i]['preco_num']
      pontuacao += JOG[T[i]['id']]['pontos_num']
      variacao += JOG[T[i]['id']]['variacao_num']

  print('└─────┴──────────────────────┴─────────────────┴───────┘')

  print('Esquema: {}-{}-{}'.format(cont_def,cont_mei,cont_ata))
  print('Preço total: %.2f' % preco_total)
  print('Pontuação: %.2f' % pontuacao)
  print('Variação: %.2f' % variacao)

if __name__ == '__main__':
  main()