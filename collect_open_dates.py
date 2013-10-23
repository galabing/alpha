#!/usr/local/bin/python3

""" Collects open dates from historical data.
"""

import argparse
import datetime
import os

# Define a date to be open if 90% of the stocks overlapping
# this date are open.
MIN_RATIO = 0.9

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--output_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  date_map = dict()
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('Processing %d/%d: %s' % (i+1, len(tickers), ticker))
    input_file = '%s/%s.csv' % (args.price_dir, ticker)
    if not os.path.isfile(input_file):
      print('!! %s does not exist, skipping' % input_file)
      continue
    with open(input_file, 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) > 0
    assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
    # Update market dates for this stock (numerator).
    pd = None
    for line in lines[1:]:
      d, o, h, l, c, v, a = line.split(',')
      if pd is None:
        pd = d
      else:
        assert d < pd
      if d not in date_map:
        date_map[d] = [1, 0]
      else:
        date_map[d][0] += 1
    # Update all dates for this stock (denominator).
    fd = lines[1][:lines[1].find(',')]
    ld = lines[-1][:lines[-1].find(',')]
    assert fd > ld
    date = datetime.datetime.strptime(ld, '%Y-%m-%d')
    delta = datetime.timedelta(days=1)
    while True:
      d = date.strftime('%Y-%m-%d')
      if d not in date_map:
        date_map[d] = [0, 1]
      else:
        date_map[d][1] += 1
      if d >= fd:
        break
      date += delta

  ratio_map = dict()
  for k, v in date_map.items():
    assert v[0] <= v[1]
    assert v[1] > 0
    ratio_map[k] = float(v[0])/v[1]
  count = 0
  with open(args.output_file, 'w') as fp:
    for k in sorted(ratio_map.keys()):
      if ratio_map[k] >= MIN_RATIO:
        print(k, file=fp)
        count += 1
  print('%d out of %d dates are open' % (count, len(ratio_map)))
  ratios = sorted(ratio_map.values())
  print('min ratio: %f' % ratios[0])
  print('max ratio: %f' % ratios[-1])
  print('median ratio: %f' % ratios[int(len(ratios)/2)])
  print('1%% ratio: %f' % ratios[int(len(ratios)*0.01)])
  print('10%% ratio: %f' % ratios[int(len(ratios)*0.1)])
  print('90%% ratio: %f' % ratios[int(len(ratios)*0.9)])
  print('99%% ratio: %f' % ratios[int(len(ratios)*0.99)])

if __name__ == '__main__':
  main()

