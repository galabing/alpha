#!/usr/local/bin/python3

""" Calculates gains of all stocks for a range of dates.  The output file will
    be used to train/test stock classifiers.
    Output format:
        <date> <ticker> <gain>
"""

import argparse
import datetime
import os

# Eg, 2013-09-16.
TIME_FORMAT = '%Y-%m-%d'
# Max delay in days in finding future stock price for a specified date.
MAX_DELAY_DAYS = 7

def add_days(date, days):
  return (datetime.datetime.strptime(date, TIME_FORMAT)
          + datetime.timedelta(days=days)).strftime(TIME_FORMAT)

def find_price(prices, date, max_delay_days):
  prev_price = None
  for price in prices:
    if price[0] < date:
      break
    prev_price = price
  if prev_price is None:
    return None
  prev_date = datetime.datetime.strptime(prev_price[0], TIME_FORMAT)
  date = datetime.datetime.strptime(date, TIME_FORMAT)
  if (prev_date - date).days > max_delay_days:
    return None
  return prev_price[1]

def process(price_file, min_date, max_date, ticker, lookahead, gfp):
  with open(price_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) >= 1
  assert lines[0] == 'Date,Open,High,Low,Close,Volume,Adj Close'
  prices = []
  for i in range(1, len(lines)):
    d, o, h, l, c, v, a = lines[i].split(',')
    if len(prices) > 0:
      assert prices[-1][0] > d
    prices.append([d, float(a)])
  total, processed = 0, 0
  date = None
  while date is None or date <= max_date:
    if date is None:
      date = min_date
    else:
      date = add_days(date, 1)
    total += 1
    price = find_price(prices, date, 0)
    if price is None or price <= 0:
      continue
    date2 = add_days(date, lookahead)
    price2 = find_price(prices, date2, MAX_DELAY_DAYS)
    if price2 is None or price2 <= 0:
      continue
    gain = (price2-price)/price
    print('%s %s %f' % (date, ticker, gain), file=gfp)
    processed += 1
  return total, processed

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ticker_file', required=True)
  parser.add_argument('--ranking_dir', required=True)
  parser.add_argument('--price_dir', required=True)
  parser.add_argument('--lookahead', required=True)
  parser.add_argument('--gain_file', required=True)
  args = parser.parse_args()

  # Sanity check.
  lookahead = int(args.lookahead)
  assert lookahead > 0
  assert int(args.gain_file[args.gain_file.rfind('_')+1:args.gain_file.rfind('.')]) == lookahead

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  ranking_files = os.listdir(args.ranking_dir)
  dates = [rf[:rf.find('.')] for rf in ranking_files if rf.endswith('.csv')]
  print('Processing %d dates: %s' % (len(dates), dates))
  min_date = min(dates)
  max_date = datetime.datetime.today().strftime(TIME_FORMAT)
  assert min_date < max_date
  print('min date = %s' % min_date)
  print('max date = %s' % max_date)

  total, processed = 0, 0
  gfp = open(args.gain_file, 'w')
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('%d/%d: %s' % (i+1, len(tickers), ticker))
    price_file = '%s/%s.csv' % (args.price_dir, ticker)
    if not os.path.isfile(price_file):
      print('Could not find price file for %s' % ticker)
      continue
    t, p = process(price_file, min_date, max_date, ticker, lookahead, gfp)
    total += t
    processed += p
  gfp.close()
  print('Processed %d out of %d date/stock pairs' % (processed, total))

if __name__ == '__main__':
  main()

