#!/usr/local/bin/python3

""" This script looks for model files and data files in the current directory
    and triggers libsvm's predictor on the data files.

    In order not to cheat, the models used for prediction must be trained more
    than k days ago, where k being the look-ahead for training labels.  This
    script looks for a ^d\d+$ patterend filename in the current directory
    (eg, d30), and use its value as k.
"""

import datetime
import os
import re

def run(cmd):
  print('Running command: %s' % cmd)
  assert os.system(cmd) == 0

data_prog = re.compile('^\d{4}-\d{2}-\d{2}\.txt$')
k_prog = re.compile('^d\d+$')

data_files = []
k = None
files = os.listdir('.')
for f in files:
  if k_prog.match(f):
    k = int(f[1:])
    print('Look ahead: %d days' % k)
    continue
  if data_prog.match(f):
    data_files.append(f)
assert k is not None
print('Found %d base data files: %s' % (len(data_files), data_files))

models = []
for df in data_files:
  if os.path.isfile('./%s.model' % df) and os.path.isfile('./%s.range' % df):
    models.append(df)
print('Found %d models trained from these files %s' % (len(models), models))

for model in models:
  for df in data_files:
    md = datetime.datetime.strptime(model[:model.find('.')], '%Y-%m-%d')
    dd = datetime.datetime.strptime(df[:df.find('.')], '%Y-%m-%d')
    if (dd - md).days < k:
      continue
    print('%s => %s' % (model, df))
    test_file = '%s.scale_%s' % (df, model[:model.find('.')])
    run('svm-scale -r %s.range %s > %s' % (model, df, test_file))
    run('svm-predict -b 1 %s %s.model %s.out' % (test_file, model, test_file))

