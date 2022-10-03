from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
import ssl

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait #wating for content to load
from selenium.webdriver.support import expected_conditions as EC #required for passing 

import os
import pandas as pd
import schedule
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

def job():
    # email list of people we want ot email to
    # emaillist = ['angelamaharjan96@gmail.com', 'kimmhrz@gmail.com', 'supalamhrzn@gmail.com']
    emaillist = ['kimmhrz@gmail.com']

    driver.get("https://nepsealpha.com/trading-signals/tech")

    tkr = [ ]
    macds = [ ]

    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 10)

    # selecting 100 rows on the table from the default 10
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#funda-table_length > label > select"))).click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#funda-table_length > label > select > option:nth-child(4)"))).click()

    # loop for 2 pages
    for j in range(2):
        # For Ticker
        driver.implicitly_wait(5)
        tickers = driver.find_elements_by_css_selector("#funda-table > tbody > tr > td.fixed-left-header")
        for ticker in tickers:
            tkr.append(ticker.text)
            
        # For MACD
        macd = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/div/div/div/div[2]/div/div/div/div[3]/div[2]/table/tbody/tr/td[11]")
        for i in macd:
            macds.append(i.text)
            
        # Navigate to Next Page    
        wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div/div/div/div[2]/div/div/div/div[5]/a[2]"))).click()

    # Creating a dataframe
    df = {'TICKER': tkr, 'MACD': macds}
    dataset = pd.DataFrame.from_dict(df, orient = 'index')
    dataset = dataset.transpose()

    # Removing duplicate entries
    dataset = dataset.drop_duplicates()

    # Filtering Data
    bullish = dataset.loc[dataset['MACD'] == 'Bullish']
    bullish_list = list(bullish['TICKER'])
    bullish_list = str(bullish_list)
    bullish_list = bullish_list.replace("'", " ")
    bullish_list = bullish_list.replace("[", "")
    bullish_list = bullish_list.replace("]", "")
    print(bullish_list)

    # Email Part starts here
    # Creating Variables
    EMAIL_FROM = 'krishmzn69@gmail.com'
    SMTP_PD = 'aqfdkqdawdzqocye'
    EMAIL_TO = 'kimmhrz@gmail.com'

    EMAIL_SUBJECT = 'NEPSE bullish crossover of the day'
    MESSAGE_BODY = 'MACD technical analysis summary'
    
    msg = MIMEMultipart("alternative")
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    
    # Create the plain-text and HTML version of your message
    html = """\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <!-- css -->
            <style>
                h2, h4{
                    color:#000;
                }
            </style>
        </head>
        <body>
            <!-- body -->
            <h2>MACD bullish crossovers today</h2>
            <h4>$(data)</h4>
        </body>
        </html>
            """
        
    html = html.replace("$(data)", bullish_list)
    part1 = MIMEText(html, "html")

    # HTML/plain-text parts to MIMEMultipart message
    msg.attach(part1)
    # Converting the message to a string and send it
    context = ssl.create_default_context()
    
    # looping through email list
    for mail_loop in emaillist:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_FROM, SMTP_PD)
            smtp.sendmail(EMAIL_FROM, mail_loop, msg.as_string())
     
job()

schedule.every(1).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at('18:00').do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":17").do(job)

while True:
    schedule.run_pending()
    time.sleep(1) # wait one minute