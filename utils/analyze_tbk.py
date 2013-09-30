#!/usr/local/bin/python3

import argparse
import math
import os

# Commission rate.  For IB, each contract costs 1 dollar in commission,
# while the cost of the contract ranges in about 50 to 100 dollars.
C_RATE = 0.015
# Premium price as a rate to investment.
# On 2013-09-25, the call option for IM (51 days with strike price near trading
# price) is 0.9 while the stock price is 22.5.
P_RATE = 0.04

# For call:
# Gain ~= (max(0, gain) - P_RATE) / P_RATE - k*C_RATE
# For put:
# Gain ~= (max(0, -gain) - P_RATE) / P_RATE - k*C_RATE
# k = 1 if max(0, x) = 0 (no need to close position), k = 2 otherwise.

def read_gain_map(gain_file):
  gain_map = dict()
  with open(gain_file, 'r') as fp:
    lines = fp.read().splitlines()
  for line in lines:
    date, ticker, gain = line.split(' ')
    if date not in gain_map:
      gain_map[date] = dict()
    gain_map[date][ticker] = float(gain)
  return gain_map

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--score_dir', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--gain_file', required=True)
  parser.add_argument('--tbk', required=True)
  args = parser.parse_args()

  assert args.tbk.startswith('t') or args.tbk.startswith('b')
  k = int(args.tbk[1:])

  score_files = os.listdir(args.score_dir)
  dates = sorted([sf[:sf.find('.')] for sf in score_files
                  if sf.endswith('.txt')])
  gain_map = read_gain_map(args.gain_file)

  with open(args.ticker_file, 'r') as fp:
    tickers = set(fp.read().splitlines())

  top = args.tbk.startswith('t')
  good_count, bad_count, unknown_count, date_count = 0, 0, 0, 0
  goods = []
  profits = []
  total_good, total_bad = 0, 0
  first_date, last_date = None, None
  for date in dates:
    if date not in gain_map:
      print('Gains are not verifiable for date %s' % date)
      continue
    if first_date is None:
      first_date = date
    gmd = gain_map[date]
    with open('%s/%s.txt' % (args.score_dir, date), 'r') as fp:
      tmp_lines = fp.read().splitlines()
    lines = []
    for line in tmp_lines:
      ticker, score = line.split(' ')
      if ticker in tickers:
        lines.append(line)
    assert len(lines) >= k
    for line in lines:
      ticker, score = line.split(' ')
      if ticker not in gmd:
        continue
      gain = gmd[ticker]
      if (top and gain > 0) or (not top and gain < 0):
        total_good += 1
      else:
        total_bad += 1
    if top:
      lines = lines[:k]
    else:
      lines = lines[-k:]
    good, bad, unknown = [], [], []
    profit = 0.0
    for line in lines:
      ticker, score = line.split(' ')
      if ticker not in gmd:
        unknown.append(0)
        continue
      gain = gmd[ticker]
      if (top and gain > 0) or (not top and gain < 0):
        good.append(gain)
        profit += (abs(gain) - P_RATE) / P_RATE - 2 * C_RATE
      else:
        bad.append(gain)
        profit += -1 - C_RATE
    goods.extend(good)
    profit /= (len(good) + len(bad))
    profits.append(profit)
    good_count += len(good)
    bad_count += len(bad)
    unknown_count += len(unknown)
    date_count += 1
    print('Processed %d tickers for date %s' % (k, date))
    print('\tGood: %d\t\tBad: %d\t\tUnknown: %d'
          % (len(good), len(bad), len(unknown)))
    print('\tProfit: %.2f%%' % (profit*100))
    print('Good: %s' % good)
    print('Bad: %s' % bad)
    print('==================================================')
    last_date = date
#  total_count = good_count + bad_count + unknown_count
  total_count = good_count + bad_count
  print('Summary for %d dates' % date_count)
  print('Good: %d/%d - %.2f%%'
        % (good_count, total_count, good_count*100.0/total_count))
  print('Bad: %d/%d - %.2f%%'
        % (bad_count, total_count, bad_count*100.0/total_count))
#  print('Unknown: %d/%d - %.2f%%'
#        % (unknown_count, total_count, unknown_count*100.0/total_count))
  mp = sum(profits)/len(profits)
  stdp = 0.0
  for p in profits:
    stdp += (p - mp) * (p - mp)
  stdp /= len(profits)
  stdp = math.sqrt(stdp)
  print('Total profit: %.2f%% with median %.2f%% and std %.2f%%, sharpe ~= %.2f'
        % (mp*100, sorted(profits)[int(len(profits)/2)]*100, stdp*100,
           mp/stdp))
  print('Total good vs bad: %d vs %d (%.2f%% vs %.2f%%)'
        % (total_good, total_bad, total_good*100.0/(total_good+total_bad),
           total_bad*100.0/(total_good+total_bad)))
  goods.sort(reverse=top)
  print('%d goods: %s' % (len(goods), goods))
  for r in [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]:
    print('%.2f%% position: %.2f%% gain'
          % (r*100, goods[int(len(goods)*r)]*100))
  print('Mean gain of all goods: %.2f%%' % (sum(goods)/len(goods)*100))

if __name__ == '__main__':
  main()

