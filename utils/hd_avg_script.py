#!/usr/local/bin/python3

input_file = './analyze_tbk2.log'
output_file = './hd_avg.csv'

with open(input_file, 'r') as fp:
  lines = fp.read().splitlines()

hd_map = dict()
hs, ds = set(), set()
h, d = None, None
for i in range(len(lines)):
  if lines[i].startswith('Looking ahead'):
    _, _, h, _, _, d, _, _ = lines[i].split(' ')
    h, d = int(h), int(d)
    hs.add(h)
    ds.add(d)
  if lines[i].startswith('Total profit per week: '):
    p = float(lines[i][lines[i].rfind(' ')+1:lines[i].rfind('%')])
    key = 'h%dd%d' % (h, d)
    if key in hd_map:
      hd_map[key][0] += p
      hd_map[key][1] += 1
    else:
      hd_map[key] = [p, 1]
print(hd_map)

for k, v in hd_map.items():
  assert v[1] == 2
  hd_map[k] = v[0]/2

with open(output_file, 'w') as fp:
  print(','.join([str(item) for item in ['h/d'] + sorted(ds)]), file=fp)
  for h in sorted(hs):
    items = [str(h)]
    for d in sorted(ds):
      items.append('%.2f%%' % hd_map['h%dd%d' % (h, d)])
    print(','.join(items), file=fp)

