#!/bin/sh

D='2013-10-06'
P='13 Nov'

./rank_stocks.py\
 --ticker_file=../../data_alpha/virtual/$D/t30.txt\
 --oprice_dir=../../data_alpha/virtual/$D/oprices\
 --date_prefix="$P"\
 --type=call\
 --correction_file=../../data_alpha/virtual/$D/corrections.txt\
 | tee ../../data_alpha/virtual/$D/call.txt

./rank_stocks.py\
 --ticker_file=../../data_alpha/virtual/$D/b30.txt\
 --oprice_dir=../../data_alpha/virtual/$D/oprices\
 --date_prefix="$P"\
 --type=put\
 --correction_file=../../data_alpha/virtual/$D/corrections.txt\
 | tee ../../data_alpha/virtual/$D/put.txt

