#!/usr/local/bin/python3

""" Clusters tickers according to certain field, producing several ticker files
    each belonging to one class.

    The input ticker_class_file should have the following format:
        <ticker>|<field1>|<field2>|...
    The tickers will be classed by identical fieldX, where X is specified by
    flag, and multiple ticker files of the same class will be produced to the
    output directory.
"""

import argparse
import os

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_class_file', required=True)
  parser.add_argument('--field_index', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  field_index = int(args.field_index)
  ticker_map = dict()
  with open(args.ticker_class_file, 'r') as fp:
    lines = fp.read().splitlines()
  num_items = -1
  for line in lines:
    items = line.split('|')
    if num_items < 0:
      num_items = len(items)
    assert len(items) == num_items
    ticker = items[0]
    field = items[field_index]
    if field not in ticker_map:
      ticker_map[field] = [ticker]
    else:
      ticker_map[field].append(ticker)

  for f, ts in ticker_map.items():
    print('Class %s: %d tickers' % (f, len(ts)))
    output_dir = '%s/%s' % (args.output_dir, f.replace(' ', '_'))
    if not os.path.isdir(output_dir):
      os.mkdir(output_dir)
    output_file = '%s/tickers.txt' % output_dir
    with open(output_file, 'w') as fp:
      for t in sorted(ts):
        print(t, file=fp)

if __name__ == '__main__':
  main()

