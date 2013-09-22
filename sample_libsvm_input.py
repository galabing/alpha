#!/usr/local/bin/python3

""" Training data is sampled as follows:
    - For each target data file, collect training data from the past 1 to k
      months.  The lower bound is 1 to avoid look-ahead bias; the upper bound
      k is to capture time sensitive rules.
    - For each month's training data, feature points are sorted by descending
      gains.
    - Top and bottom n% of the features are used as training data, unless
      the total number of points exceeds threshold N, in which case n will
      be adjusted such that the total number of features falls below N.
"""

import argparse
import csv
import datetime
import os

MIN_DAYS, MAX_DAYS = 30, 30*4
TB_RATIO = 0.25  # Must < 0.5, otherwise there may be overlap in top/bottom.
MAX_COUNT = 6000
# If true, the top samples will be assigned +1 label, and the bottom samples
# will be assigned -1 label, regardless of the gain.
USE_RANK_LABEL = True

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
  dates = [rf[:rf.find('.')] for rf in ranking_files if rf.endswith('.csv')]
  date_map = dict()
  for d in dates:
    date_map[d] = []
    dd = datetime.datetime.strptime(d, '%Y-%m-%d')
    for d2 in dates:
      if d2 >= d:
        continue
      dd2 = datetime.datetime.strptime(d2, '%Y-%m-%d')
      delta = (dd - dd2).days
      if delta < MIN_DAYS or delta > MAX_DAYS:
        continue
      date_map[d].append(d2)

  for curr_date, past_dates in date_map.items():
    if curr_date not in gain_map:
      print('Skipping %s because no gain data is available' % curr_date)
      continue
    if len(past_dates) == 0:
      print('Skipping %s because no past data is available' % curr_date)
      continue

    # First pass, find out the total number of points.
    num_points = 0
    for pd in past_dates:
      with open('%s/%s.csv' % (args.ranking_dir, pd), 'r') as fp:
        lines = fp.read().splitlines()
      for row in csv.reader(lines[2:], delimiter=','):
        assert len(row) == 100
        ticker = row[1]
        features = row[5:]
        if ticker == '' or any([f == '' for f in features]):
          continue
        if ticker not in gain_map[pd]:
          continue
        num_points += 1
    print('%s: %d points from %s' % (curr_date, num_points, past_dates))
    r = min(TB_RATIO, float(MAX_COUNT)/num_points/2)

    # Second pass, collect and output data.
    ofp = open('%s/%s.txt' % (args.libsvm_dir, curr_date), 'w')
    for pd in past_dates:
      with open('%s/%s.csv' % (args.ranking_dir, pd), 'r') as fp:
        lines = fp.read().splitlines()
      points = []
      for row in csv.reader(lines[2:], delimiter=','):
        assert len(row) == 100
        ticker = row[1]
        features = row[5:]
        if ticker == '' or any([f == '' for f in features]):
          continue
        if ticker not in gain_map[pd]:
          continue
        point = [gain_map[pd][ticker], pd, ticker]
        point.extend([float(f) for f in features])
        points.append(point)
      points.sort(key=lambda point: point[0], reverse=True)
      num_points -= len(points)

      n = int(len(points) * r)
      for point in points[:n]:
        label = 1
        if not USE_RANK_LABEL:
          label = calc_label(point[0])
        print('%d %s #%s#%s'
              % (label,
                 ' '.join(['%d:%f' % (i-2, point[i])
                          for i in range(3, len(point))]),
                 point[1],
                 point[2]),
              file=ofp)
      for point in points[-n:]:
        label = -1
        if not USE_RANK_LABEL:
          label = calc_label(point[0])
        print('%d %s #%s#%s'
              % (label,
                 ' '.join(['%d:%f' % (i-2, point[i])
                          for i in range(3, len(point))]),
                 point[1],
                 point[2]),
              file=ofp)
    ofp.close()
    assert num_points == 0

  with open('%s/params' % args.libsvm_dir, 'w') as fp:
    print('MIN_DAYS=%d, MAX_DAYS=%d, TB_RATIO=%f, MAX_COUNT=%d'
          ', USE_RANK_LABEL=%s'
          % (MIN_DAYS, MAX_DAYS, TB_RATIO, MAX_COUNT, USE_RANK_LABEL), file=fp)

if __name__ == '__main__':
  main()

