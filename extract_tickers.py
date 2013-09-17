#!/usr/local/bin/python3

""" Extracts tickers from ranking files.
"""

import argparse
import os

FIRST_SUFFIX = ',,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
SECOND_LINE = "Ranking,Ticker,Name,# NA's,Final Stmt,100% Stock Rank,Value,Pr2CashFlTTM,Pr2FrCashFlTTM,Pr2SalesTTM,Pr2TanBkQ,PrSalesQ (intu),Earn Yield (intu),PEExclXorTTM (intu),PEG (intu),PEGLT (intu),PERelative (intu),P2BookQ (intu),ev,ev /fcf,ev / projected earnings,CurrYEPSEstvs4W,NextYEPSEstvs4W,EPS Chg TTM,EV/FCFTTM,EV/EBITDA TTM,PEG (intu)2,PE Excl (Intu),PR2FcashFlttm(intu),EV/EBITDATTM (intu),EV/SalesTTM (intu),BV / Price (intu),Prc2SalesIncDebt,FCFTTM/MktCap,FCFQ/MktCap,ROE%Q,ROE%Q3,Technical,Pr52WRel%Chg,Pr4WRel%Chg,Pr26WRel%Chg,sar,macd,Beta (intu),Price (intu),vma(150)/vma(300),ema(50)/ema(100),1movs6movol,close(0)/sma(10),3MoPctRet,3MoRet3MoAgo,3MoPctRet (intu),VolM% Shsout (intu),RSI(5),dummy,Profitability,EBITDMgn%5YAvg,ROA%TTM,ROI%5YAvg,40% ROA/ROE,ROA Change,ROE Change,ROE%TTM (intu),Liquidity,Inst%Own,Liquidity2,MktCap (intu),MktCap,AvgDailyTot(200),Absolute price,Investor Concerns,Buyback,Buyback4,FCFQ/AstTotQ,FCFQ / DbtTotQ,SIRatio,AnalystSentChg,AnalystEPSChg,Surprise%Q (intu),LT Grwth Rate (intu),3 Mo SI Decrease (intu),Recommendation | SI Interaction,SI % Float (intu),TATA,TACC_TTM,Short Interest,Downgrade4WkAgo,Downgrade8WkAgo,CurFY4Wk,CurFY8Wk,CurFY13Wk,NextFY4Wk,NextFY8Wk,NextFY13Wk,NextFYEPSRevisedSmall?4,NextFYEPSRevisedMid?4,NextFYEPSRevisedBig?4,NextFYEPSRevisedSmall?8,NextFYEPSRevisedMid?8,NextFYEPSRevisedBig?8"

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--ranking_dir', required=True)
  parser.add_argument('--ticker_file', required=True)
  args = parser.parse_args()

  tickers = set()
  ranking_files = os.listdir(args.ranking_dir)
  for rf in ranking_files:
    if not rf.endswith('.csv'):
      continue
    with open('%s/%s' % (args.ranking_dir, rf), 'r') as fp:
      lines = fp.read().splitlines()
      assert len(lines) >= 2
      assert lines[0].endswith(FIRST_SUFFIX)
      assert lines[1] == SECOND_LINE
      for i in range(2, len(lines)):
        items = lines[i].split(',')
        if items[1] != '':
          tickers.add(items[1])

  with open(args.ticker_file, 'w') as fp:
    for t in sorted(tickers):
      print(t, file=fp)

if __name__ == '__main__':
  main()

