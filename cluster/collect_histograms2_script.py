#!/usr/local/bin/python3

import os

cluster_home_dir = '../../data_alpha/cluster'
#cluster_bases = ['cap', 'price', 'sec']
cluster_bases = ['gng4']
histogram_input_folder = 'alpha_histograms2_30'
#histogram_input_filebases = ['t10', 't20', 't30', 'b10', 'b20', 'b30']
histogram_input_filebases = ['t10', 't20', 'b10', 'b20']
histogram_output_dir = '%s/output/all_histograms2' % cluster_home_dir

for cb in cluster_bases:
  cluster_base_dir = '%s/%s' % (cluster_home_dir, cb)
  clusters = os.listdir(cluster_base_dir)
  for c in clusters:
    cluster_dir = '%s/%s' % (cluster_base_dir, c)
    if not os.path.isdir(cluster_dir):
      continue
    histogram_input_dir = '%s/%s' % (cluster_dir, histogram_input_folder)
    assert os.path.isdir(histogram_input_dir)
    histogram_map = dict()
    for fb in histogram_input_filebases:
      histogram_file = '%s/%s.csv' % (histogram_input_dir, fb)
      if not os.path.isfile(histogram_file):
        break
      with open(histogram_file, 'r') as fp:
        lines = fp.read().splitlines()
      histogram_map[fb] = lines
    if set(histogram_map.keys()) != set(histogram_input_filebases):
      print('!! Not enough histogram files for %s' % c)
    rows = []
    first_dates, first_mkts = None, None
    for fb in histogram_input_filebases:
      if len(rows) == 0:
        for i in range(len(histogram_map[fb])):
          rows.append([])
      dates, mkts = [], []
      for i in range(len(histogram_map[fb])):
        date, gain, mkt = histogram_map[fb][i].split(',')
        rows[i].append(gain)
        dates.append(date)
        mkts.append(mkt)
      if first_dates is None:
        first_dates = dates
        first_mkts = mkts
      assert first_dates == dates
      assert first_mkts == mkts
    assert len(first_dates) == len(rows)
    assert len(first_mkts) == len(rows)
    with open('%s/%s__%s.csv' % (histogram_output_dir, cb, c), 'w') as fp:
      print(','.join(['date'] + histogram_input_filebases + ['mkt']), file=fp)
      for i in range(len(rows)):
        print(','.join([dates[i]] + rows[i] + [mkts[i]]), file=fp)

