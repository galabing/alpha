#!/usr/local/bin/python3

#./analyze_tbk2.py --score_dir=../../data_alpha/alpha_scores/ --ticker_file=../../data_alpha/cluster/price_0-20/0-20/tickers.txt --od_file=../../data_alpha/open_dates.txt --gain_file=../../data_alpha/gainc_7.txt --tbk=t30

gk = [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 98, 105, 112]
#dk = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
dk = [0]
tbk = ['t30', 'b30']

import os
for g in gk:
  for d in dk:
    for tb in tbk:
      cmd = './analyze_tbk2.py --score_dir=../../data_alpha/alpha_scores/ --ticker_file=../../data_alpha/cluster/price_0-20/0-20/tickers.txt --od_file=../../data_alpha/open_dates.txt --gain_file=../../data_alpha/gainc_%d.txt --delay=%d --tbk=%s >> ./analyze_tbk2.log' % (g, d, tb)
      print(cmd)
      assert os.system(cmd) == 0

