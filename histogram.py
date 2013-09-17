#!/usr/local/bin/python3

""" Makes a histogram by breaking a stock ranking into segments and calculating
    the average gain within each segment.
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

def make_histogram(gains, num_bins):
  bin_size = int(len(gains)/num_bins)
  sizes = [bin_size for i in range(num_bins)]
  for i in range(len(gains)%num_bins):
    sizes[i] += 1
  assert sum(sizes) == len(gains)
  assert max(sizes) - min(sizes) <= 1
  indexes = [0]
  for i in range(num_bins):
    indexes.append(indexes[i] + sizes[i])
  assert indexes[-1] == len(gains)
  histogram = [sum(gains[indexes[i]:indexes[i+1]])/(indexes[i+1]-indexes[i])
               for i in range(num_bins)]
  mkt_gain = sum(gains)/len(gains)
  return histogram, mkt_gain

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--score_dir', required=True)
  parser.add_argument('--gain_file', required=True)
  parser.add_argument('--num_bins', default=100)
  parser.add_argument('--histogram_dir', required=True)
  args = parser.parse_args()

  gain_map = read_gain_map(args.gain_file)
  num_bins = int(args.num_bins)

  total_histogram = None
  score_files = os.listdir(args.score_dir)
  for sf in score_files:
    if not sf.endswith('.txt'):
      continue
    print('Processing %s' % sf)
    date = sf[:sf.find('.')]
    if date not in gain_map:
      print('!! Gains for %s is not verifiable' % date)
      continue
    with open('%s/%s' % (args.score_dir, sf), 'r') as fp:
      lines = fp.read().splitlines()
    print('\t%d scores' % len(lines))
    gains = []
    for line in lines:
      ticker, score = line.split(' ')
      if ticker in gain_map[date]:
        gains.append(gain_map[date][ticker])
    print('\t%d verifiable scores' % len(gains))
    histogram, mkt_gain = make_histogram(gains, num_bins)
    assert len(histogram) == num_bins
    print('\tMarket gain: %.2f%%' % (mkt_gain*100))
    with open('%s/%s.csv' % (args.histogram_dir, sf[:sf.find('.')]), 'w') as fp:
      for i in range(num_bins):
        print('%d,%.2f' % (i+1, histogram[i]*100), file=fp)
    if total_histogram is None:
      total_histogram = histogram
    else:
      assert len(total_histogram) == num_bins
      for i in range(num_bins):
        total_histogram[i] += histogram[i]
  with open('%s/total.csv' % args.histogram_dir, 'w') as fp:
    for i in range(num_bins):
      print('%d,%.2f' % (i+1, total_histogram[i]*100), file=fp)

if __name__ == '__main__':
  main()

