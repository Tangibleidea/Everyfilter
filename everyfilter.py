from __future__ import print_function
import tldextract # pip install tldextract
import pickle
from os import path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import sys
import ssl
import requests.api
import re
import validators
import urllib3
from urllib.request import urlopen
import time
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '16XngdfajuFrCzi_fIUr6kyNiRRfVM_aVQfIKk38G4Oc'
service = None
def getSheetList():
    global service
    if(service is None):
        service= getSheetService()
        
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()

    #sheet_id = None
    sheetList = []
    properties = sheet_metadata.get('sheets')
    for  item in properties:
        #print(item)
        sheetName= item.get("properties").get('title')
        print(sheetName)
        sheetList.append(sheetName)
    return sheetList

def getSheetService():
    global service # use global variable.
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('abptools_clientsecret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service


def readSheet(sheetName):
    global service
    #Call the Sheets API
    rangeName= sheetName= "!A:Z"

    if service is None:
        service = getSheetService()

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            # Print columns A to Z, which correspond to indices 0 to 25.
            for x in range(25):
                try:
                    print(row[x])
                except IndexError:
                    break



def readSource3(url):
    arrSource= []   
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = response.data.decode('utf-8')
    for line in data.splitlines():
        arrSource.append(line)
    print('done')
    return arrSource

def readSource1(url):
    arrSource= []   
    data = urlopen(url)
    for source in data:
        arrSource.append(source)
    print('done')

def savePickle(target):
    with open('dump.filters', 'wb') as f:
        pickle.dump(target, f)

def openPickle():
    with open('dump.filters', 'rb') as f:
        data = pickle.load(f)
    return data

def saveTXT(target):
    with open('dump.filters', 'w') as f:
        for item in target:
            f.write("%s\n" % item)

def openTXT():
    arrLines= []
    with open("C:\name\MyDocuments\numbers") as file:
        for line in file:
            line = line.strip() #preprocess line
            arrLines.append(line)
    return arrLines

def main():
    global service

    start_time = time.time()
    if path.exists("dump.filters"):
        opened= openTXT()
        print(opened)
    else:
        arrSource= readSource3("https://easylist-downloads.adblockplus.org/easylist.txt")
        saveTXT(arrSource)

    print("--- %s seconds ---" % (time.time() - start_time))
    # if validators.domain('http://stackoverflow.com/a/30007882/697313'):
    #     print('this domain is valid')
    # else:
    #     print('this domain is not valid')

    # pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    #test_string1 = 'https://stackoverflow.com/a/30007882/697313'
    # test_string2 = '0.018321'
    # extracted = tldextract.extract(test_string2)
    # print(extracted)

    # result1 = re.findall(pattern, test_string1)
    # print(result1)
    # result2 = re.findall(pattern, test_string2)
    # print(result2)

    # if result:
    #     print("Search successful.")
    # else:
    #     print("Search unsuccessful.")	

    # try:
    #     service = getSheetService()
    # except requests.exceptions.SSLError:
    #     print("===SSLError===")

    # arrSheet= getSheetList()
    # for sheet in arrSheet:
    #     readSheet(sheet)

    
    

if __name__ == '__main__':
    main()