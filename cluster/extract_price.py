#!/usr/local/bin/python3

""" Extracts current stock prices.
    Each output line will consist of:
        <ticker>|<price>|<class>
"""

import argparse
import os

DELIMITER = '|'
CAPS = [
  (100, '100-inf'),
  (75, '75-100'),
  (50, '50-75'),
  (40, '40-50'),
  (30, '30-40'),
  (25, '25-30'),
  (20, '20-25'),
  (15, '15-20'),
  (10, '10-15'),
  (5, '5-10'),
  (0, '0-5'),
]
MAX_DATE = '2013-10-12'
MIN_DATE = '2013-10-05'

def get_class(v):
  for cap in CAPS:
    thresh, cls = cap
    if v > thresh:
      return cls
  assert False

def update_map(m, cls):
  if cls in m:
    m[cls] += 1
  else:
    m[cls] = 1

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--price_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  cls_map = dict()
  output_lines = []
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('%d/%d: %s' % (i+1, len(tickers), ticker))
    price_file = '%s/%s.csv' % (args.price_dir, ticker)
    if not os.path.isfile(price_file):
      print('Price data does not exist for %s' % ticker)
      continue
    with open(price_file, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
    if len(lines) <= 1:
      print('No price data available for %s' % ticker)
      continue
    d, o, h, l, c, v, a = lines[1].split(',')
    assert d <= MAX_DATE
    if d < MIN_DATE:
      print('No recent price data available for %s' % ticker)
      continue
    price = float(a)
    cls = get_class(price)
    output_lines.append('%s%s%f%s%s'
                        % (ticker, DELIMITER, price, DELIMITER, cls))
    update_map(cls_map, cls)

  print(cls_map)

  with open(args.price_file, 'w') as fp:
    for line in output_lines:
      print(line, file=fp)

if __name__ == '__main__':
  main()

