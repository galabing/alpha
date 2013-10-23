#!/usr/local/bin/python3

import argparse
import csv
import os

#EXPECTED_GAIN_CALL = 0.1
#EXPECTED_GAIN_PUT = -0.1

EG_CALL_MAP = {
  30: 0.1282,
}
EG_PUT_MAP = {
  30: -0.1369,
}
MAX_ASK = 2
MIN_EXP = 90
TGT_EXP = 110
MAX_EXP = 180
K = 10

# HACK
def get_expected_gain(tbrank, call):
  assert tbrank >= 1 and tbrank <= 30
  if call:
    for k in sorted(EG_CALL_MAP.keys()):
      if tbrank <= k:
        return EG_CALL_MAP[k]
  else:
    for k in sorted(EG_PUT_MAP.keys()):
      if tbrank <= k:
        return EG_PUT_MAP[k]
  assert False

def compute_num_contracts(ask):
  num_contracts = 1
  while (ask*num_contracts*100 < MIN_EXP
         and ask*(num_contracts+1)*100 <= TGT_EXP):
    num_contracts += 1
  if ask*num_contracts*100 > MAX_EXP:
    return 0
  return num_contracts

def compute_profit(ask, num_contracts, low, high):
  option_commission = max(1.0, num_contracts*0.7)
  stock_commission = max(1.0, num_contracts*100*0.005) * 2
  buy = ask * num_contracts * 100
  cost = option_commission + stock_commission + buy
  assert high > low
  exe = (high - low) * num_contracts * 100
  profit = exe - cost
  if cost == 0:
    gain = 0
  else:
    gain = profit/cost
  return cost, profit, gain

def process(
    tbrank, ticker, stock_price, call, date_prefix, expected_gain, data,
    corrections):
  date_prefixes = date_prefix.split(',')
  symbol, last_sale, net, bid, ask, vol, open_interest = data
  found = False
  for dp in date_prefixes:
    if symbol.startswith('%s ' % dp):
      date_prefix = dp
      found = True
      break
  if not found:
    return None
  if ask < 0.001:
    return None
  fp = symbol[symbol.find('(')+1:symbol.rfind(')')]
  assert fp.startswith(ticker)
  strike_price = float(symbol[len(date_prefix)+1:symbol.find('(')])
  assert stock_price > 0
  # Currently we are interested in stock price 0-20.
  # This may change in the future.
  assert stock_price < 30
  # Sanity checks.
  assert strike_price > 0
  assert strike_price < stock_price * 10
  # Possible fix by corrections.
  if call:
    cp = 'call'
  else:
    cp = 'put'
  key = '%s-%s-%.2f' % (ticker, cp, strike_price)
  if key in corrections:
    print('Replacing asking price for %s from %.2f to %.2f'
          % (key, ask, corrections[key]))
    ask = corrections[key]
  if ask < 0.001 or ask > MAX_ASK:
    return None
  num_contracts = compute_num_contracts(ask)

  if expected_gain is None:
    expected_gain = get_expected_gain(tbrank, call)
  expected_price = stock_price * (1 + expected_gain)
  if call and expected_price <= strike_price:
    return None
  if not call and expected_price >= strike_price:
    return None
  if call:
    low = strike_price
    high = expected_price
  else:
    low = expected_price
    high = strike_price
  cost, profit, gain = compute_profit(ask, num_contracts, low, high)
  return [tbrank, ticker, fp, stock_price, expected_price, strike_price, ask,
          num_contracts, cost, profit, date_prefix, gain]

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--oprice_dir', required=True)
  # Eg, '13 Nov'.
  parser.add_argument('--date_prefix', required=True)
  # Must be 'call' or 'put'.
  parser.add_argument('--type', required=True)
  parser.add_argument('--correction_file')
  parser.add_argument('--expected_gain')
  args = parser.parse_args()

  assert args.type == 'call' or args.type == 'put'
  call = (args.type == 'call')

  if args.expected_gain is not None:
    #expected_gain = float(args.expected_gain)
    # Can't take --expected_gain when there is a hack.
    assert False
  # Sanity checks.
  #if call:
  #  assert expected_gain > 0
  #  assert expected_gain < 1
  #else:
  #  assert expected_gain < 0
  #  assert expected_gain > -1

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  corrections = dict()
  if args.correction_file is not None:
    with open(args.correction_file, 'r') as fp:
      lines = fp.read().splitlines()
    for line in lines:
      ticker, cp, strike, ask = line.split(' ')
      assert cp == 'call' or cp == 'put'
      strike, ask = float(strike), float(ask)
      corrections['%s-%s-%.2f' % (ticker, cp, strike)] = ask
  print('Using %d corrections' % len(corrections))

  all_info = []
  num_added = 0
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('Processing ticker %s' % ticker)
    oprice_file = '%s/%s.csv' % (args.oprice_dir, ticker)
    if not os.path.isfile(oprice_file):
      print('!!! Option price not available for %s' % ticker)
      continue

    with open(oprice_file, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) >= 3
    assert lines[2] == (
        'Calls,Last Sale,Net,Bid,Ask,Vol,Open Int,'
        'Puts,Last Sale,Net,Bid,Ask,Vol,Open Int,')

    row_index = 0
    stock_price = None
    added = False
    for row in csv.reader(lines, delimiter=','):
      if row_index == 0:
        assert len(row) == 4
        assert row[0].startswith('%s ' % ticker)
        assert row[3] == ''
        stock_price = float(row[1])
        row_index += 1
        continue
      if row_index < 3:
        row_index += 1
        continue
      assert stock_price is not None
      cs, cls, cn, cb, ca, cv, coi, ps, pls, pn, pb, pa, pv, poi, tmp = row
      assert tmp == ''
      if call:
        try:
          data = [cs, float(cls), float(cn), float(cb), float(ca),
                  int(cv), int(coi)]
        except ValueError:
          print('Dropping bad data point: %s' % row)
          data = None
      else:
        try:
          data = [ps, float(pls), float(pn), float(pb), float(pa),
                  int(pv), int(poi)]
        except ValueError:
          print('Dropping bad data point: %s' % row)
          data = None
      if data is None:
        continue
      info = process(
          i+1, ticker, stock_price, call, args.date_prefix, None, data,
          corrections)
      if info is not None:
        all_info.append(info)
        added = True
      row_index += 1
    if not added:
      print('!!! Could not add one data point for ticker %s' % ticker)
    else:
      num_added += 1
  #print(all_info)
  print('Added %d tickers' % num_added)

  all_info.sort(key=lambda info: info[-1], reverse=True)
  showed_tickers = set()
  k_cost, k_profit = 0, 0
  rates = []
  for i in range(len(all_info)):
    (rank, ticker, fp, stock_price, expected_price, strike_price, ask,
     num_contracts, cost, profit, date_prefix, gain) = all_info[i]
    if ticker in showed_tickers:
      continue
    showed_tickers.add(ticker)
    if len(showed_tickers) <= K:
      k_cost += cost
      k_profit += profit
    if call:
      rank = 't%d' % rank
    else:
      rank = 'b%d' % rank

    delta = stock_price - strike_price
    if call:
      atask = ask - delta
    else:
      atask = ask + delta
    assert atask > 0
    rates.append(atask/stock_price)

    print('Rank %d (%d), %s: %s (%s), %s; gain = %.2f%%'
          % (len(showed_tickers), i+1, rank, ticker, fp, date_prefix, gain*100))
    print('  Stock price: current = %.2f, expected = %.2f'
          % (stock_price, expected_price))
    print('  Buy: strike = %.2f, ask = %.2f' % (strike_price, ask))
    print('  Trans: contracts = %d, cost = %.2f, profit = %.2f'
          % (num_contracts, cost, profit))
    print()
  print('Processed %d tickers' % len(showed_tickers))
  print('At %d: cost = %.2f, profit = %.2f' % (K, k_cost, k_profit))
  print('Rates: %s - avg = %f, avg@10 = %f' % (rates, sum(rates)/len(rates), sum(rates[:10])/10))

if __name__ == '__main__':
  main()

