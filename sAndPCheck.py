import pandas as pd
import yfinance as yf
import os
import smtplib
import ssl
import time


SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


smtp_server = "smtp.mail.yahoo.com"
port = 465  
sender_email = SENDER_EMAIL
receiver_email = RECIPIENT_EMAIL
password = EMAIL_PASSWORD

# Subject lines text
subject_text = 'Buy or Sell stocks'

# Index specific message text
## S&P 500
sandp_message_text = '''
ETFs:
Vanguard S&P 500 ETF: VOO
iShares Core S&P ETF: IVV
SPDR S&P 500 ETF: SPY
SPDR Portfolio S&P 500 ETF: SPLG

Index Funds:
Schwab S&P 500 Index Fund: SWPPX
Fidelity 500 Index Fund: FXAIX
Vanguard 500 Index Fund Admiral Shares: VFIAX
State Street S&P 500 Index Fund Class N: SVSPX
'''

## Dow Jones
dj_message_text = '''
ETFs:
SPDR Dow Jones Industrial Average ETF Trust: DIA
Schwab US Broad Market ETF: SCHB 
'''

## NASDAQ
nasdaq_message_text = '''
ETFs:
Invesco Nasdaq 100 ETF: QQQM
Invesco QQQ: QQQ
'''

### Russell
russell_message_text = '''
ETFs:
Vanguard's Russell 2000 ETF: VTWO
Direxion Daily Small Cap Bull 3x Shares: TNA
BlackRock's iShares Russell 2000 ETF: IWM
'''

sandp_message = 'Subject: {}\n\n{}'.format(subject_text, sandp_message_text)
dj_message = 'Subject: {}\n\n{}'.format(subject_text, dj_message_text)
nasdaq_message = 'Subject: {}\n\n{}'.format(subject_text, nasdaq_message_text)
russell_message = 'Subject: {}\n\n{}'.format(subject_text, russell_message_text)

messages = [sandp_message, dj_message, nasdaq_message, russell_message]

tickers = ['^GSPC', '^DJI', '^IXIC', '^RUT']

hist_files = ['sandp_hist.csv', 'dowjones_hist.csv', 'nasdaq_hist.csv', 'russell_hist.csv']

dod_chgs_loss = [-0.01147873, -0.01548024, -0.01421591, -0.02035182]
wow_chgs_loss = [-0.03177592, -0.03197264, -0.04213725, -0.04555398]
mom_chgs_loss = [-0.04931180, -0.05204150, -0.08436092, -0.08876828]

dod_chgs_gain = [0.006793501, 0.005650722, 0.006119077, 0.004868226]
wow_chgs_gain = [0.023496256, 0.014506593, 0.022056676, 0.024617206]
mom_chgs_gain = [0.049507707, 0.048641329, 0.052482625, 0.055777122]


def checkStock(stock_ticker, message_text, dod_chg_loss, dod_chg_gain, wow_chg_loss, wow_chg_gain, mom_chg_loss, mom_chg_gain, hist_file):
  # Download ticker data from yfinance

  index_data = yf.Ticker(stock_ticker)

  index_data_last_month = index_data.history(period="1mo", interval="1d", prepost=False, actions=False, auto_adjust=True)

  index_data_last_month.reset_index(level=0, inplace=True)

  index_data_last_month = index_data_last_month.sort_values(by="Date", ascending=False).reset_index(drop=True)

  assert isinstance(index_data_last_month, pd.DataFrame)

  # Get day-over-day, week-over-week, and month-over-month change
  DoD = (index_data_last_month.loc[0, 'Close'] - index_data_last_month.loc[1, 'Close']) / index_data_last_month.loc[1, 'Close']

  WoW = (index_data_last_month.loc[0, 'Close'] - index_data_last_month.loc[5, 'Close']) / index_data_last_month.loc[5, 'Close']

  n_rows = (len(index_data_last_month) - 1)

  MoM = (index_data_last_month.loc[0, 'Close'] - index_data_last_month.loc[n_rows, 'Close']) / index_data_last_month.loc[n_rows, 'Close']

  # Add to the total dataframe
  latest_date = index_data_last_month['Date'][0]
  latest_values = index_data_last_month['Close'][0]

  changes_over_time_list = [DoD, WoW, MoM]
  latest_date_list = [latest_date] * 3
  latest_value_list = [latest_values] * 3

  latest_dict = {'Changes': changes_over_time_list, 
  'Change Value': ['DoD', 'WoW', 'MoM'], 'Close': latest_value_list, 'Date': latest_date_list}

  latest_DF = pd.DataFrame(latest_dict)

  hist_DF = pd.read_csv(hist_file, parse_dates=['Date'])

  full_DF = pd.concat([latest_DF, hist_DF])

  full_DF.to_csv(hist_file, index=False)

  DoD_check = (DoD < dod_chg_loss) | (DoD > dod_chg_gain)
  WoW_check = (WoW < wow_chg_loss) | (WoW > wow_chg_gain)
  MoM_check = (MoM < mom_chg_loss) | (MoM > mom_chg_gain)

  if (DoD_check & WoW_check & MoM_check):

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message_text)
    
    print(f"Email sent for {stock_ticker}")
  else:
    print(f"No email needed for {stock_ticker}")


for i in range(len(tickers)):
  checkStock(tickers[i], messages[i], dod_chgs_loss[i], dod_chgs_gain[i], wow_chgs_loss[i], wow_chgs_gain[i], mom_chgs_loss[i], mom_chgs_gain[i], hist_files[i])
  time.sleep(3)

# Research resources
# Gmail API: https://developers.google.com/gmail/api/reference/rest & https://developers.google.com/gmail?hl=en 
# Gmail API Python Quickstart: https://developers.google.com/gmail/api/quickstart/python
# Gmail API Sending Emails: https://developers.google.com/gmail/api/guides/sending#python 

# https://github.com/marketplace/actions/send-email
# https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions

# Using SMTP (preffered)
# https://realpython.com/python-send-email/
# https://fulowa.medium.com/how-to-send-emails-using-python-and-github-actions-e3f09209044d
# App password?
# https://support.google.com/accounts/answer/185833?hl=en
# https://spacejelly.dev/posts/how-to-schedule-daily-email-reports-with-github-actions-gmail-cron/
# Use Yahoo!
