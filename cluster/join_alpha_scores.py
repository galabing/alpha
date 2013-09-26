#!/usr/local/bin/python3

import argparse
import os

OUTPUT_FOLDER = 'alpha_scores'

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--score_dir', required=True)
  parser.add_argument('--cluster_base_dir', required=True)
  args = parser.parse_args()

  score_files = os.listdir(args.score_dir)
  clusters = os.listdir(args.cluster_base_dir)
  for cluster in clusters:
    cluster_dir = '%s/%s' % (args.cluster_base_dir, cluster)
    if not os.path.isdir(cluster_dir):
      continue
    ticker_file = '%s/tickers.txt' % cluster_dir
    if not os.path.isfile(ticker_file):
      continue
    with open(ticker_file, 'r') as fp:
      tickers = set(fp.read().splitlines())
    output_dir = '%s/%s' % (cluster_dir, OUTPUT_FOLDER)
    if not os.path.isdir(output_dir):
      os.mkdir(output_dir)
    for sf in score_files:
      if not sf.endswith('.txt'):
        continue
      with open('%s/%s' % (args.score_dir, sf), 'r') as fp:
        lines = fp.read().splitlines()
      with open('%s/%s' % (output_dir, sf), 'w') as fp:
        prev_score = None
        for line in lines:
          ticker, score = line.split(' ')
          score = float(score)
          if prev_score is not None:
            assert prev_score >= score
          prev_score = score
          if ticker in tickers:
            print(line, file=fp)

if __name__ == '__main__':
  main()

