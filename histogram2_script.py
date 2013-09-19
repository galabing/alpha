#!/usr/local/bin/python3

import os

ios = [
    ['alpha_scores', 'alpha_histograms2_30'],
    ['libsvm_30_out_src', 'libsvm_src_histograms2_30'],
    ['libsvm_30_out_dst', 'libsvm_dst_histograms2_30'],
    ['libsvm_30_out_rec', 'libsvm_rec_histograms2_30']
]

ks = [10, 20, 30]

for io in ios:
  i, o = io
  for x in ['t', 'b']:
    for k in ks:
      cmd = ('./histogram2.py --score_dir=../data_alpha/%s'
             ' --gain_file=../data_alpha/gains_30.txt --tbk=%s%d'
             ' --histogram_file=../data_alpha/%s/%s%d.csv'
             % (i, x, k, o, x, k))
      print(cmd)
      assert os.system(cmd) == 0

