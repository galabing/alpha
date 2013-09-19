#!/usr/local/bin/python3

""" Makes a histogram by averaging the gain of top/bottom k stocks at each
    date tested.
"""

import argparse
import os

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

def mean(vals):
  return sum(vals)/len(vals)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--score_dir', required=True)
  parser.add_argument('--gain_file', required=True)
  # Eg, t30 for top 30, b15 for bottom 15.
  parser.add_argument('--tbk', required=True)
  parser.add_argument('--histogram_file', required=True)
  args = parser.parse_args()

  assert args.tbk.startswith('t') or args.tbk.startswith('b')
  k = int(args.tbk[1:])
  if args.tbk.startswith('b'):
    k *= -1
  gain_map = read_gain_map(args.gain_file)

  score_files = os.listdir(args.score_dir)
  dates = [sf[:sf.find('.')] for sf in score_files if sf.endswith('.txt')]
  dates.sort()

  ofp = open(args.histogram_file, 'w')
  ts, tg, count = 0.0, 0.0, 0
  for date in dates:
    print('Processing %s' % date)
    if date not in gain_map:
      print('!! Gains for %s is not verifiable' % date)
      continue
    with open('%s/%s.txt' % (args.score_dir, date), 'r') as fp:
      lines = fp.read().splitlines()
    print('\t%d scores' % len(lines))
    gains = []
    for line in lines:
      ticker, score = line.split(' ')
      if ticker in gain_map[date]:
        gains.append(gain_map[date][ticker])
    print('\t%d verifiable scores' % len(gains))
    if k > 0:
      segment = gains[:k]
    else:
      segment = gains[k:]
    assert len(segment) == abs(k)
    ms = mean(segment)*100
    mg = mean(gains)*100
    ts += ms
    tg += mg
    count += 1
    print('%s,%.2f,%.2f' % (date, ms, mg), file=ofp)
  print('Avg,%.2f,%.2f' % (ts/count, tg/count), file=ofp)
  ofp.close()

if __name__ == '__main__':
  main()

