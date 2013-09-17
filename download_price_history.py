#!/usr/local/bin/python3

""" Downloads csv files of historical stock prices from yahoo finance.
"""

import argparse
import os

WGET = '/usr/local/bin/wget'

def download(ticker, output_path):
  # Eg, BF.B becomes BF-B on yahoo.
  yahoo_ticker = ticker.replace('.', '-')
  url = 'http://ichart.finance.yahoo.com/table.csv?s=%s' % yahoo_ticker
  cmd = '%s -q "%s" -O %s' % (WGET, url, output_path)
  if os.system(cmd) != 0:
    print('Download failed for %s: %s' % (ticker, url))
    if os.path.isfile(output_path):
      os.remove(output_path)
    return False
  return True

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--output_dir', required=True)
  parser.add_argument('--overwrite', action='store_true')
  args = parser.parse_args()

  # Tickers are listed one per line.
  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()
  print('Processing %d tickers' % len(tickers))

  count = 0
  failures = []
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('%d/%d: %s' % (i+1, len(tickers), ticker))

    # NOTE: This won't work with the S&P500 ticker (starting with ^).
    output_path = '%s/%s.csv' % (args.output_dir, ticker)
    if os.path.isfile(output_path) and not args.overwrite:
      print('Output file already exists and not overwritable: %s' % output_path)
      continue

    count += 1
    if os.path.isfile(output_path):
      os.remove(output_path)
    if not download(ticker, output_path):
      failures.append(ticker)

  print('Processed %d tickers, %d for downloading' % (len(tickers), count))
  print('Encountered %d failures, tickers: %s' % (len(failures), failures))

if __name__ == '__main__':
  main()

