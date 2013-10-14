alpha
=====

regression procedure:
download_price_history.py
calc_gains.py
extract_alpha_scores.py
extract_price.py
// optional: recombine tickers (eg, into price 0-20)
join_alpha_scores.py
histogram_script.py
histogram2_script.py

stock picking procedure:
download from http://www.alphastreetresearch.com/home/stock-ranking-list => xlsx
upload to google doc, convert to csv => rankings
extract_alpha_scores.py
pick_stocks.py
download_option_quotes.py
rank_stocks.sh

paste command:
paste -d , t10.csv t20.csv t30.csv b10.csv b20.csv b30.csv > paste.csv


