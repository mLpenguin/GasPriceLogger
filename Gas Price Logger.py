#!/usr/bin/env python
# coding: utf-8

# In[2]:


#import requests

#import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver import ActionChains
import pandas as pd

import csv
import os.path
import datetime

import sys #import args


# In[3]:


def subtractDays(numOfDays):
    now = datetime.datetime.now()
    days = datetime.timedelta(numOfDays)
    
    new_date = now - days
    return new_date.strftime("%m-%d-%Y")


# In[4]:


def calculateDate(timeAgo):

    locOfDays = timeAgo.find('day')
    if (locOfDays!=-1):
        numOfDays = int(timeAgo[:locOfDays-1])
        #print(len(test[:locOfDays-1]))
        return subtractDays(numOfDays)
    else:
        return subtractDays(0)


# In[5]:


def readCSV(fileName):
    outputArray = []
    with open(fileName, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_ALL, skipinitialspace=True)
        next(reader, None)  # skip the headers
        
        for row in reader:
            temp = []
            for i in range(0,len(row)):
                if row[i] != '':
                    temp.append(row[i])
            #print (row[0])
            outputArray.append(temp)
    return outputArray


# In[6]:


def writeCSV(header, rows, filename, newFile=True):

    with open(filename, 'a', newline='') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
        
        if (newFile):
            # writing the fields 
            csvwriter.writerow(header) 

        # writing the data rows 
        csvwriter.writerows(rows)


# In[33]:


def dataframe_difference(df1, df2, which=None):
    """Find rows which are different between two DataFrames."""
    comparison_df = df1.merge(
        df2,
        indicator=True,
        how='outer'
    )
    if which is None:
        diff_df = comparison_df[comparison_df['_merge'] != 'both']
    else:
        diff_df = comparison_df[comparison_df['_merge'] == which]
    #diff_df.to_csv('data/diff.csv')
    return diff_df


# In[7]:


#STATION_URL = "https://www.gasbuddy.com/station/36156"


# In[8]:


def getData(STATION_URL):

    #STATION_URL = "https://www.gasbuddy.com/station/38348"

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get(STATION_URL)

    #Parse Data
    prices = browser.find_elements(By.CSS_SELECTOR,".text__xl___2MXGo.text__bold___1C6Z_.text__left___1iOw3.FuelTypePriceDisplay-module__price___3iizb")
    types = browser.find_elements(By.CSS_SELECTOR, ".text__left___1iOw3.GasPriceCollection-module__fuelTypeDisplay___eE6tM")
    times = browser.find_elements(By.CSS_SELECTOR, ".text__sm___1q2rU.text__left___1iOw3.FuelTypePriceDisplay-module__reportedTime___1Zinr.FuelTypePriceDisplay-module__reportedGrey___g8pgI")
    statonName = browser.find_element(By.CSS_SELECTOR, ".header__header1___3U_VP.header__header___1zII0").text

    pricesTxt = []
    timesTxt = []
    timesCounter = 0
    for x in range(len(prices)):
        if (prices[x].text == '- - -'):
            pricesTxt.append('N/A')
            timesTxt.append('NO DATA')
        else: 
            pricesTxt.append(prices[x].text)
            timesTxt.append(times[timesCounter].text)
            timesCounter+=1

    typesTxt = []
    for x in range(len(types)):
        typesTxt.append(types[x].text)


    print(len(pricesTxt))
    print(len(typesTxt))
    print(len(timesTxt))
    print(statonName)

    print(pricesTxt[0])
    print(typesTxt[0])
    print(timesTxt[0])
    print(statonName)

    #Build Array
    data = []

    if(len(prices) == len(types)):

        for x in range(len(prices)):

            date  = calculateDate(timesTxt[x])


            temp = [date, typesTxt[x], pricesTxt[x]]
            data.append(temp)

        header = ['Date','Type','Price']
    else:

        for x in range(len(typesTxt)):

            date  = calculateDate(timesTxt[x])
            temp = [date, 'CASH', typesTxt[x], pricesTxt[x]]
            data.append(temp)

        for x in range(len(typesTxt)):

            date  = calculateDate(timesTxt[x+len(typesTxt)])
            temp = [date, 'CARD', typesTxt[x], pricesTxt[x]]
            data.append(temp)
        header = ['Date','Payment_Type','Type','Price']

    #Remove Unknown Values
    df = pd.DataFrame(data)
    df = df[df.iloc[:, 0] != 'N/A']
    data = df.values.tolist()

    data

    browser.close()
    browser.quit()



    filename = statonName.replace(' ','_')+'.txt'
    print(filename)

    #Create new file or Append Data
    if (not os.path.isfile(filename)):
        writeCSV(header, data, filename)
    else: #Import existing data
        importedData = readCSV(filename)
        df = pd.DataFrame(data)
        importedDf = pd.DataFrame(importedData)

        #Find date of last entered data
        ##LastDateEntry = importedData[-1][-1]
        ##print(LastDateEntry)
        ##importedDfTrimmed = importedDf[(importedDf == LastDateEntry).any(axis=1)]

        importedDfTrimmed = importedDf

        #Combine Df
        combined = df.append(importedDfTrimmed)

        #Remove Duplicates (not needed because of below)
        #dupRemoved = combined.drop_duplicates(keep=False)


        #Remove Existing Data
        dupRemoved = dataframe_difference(importedDfTrimmed, combined).drop(['_merge'], axis=1)
        #dupRemoved = dupRemoved[~dupRemoved.isin(importedDfTrimmed)]


        #Append Data
        dataToAppend = dupRemoved.values.tolist()
        print(dataToAppend)
        writeCSV(header, dataToAppend, filename,False)

'''
# In[ ]:


STATION_URL = "https://www.gasbuddy.com/station/38348"


# In[108]:


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
browser.get(STATION_URL)

#Parse Data
prices = browser.find_elements(By.CSS_SELECTOR,".text__xl___2MXGo.text__bold___1C6Z_.text__left___1iOw3.FuelTypePriceDisplay-module__price___3iizb")
types = browser.find_elements(By.CSS_SELECTOR, ".text__left___1iOw3.GasPriceCollection-module__fuelTypeDisplay___eE6tM")
times = browser.find_elements(By.CSS_SELECTOR, ".text__sm___1q2rU.text__left___1iOw3.FuelTypePriceDisplay-module__reportedTime___1Zinr.FuelTypePriceDisplay-module__reportedGrey___g8pgI")
statonName = browser.find_element(By.CSS_SELECTOR, ".header__header1___3U_VP.header__header___1zII0").text

pricesTxt = []
timesTxt = []
timesCounter = 0
for x in range(len(prices)):
    if (prices[x].text == '- - -'):
        pricesTxt.append('N/A')
        timesTxt.append('NO DATA')
    else: 
        pricesTxt.append(prices[x].text)
        timesTxt.append(times[timesCounter].text)
        timesCounter+=1

typesTxt = []
for x in range(len(types)):
    typesTxt.append(types[x].text)


print(len(pricesTxt))
print(len(typesTxt))
print(len(timesTxt))
print(statonName)

print(pricesTxt[0])
print(typesTxt[0])
print(timesTxt[0])
print(statonName)

#Build Array
data = []

if(len(prices) == len(types)):

    for x in range(len(prices)):

        date  = calculateDate(timesTxt[x])


        temp = [pricesTxt[x], typesTxt[x], date]
        data.append(temp)

    header = ['Date','Type','Price']
else:

    for x in range(len(typesTxt)):

        date  = calculateDate(timesTxt[x])
        temp = [pricesTxt[x],'CASH', typesTxt[x], date]
        data.append(temp)

    for x in range(len(typesTxt)):

        date  = calculateDate(timesTxt[x+len(typesTxt)])
        temp = [pricesTxt[x+len(typesTxt)],'CARD', typesTxt[x], date]
        data.append(temp)
    header = ['Date','Payment_Type','Type','Price']

#Remove Unknown Values
df = pd.DataFrame(data)
df = df[df.iloc[:, 0] != 'N/A']
data = df.values.tolist()

data

browser.close()
browser.quit()



filename = statonName.replace(' ','_')+'.txt'
print(filename)

#Create new file or Append Data
if (not os.path.isfile(filename)):
    writeCSV(header, data, filename)
else: #Import existing data
    importedData = readCSV(filename)
    df = pd.DataFrame(data)
    importedDf = pd.DataFrame(importedData)

    #Find date of last entered data
    ##LastDateEntry = importedData[-1][-1]
    ##print(LastDateEntry)
    ##importedDfTrimmed = importedDf[(importedDf == LastDateEntry).any(axis=1)]

    importedDfTrimmed = importedDf

    #Combine Df
    combined = df.append(importedDfTrimmed)

    #Remove Duplicates (not needed because of below)
    #dupRemoved = combined.drop_duplicates(keep=False)


    #Remove Existing Data
    dupRemoved = dataframe_difference(importedDfTrimmed, combined).drop(['_merge'], axis=1)
    #dupRemoved = dupRemoved[~dupRemoved.isin(importedDfTrimmed)]


    #Append Data
    dataToAppend = dupRemoved.values.tolist()
    print(dataToAppend)
    writeCSV(header, dataToAppend, filename,False)


# In[66]:


dataframe_difference(importedDfTrimmed, combined).drop(['_merge'], axis=1)


# In[106]:


importedDf


# In[76]:


importedData


# In[77]:


df


# In[84]:


f = pd.unique(importedDf.iloc[:, 2]).tolist()


# In[99]:


(importedDf == f[0]).any(axis=1)


# In[103]:


f


# In[105]:


importedDf[(importedDf == f[-3]).any(axis=1)]


# In[52]:


dupRemoved

'''
# In[9]:


#getData("https://www.gasbuddy.com/station/36156")


# In[ ]:


command = str(sys.argv[1]).replace("\'", "")
getData(command)

