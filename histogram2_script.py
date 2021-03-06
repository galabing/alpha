#!/usr/local/bin/python3

import os

ios = [
##
#    ['alpha_scores', 'alpha_histograms2_30'],
#    ['libsvm_30_out_src', 'libsvm_src_histograms2_30'],
#    ['libsvm_30_out_dst', 'libsvm_dst_histograms2_30'],
#    ['libsvm_30_out_rec', 'libsvm_rec_histograms2_30'],
##
#    ['libsvms_30_a_out', 'libsvms_30_a_histograms2'],
##
    ['alpha_scores', 'alpha_histograms2_90'],
]

ks = [10, 20, 30]
gdays = 90

for io in ios:
  i, o = io
  for x in ['t', 'b']:
    for k in ks:
      cmd = ('./histogram2.py --score_dir=../data_alpha/%s'
             ' --gain_file=../data_alpha/gains_%d.txt --tbk=%s%d'
             ' --histogram_file=../data_alpha/%s/%s%d.csv'
             % (i, gdays, x, k, o, x, k))
      print(cmd)
      assert os.system(cmd) == 0

