import pandas as pd
import yfinance as yf
import os
import smtplib
import ssl


SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


smtp_server = "smtp.mail.yahoo.com"
port = 465  
sender_email = SENDER_EMAIL
receiver_email = RECIPIENT_EMAIL
password = PASSWORD
sAndPSubjectText = 'Buy stocks'
sAndPMessageText = '''
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
SPDR S&P 500 ETF: SPY
'''
message = 'Subject: {}\n\n{}'.format(sAndPSubjectText, sAndPMessageText)


# S&P 500 yahoo finance data from yfinance
sAndP = yf.Ticker('^GSPC')

sAndPLastMonth = sAndP.history(period="1mo", interval="1d", prepost=False, actions=False, auto_adjust=True)

sAndPLastMonth.reset_index(level=0, inplace=True)

sAndPLastMonth = sAndPLastMonth.sort_values(by="Date", ascending=False)

assert isinstance(sAndPLastMonth, pd.DataFrame)

# Get day-over-day, week-over-week, and month-over-month change
DoD = (sAndPLastMonth.loc[1, 'Close'] - sAndPLastMonth.loc[2, 'Close']) / sAndPLastMonth.loc[2, 'Close']

WoW = (sAndPLastMonth.loc[1, 'Close'] - sAndPLastMonth.loc[5, 'Close']) / sAndPLastMonth.loc[5, 'Close']

n_rows = (len(sAndPLastMonth) - 1)

MoM = (sAndPLastMonth.loc[1, 'Close'] - sAndPLastMonth.loc[n_rows, 'Close']) / sAndPLastMonth.loc[n_rows, 'Close']

# DoD: < -0.006561433645552261
# WoW: < -0.018166249525890653
# MoM: < -0.019372077488310015

DoD = True
WoW = True
MoM = True

if ((DoD) & (WoW) & (MoM)):

  # Create a secure SSL context
  context = ssl.create_default_context()

  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message)
