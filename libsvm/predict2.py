#!/usr/local/bin/python3

""" This script looks for model files in the current directory and data files
    in the 'predictions' subdirectory.  yyyy-mm-dd.txt.model is used to predict
    predictions/yyyy-mm-dd.txt.
"""

import datetime
import os
import re

def run(cmd):
  print('Running command: %s' % cmd)
  assert os.system(cmd) == 0

data_prog = re.compile('^\d{4}-\d{2}-\d{2}\.txt$')

model_dates = set()
files = os.listdir('.')
for f in files:
  if data_prog.match(f):
    if os.path.isfile('./%s.model' % f) and os.path.isfile('./%s.range' % f):
      model_dates.add(f[:f.find('.')])
print('Found %d model dates: %s' % (len(model_dates), model_dates))

data_files = []
files = os.listdir('./predictions')
for f in files:
  if data_prog.match(f):
    data_files.append(f)
print('Found %d data files: %s' % (len(data_files), data_files))

for df in data_files:
  date = df[:df.find('.')]
  if date not in model_dates:
    print('No model available for date %s ' % date)
    continue
  test_file = './predictions/%s.scale' % df
  run('svm-scale -r ./%s.range ./predictions/%s > %s'
      % (df, df, test_file))
  run('svm-predict -b 1 %s ./%s.model %s.out'
      % (test_file, df, test_file))

