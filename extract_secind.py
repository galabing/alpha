#!/usr/local/bin/python3

""" Extracts sector and industry info from ticker homepages.
    Each output line will consist of:
        <ticker>|<sector>|<industry>
"""

import argparse
import os
from bs4 import BeautifulSoup

DELIMITER = '|'

def update_map(m, v):
  if v in m:
    m[v] += 1
  else:
    m[v] = 1

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--homepage_dir', required=True)
  parser.add_argument('--secind_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  smap, imap, simap = dict(), dict(), dict()
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
    cd = soup.find_all(id='company_details')
    if len(cd) == 0:
      print('Invalid homepage for %s' % ticker)
      continue
    assert len(cd) == 1
    secind = cd[0].get_text(DELIMITER)
    sh, sc, ih, ic = secind.split(DELIMITER)
    assert sh == 'Sector'
    assert ih == 'Industry'
    output_lines.append(DELIMITER.join([ticker, sc, ic]))
    update_map(smap, sc)
    update_map(imap, ic)
    update_map(simap, '%s%s%s' % (sc, DELIMITER, ic))

  print(len(smap))
  print(len(imap))
  print(len(simap))

  with open(args.secind_file, 'w') as fp:
    for line in output_lines:
      print(line, file=fp)

if __name__ == '__main__':
  main()

