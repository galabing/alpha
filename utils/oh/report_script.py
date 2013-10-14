#!/usr/local/bin/python3

data_dir = '/Users/linyang/Projects/github/data_alpha/virtual/oh/2013-10-12'
order_file = '%s/orders.csv' % data_dir
order_date = '2013-10-01'
position_file = '%s/positions.csv' % data_dir

def gain1(price, quantity, strike, last, cp):
  cost = price*quantity*100
  diff = last - strike
  if cp == 'Put': diff = -diff
  return [cost, max(0, diff*quantity*100)]

def gain2(price, quantity, bid):
  cost = price*quantity*100
  return [cost, bid*quantity*100]

with open(order_file, 'r') as fp:
  lines = fp.read().splitlines()
assert len(lines) > 0
assert lines[0] == 'Description,Id,Created On,Last Update,Transaction,Order Quantity,Quantity Filled,Price,Type,Duration,Status,Stop Price,Trigger,Trail'

items = []
for line in lines[1:]:
  desc, _, co, _, _, oq, qf, p, _, _, stat, _, _, _ = line.split(',')
  if not co.startswith(order_date):
    continue
  assert stat == 'Filled'
  assert oq == qf
  items.append([desc, int(qf), float(p)])

#print(items)

with open(position_file, 'r') as fp:
  lines = fp.read().splitlines()
assert len(lines) > 0
assert lines[0] == 'Description,Qty,Mark,Market Value,Cost Basis,Gain/Loss,Mark Chg,Value Chg,Stock Last,Bid,Ask'

pos = dict()
for line in lines[1:]:
  desc, q, _, _, _, _, _, _, last, bid, ask = line.split(',')
  assert desc not in pos
  pos[desc] = [int(q), float(last), float(bid), float(ask)]

#print(pos)

tcost, tret = 0, 0
for item in items:
  desc, q, p = item
  assert desc in pos
  q2, last, bid, ask = pos[desc]
  assert q2 >= q

  ticker, month, day, strike, cp = desc.split(' ')
  strike = float(strike)
  assert cp == 'Call' or cp == 'Put'

  c1, r1 = gain1(p, q, strike, last, cp)
  c2, r2 = gain2(p, q, bid)
  assert c1 == c2
  tcost += c1
  tret += max(r1, r2)
  print('%s:\n\t%s\t%s'
        % (desc, gain1(p, q, strike, last, cp), gain2(p, q, bid)))

print('total cost = %.2f, total return = %.2f, gain = %.2f%%'
      % (tcost, tret, (tret - tcost)*100/tcost))

