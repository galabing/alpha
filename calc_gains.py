#!/usr/local/bin/python3

""" Calculates gains of all stocks at specified dates.  The output file will
    be used to train/test stock classifiers.
    Output format:
        <date> <ticker> <gain>
"""

import argparse
import datetime
import os

# The number of days in which gain is calculated.
PERIOD_DAYS = 90
# Eg, 2013-09-16.
TIME_FORMAT = '%Y-%m-%d'
# Max delay in days in finding stock price for a specified date.
MAX_DELAY_DAYS = 7

def add_days(date, days):
  return (datetime.datetime.strptime(date, TIME_FORMAT)
          + datetime.timedelta(days=PERIOD_DAYS)).strftime(TIME_FORMAT)

def find_price(prices, date):
  prev_price = None
  for price in prices:
    if price[0] < date:
      break
    prev_price = price
  if prev_price is None:
    return None
  prev_date = datetime.datetime.strptime(prev_price[0], TIME_FORMAT)
  date = datetime.datetime.strptime(date, TIME_FORMAT)
  if (prev_date - date).days > MAX_DELAY_DAYS:
    return None
  return prev_price[1]

def process(ticker_file, dates, ticker, gfp):
  with open(ticker_file, 'r') as fp:
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
  for date in dates:
    total += 1
    price = find_price(prices, date)
    date2 = add_days(date, PERIOD_DAYS)
    price2 = find_price(prices, date2)
    if price is None or price <= 0 or price2 is None or price2 <= 0:
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
  parser.add_argument('--gain_file', required=True)
  args = parser.parse_args()

  with open(args.ticker_file, 'r') as fp:
    tickers = fp.read().splitlines()

  ranking_files = os.listdir(args.ranking_dir)
  dates = [rf[:rf.find('.')] for rf in ranking_files if rf.endswith('.csv')]
  print('Processing %d dates: %s' % (len(dates), dates))

  total, processed = 0, 0
  gfp = open(args.gain_file, 'w')
  for i in range(len(tickers)):
    ticker = tickers[i]
    print('%d/%d: %s' % (i+1, len(tickers), ticker))
    price_file = '%s/%s.csv' % (args.price_dir, ticker)
    if not os.path.isfile(price_file):
      print('Could not find price file for %s' % ticker)
      continue
    t, p = process(price_file, dates, ticker, gfp)
    total += t
    processed += p
  gfp.close()
  print('Processed %d out of %d date/stock pairs' % (processed, total))

if __name__ == '__main__':
  main()

