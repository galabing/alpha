#!/usr/local/bin/python3

""" Extracts market cap from ticker homepages.
    Each output line will consist of:
        <ticker>|<cap>|<class>
"""

import argparse
import os
from bs4 import BeautifulSoup

DELIMITER = '|'
DIV_HEADER = 'yfi_quote_summary_data'
CAP_HEADER = 'Market Cap:'
THOUSAND = 1000.0
MILLION = 1000 * THOUSAND
BILLION = 1000 * MILLION
UNIT_MAP = {
  'K': THOUSAND,
  'M': MILLION,
  'B': BILLION,
}
CAPS = [
#  (200 * BILLION, 'mega'),
  (10 * BILLION, 'large'),
  (2 * BILLION, 'mid'),
  (250 * MILLION, 'small'),
#  (50 * MILLION, 'micro'),
#  (0, 'nano'),
  (0, 'micro'),
]

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
  parser.add_argument('--homepage_dir', required=True)
  parser.add_argument('--cap_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  cls_map = dict()
  output_lines = []
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('%d/%d: %s' % (i+1, len(tickers), ticker))
    homepage_file = '%s/%s.html' % (args.homepage_dir, ticker)
    if not os.path.isfile(homepage_file):
      print('Homepage does not exist for %s' % ticker)
      continue
    with open(homepage_file, 'r') as fp:
      content = fp.read()
    soup = BeautifulSoup(content)
    sd = soup.find_all(id=DIV_HEADER)
    if len(sd) == 0:
      print('Invalid homepage for %s' % ticker)
      continue
    assert len(sd) == 1
    text = sd[0].get_text(DELIMITER)
    items = text.split(DELIMITER)
    hi = items.index(CAP_HEADER)
    cap = items[hi+1]
    if cap == 'N/A':
      print('N/A market cap for %s' % ticker)
      continue
    unit = cap[-1]
    assert unit in UNIT_MAP
    cap = float(cap[:-1]) * UNIT_MAP[cap[-1]]
    cls = get_class(cap)
    output_lines.append('%s%s%f%s%s' % (ticker, DELIMITER, cap, DELIMITER, cls))
    update_map(cls_map, cls)

  print(cls_map)

  with open(args.cap_file, 'w') as fp:
    for line in output_lines:
      print(line, file=fp)

if __name__ == '__main__':
  main()

