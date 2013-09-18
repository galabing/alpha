#!/usr/local/bin/python3

""" This script looks for yyyy-mm-dd.txt files in the current directory and
    trigger libsvm's easy.py to train a model on each of them.
"""

import datetime
import os
import re

def run(cmd):
  print('[%s] Running command: %s' % (datetime.datetime.now(), cmd))
  assert os.system(cmd) == 0

def exist(f):
  SUFFIXES = ['.model', '.range', '.scale', '.scale.out', '.easy.log']
  for s in SUFFIXES:
    if not os.path.isfile('./%s%s' % (f, s)):
      return False
  return True

prog = re.compile('^\d{4}-\d{2}-\d{2}\.txt$')

files = os.listdir('.')
for f in files:
  if not prog.match(f):
    continue
  log_file = './%s.easy.log' % f
  if not exist(f):
    run('./easy.py %s > %s' % (f, log_file))
    assert exist(f)
  # Parse log file to find the optimal c, gamma values.
  with open(log_file, 'r') as fp:
    lines = fp.read().splitlines()
  assert len(lines) >= 3
  items = lines[-3].split(' ')
  assert len(items) == 4
  assert items[0] == 'Best'
  keys, values = ['c', 'g', 'cvrate'], []
  for i in range(3):
    k, v = items[i+1].split('=')
    assert k == keys[i]
    values.append(float(v))
  c, g, r = values
  print('c = %f, g = %f, cvrate = %f' % (c, g, r))
  # Retrain the model with probability support.
  run('svm-train -c %f -g %f -b 1 %s.scale %s.model' % (c, g, f, f))
  assert exist(f)

