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
password = EMAIL_PASSWORD
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

sAndPLastMonth = sAndPLastMonth.sort_values(by="Date", ascending=False).reset_index(drop=True)

assert isinstance(sAndPLastMonth, pd.DataFrame)

# Get day-over-day, week-over-week, and month-over-month change
DoD = (sAndPLastMonth.loc[0, 'Close'] - sAndPLastMonth.loc[1, 'Close']) / sAndPLastMonth.loc[1, 'Close']

WoW = (sAndPLastMonth.loc[0, 'Close'] - sAndPLastMonth.loc[5, 'Close']) / sAndPLastMonth.loc[5, 'Close']

n_rows = (len(sAndPLastMonth) - 1)

MoM = (sAndPLastMonth.loc[0, 'Close'] - sAndPLastMonth.loc[n_rows, 'Close']) / sAndPLastMonth.loc[n_rows, 'Close']

# Add to the total dataframe
latestDate = sAndPLastMonth['Date'][0]
latestValue = sAndPLastMonth['Close'][0]

changesOverTimeList = [DoD, WoW, MoM]
latestDateList = [latestDate] * 3
latestValueList = [latestValue] * 3

latestDict = {'Changes': changesOverTimeList, 
'Change Value': ['DoD', 'WoW', 'MoM'], 'Close': latestValueList, 'Date': latestDateList}

latestDF = pd.DataFrame(latestDict)

histDF = pd.read_csv('sAndPHist.csv', parse_dates=['Date'])

fullDF = latestDF.append(histDF)

fullDF.to_csv('sAndPHist.csv', index=False)

DoDCheck = DoD < -0.006561433645552261
WoWCheck = WoW < -0.018166249525890653
MoMCheck = MoM < -0.019372077488310015

if (DoDCheck & WoWCheck & MoMCheck):

  # Create a secure SSL context
  context = ssl.create_default_context()

  with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
      server.login(sender_email, password)
      server.sendmail(sender_email, receiver_email, message)


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
