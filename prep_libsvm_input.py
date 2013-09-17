#!/usr/local/bin/python3

import argparse
import csv
import os

# TODO: Also used by others.  Move up.
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

# TODO: May want to try
#           +1: if gain >= pos_threshold
#           -1: if gain <= neg_threshold
#       and train the models on more extreme data.
def calc_label(gain):
  if gain > 0:
    return 1
  return -1

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ranking_dir', required=True)
  parser.add_argument('--gain_file', required=True)
  parser.add_argument('--libsvm_dir', required=True)
  args = parser.parse_args()

  gain_map = read_gain_map(args.gain_file)

  ranking_files = os.listdir(args.ranking_dir)
  for rf in ranking_files:
    if not rf.endswith('.csv'):
      continue
    print('Processing ranking file: %s' % rf)
    date = rf[:rf.find('.')]
    if date not in gain_map:
      print('!! Gains for %s is unknown' % date)
      continue
    with open('%s/%s' % (args.ranking_dir, rf), 'r') as fp:
      lines = fp.read().splitlines()
    num_bad_features, num_bad_labels = 0, 0
    with open('%s/%s.txt' % (args.libsvm_dir, rf[:rf.find('.')]), 'w') as fp:
      for row in csv.reader(lines[2:], delimiter=','):
        assert len(row) == 100
        ticker = row[1]
        features = row[5:]
        if ticker == '' or any([f == '' for f in features]):
          num_bad_features += 1
          continue
        if ticker not in gain_map[date]:
          num_bad_labels += 1
          continue
        features = [float(f) for f in features]
        gain = gain_map[date][ticker]
        label = calc_label(gain)
        print('%d %s #%s'
              % (label,
                 ' '.join(['%d:%f' % (i+1, features[i])
                           for i in range(len(features))]),
                 ticker),
              file=fp)
    print('\tProcessed %d lines, %d bad features, %d bad labels'
          % (len(lines)-2, num_bad_features, num_bad_labels))

if __name__ == '__main__':
  main()

