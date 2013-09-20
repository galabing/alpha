#!/usr/local/bin/python3

""" Extracts scores from libsvm's output files, all of them.
"""

import argparse
import os
import re

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--libsvm_dir', required=True)
  parser.add_argument('--output_dir', required=True)
  args = parser.parse_args()

  # Eg, 2013-06-30.txt.scale.out
  prog = re.compile('^\d{4}-\d{2}-\d{2}\.txt\.scale\.out$')
  files = os.listdir(args.libsvm_dir)
  for f in files:
    if not prog.match(f):
      continue
    print('Processing %s' % f)
    date = f[:f.find('.')]
    data_file = '%s/%s.txt' % (args.libsvm_dir, date)
    assert os.path.isfile(data_file)
    # Load tickers.
    with open(data_file, 'r') as fp:
      tickers = [line[line.rfind('#')+1:] for line in fp.read().splitlines()]
    # Load predictions.
    with open('%s/%s' % (args.libsvm_dir, f), 'r') as fp:
      lines = fp.read().splitlines()
    assert len(lines) >= 1
    assert lines[0] == 'labels 1 -1'
    scores = []
    for i in range(1, len(lines)):
      label, pos, neg = lines[i].split(' ')
      assert label == '1' or label == '-1'
      pos, neg = float(pos), float(neg)
      assert abs(pos + neg - 1) < 1e-5
      scores.append(pos)
    assert len(tickers) == len(scores)
    ts = [[tickers[i], scores[i]] for i in range(len(tickers))]
    ts.sort(key=lambda item: item[1], reverse=True)
    with open('%s/%s.txt' % (args.output_dir, date), 'w') as fp:
      for item in ts:
        print('%s %f' % (item[0], item[1]), file=fp)

if __name__ == '__main__':
  main()

