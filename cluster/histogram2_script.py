#!/usr/local/bin/python3

import os

ks = [10, 20, 30]
gdays = 30
cluster_base = 'gng9'
input_folder = 'alpha_scores'
output_folder = 'alpha_histograms2_%d' % gdays

cluster_home_dir = '../../data_alpha/cluster'
cluster_base_dir = '%s/%s' % (cluster_home_dir, cluster_base)
clusters = os.listdir(cluster_base_dir)
ios = []
for cluster in clusters:
  cluster_dir = '%s/%s' % (cluster_base_dir, cluster)
  if not os.path.isdir(cluster_dir):
    continue
  score_dir = '%s/%s' % (cluster_dir, input_folder)
  assert os.path.isdir(score_dir)
  histogram_dir = '%s/%s' % (cluster_dir, output_folder)
  if not os.path.isdir(histogram_dir):
    os.mkdir(histogram_dir)
  ios.append((score_dir, histogram_dir))

for io in ios:
  i, o = io
  for x in ['t', 'b']:
    for k in ks:
      cmd = ('../histogram2.py --score_dir=%s'
             ' --gain_file=../../data_alpha/gains_%d.txt --tbk=%s%d'
             ' --histogram_file=%s/%s%d.csv'
             % (i, gdays, x, k, o, x, k))
      print(cmd)
      assert os.system(cmd) == 0

