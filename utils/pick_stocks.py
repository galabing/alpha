#!/usr/local/bin/python3

import argparse

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--score_file', required=True)
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--tbk', required=True)
  parser.add_argument('--print_scores', action='store_true')
  args = parser.parse_args()

  assert args.tbk.startswith('t') or args.tbk.startswith('b')
  k = int(args.tbk[1:])
  assert k > 0

  with open(args.ticker_file, 'r') as fp:
    tickers = set(fp.read().splitlines())

  with open(args.score_file, 'r') as fp:
    lines = fp.read().splitlines()
  ts_list = []
  for line in lines:
    ticker, score = line.split(' ')
    if ticker not in tickers:
      continue
    ts_list.append((ticker, score))
  assert k <= len(ts_list)

  if args.tbk.startswith('t'):
    r = range(k)
  else:
    r = range(len(ts_list)-1, len(ts_list)-k-1, -1)
  for i in r:
    if args.print_scores:
      print('%s: %s' % (ts_list[i][0], ts_list[i][1]))
    else:
      print('%s' % ts_list[i][0])

if __name__ == '__main__':
  main()

