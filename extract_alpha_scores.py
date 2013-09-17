#!/usr/local/bin/python3

""" Extracts scores from alpha's ranking files.  The output will be a list
    of sorted (ticker, score) per ranking file.  The output file will be used
    for performance analysis (see histogram.py).
"""

import argparse
import csv
import os

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ranking_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  ranking_files = os.listdir(args.ranking_dir)
  for rf in ranking_files:
    if not rf.endswith('.csv'):
      continue
    with open('%s/%s' % (args.ranking_dir, rf), 'r') as fp:
      lines = fp.read().splitlines()
    ranks = []
    for row in csv.reader(lines[2:], delimiter=','):
      assert len(row) == 100
      if row[1] == '' or row[5] == '':
        continue
      ranks.append([row[1], float(row[5])])
    ranks.sort(key=lambda rank: rank[1], reverse=True)
    output_file = '%s/%s.txt' % (args.output_dir, rf[:rf.find('.')])
    with open(output_file, 'w') as fp:
      for rank in ranks:
        print('%s %f' % (rank[0], rank[1]), file=fp)

if __name__ == '__main__':
  main()

