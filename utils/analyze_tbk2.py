#!/usr/local/bin/python3

import argparse
import datetime
import math
import os

# Commission rate.  For IB, each contract costs 1 dollar in commission,
# while the cost of the contract ranges in about 50 to 100 dollars.
C_RATE = 0.015
# Premium price as a rate to investment.
# On 2013-09-25, the call option for IM (51 days with strike price near trading
# price) is 0.9 while the stock price is 22.5.
# UPDATE: it's more like 0.06@10 from real data.
P_RATE = 0.05 #0.06

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

def get_ddate(date, open_dates, delay):
  for i in range(len(open_dates)):
    if open_dates[i] >= date:
      if i + delay < len(open_dates):
        return open_dates[i+delay]
  return None

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--score_dir', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--gain_file', required=True)
  parser.add_argument('--od_file', required=True)
  parser.add_argument('--delay', default='0')
  parser.add_argument('--tbk', required=True)
  args = parser.parse_args()

  lookahead = int(args.gain_file[args.gain_file.rfind('_')+1:args.gain_file.rfind('.')])
  delay = int(args.delay)
  assert delay >= 0
  print('Looking ahead %d days with %d days delay' % (lookahead, delay))
  print('Label is %s' % args.tbk)
  weeks = int(lookahead/7)
  if lookahead % 7 > 0:
    weeks += 1

  with open(args.od_file, 'r') as fp:
    open_dates = sorted(fp.read().splitlines())

  assert args.tbk.startswith('t') or args.tbk.startswith('b')
  if args.tbk[1:].find('-') < 0:
    j = 0
    k = int(args.tbk[1:])
  else:
    j, k = args.tbk[1:].split('-')
    j, k = int(j), int(k)
    assert j <= k

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
  for date in dates:
    ddate = get_ddate(date, open_dates, delay)
    if ddate not in gain_map:
      print('Gains are not verifiable for date %s' % ddate)
      continue
    gmd = gain_map[ddate]
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
      lines = lines[j:k]
    else:
      lines = lines[-k:len(lines)-j]
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
    print('Processed %d tickers for date %s and ddate %s' % (k, date, ddate))
    print('\tGood: %d\t\tBad: %d\t\tUnknown: %d'
          % (len(good), len(bad), len(unknown)))
    print('\tProfit: %.2f%%' % (profit*100))
    print('Good: %s' % good)
    print('Bad: %s' % bad)
    print('==================================================')
  total_count = good_count + bad_count
  print('Summary for %d dates' % date_count)
  print('Good: %d/%d - %.2f%%'
        % (good_count, total_count, good_count*100.0/total_count))
  print('Bad: %d/%d - %.2f%%'
        % (bad_count, total_count, bad_count*100.0/total_count))
  print('Unsorted profits: %s' % ', '.join(['%.2f%%' % (p*100) for p in profits]))
  print('Sorted profits: %s' % ', '.join([('%.2f%%' % p) for p in sorted([p*100 for p in profits], reverse=True)]))
  mp = sum(profits)/len(profits)
  stdp = 0.0
  for p in profits:
    stdp += (p - mp) * (p - mp)
  stdp /= len(profits)
  stdp = math.sqrt(stdp)
  print('Total profit: %.2f%% with median %.2f%% and std %.2f%%, sharpe ~= %.2f'
        % (mp*100, sorted(profits)[int(len(profits)/2)]*100, stdp*100,
           mp/stdp))
  print('Total profit per week: %.2f%%' % (mp*100/weeks))
  print('Total good vs bad: %d vs %d (%.2f%% vs %.2f%%)'
        % (total_good, total_bad, total_good*100.0/(total_good+total_bad),
           total_bad*100.0/(total_good+total_bad)))
  goods.sort(reverse=top)
  #print('%d goods: %s' % (len(goods), goods))
  for r in [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]:
    print('%.2f%% position: %.2f%% gain'
          % (r*100, goods[int(len(goods)*r)]*100))
  print('Mean gain of all goods: %.2f%%' % (sum(goods)/len(goods)*100))

if __name__ == '__main__':
  main()

