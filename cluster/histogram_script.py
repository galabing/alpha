#!/usr/local/bin/python3

import os

folder = 'price_0-20'

lookahead = 12
num_bins = 10
script = '../histogram.py'
cluster_home_dir = '../../data_alpha/cluster'
score_folder = 'alpha_scores'
histogram_folder = 'alpha_histograms_%d_%d' % (lookahead, num_bins)

cluster_base_dir = '%s/%s' % (cluster_home_dir, folder)
clusters = os.listdir(cluster_base_dir)
for cluster in clusters:
  cluster_dir = '%s/%s' % (cluster_base_dir, cluster)
  if not os.path.isdir(cluster_dir):
    continue
  if not os.path.isfile('%s/tickers.txt' % (cluster_dir)):
    continue
  histogram_dir = '%s/%s' % (cluster_dir, histogram_folder)
  if not os.path.isdir(histogram_dir):
    os.mkdir(histogram_dir)
  cmd = ('%s --score_dir=%s/%s --gain_file=../../data_alpha/gains_%d.txt'
         ' --num_bins=%d --histogram_dir=%s'
         % (script, cluster_dir, score_folder, lookahead, num_bins,
            histogram_dir))
  print(cmd)
  assert os.system(cmd) == 0

