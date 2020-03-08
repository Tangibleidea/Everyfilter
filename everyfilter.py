from __future__ import print_function
import tldextract # pip install tldextract
import pickle
import os
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
#SPREADSHEET_ID = '16XngdfajuFrCzi_fIUr6kyNiRRfVM_aVQfIKk38G4Oc'
service = None
def getSheetList(sheetURL):
    global service
    if(service is None):
        service= getSheetService()
        
    sheet_metadata = service.spreadsheets().get(spreadsheetId=sheetURL).execute()

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


def readSheet(sheetURL, sheetName):
    global service
    #Call the Sheets API
    rangeName= sheetName+ "!A:Z"

    if service is None:
        service = getSheetService()

    arrSource= []

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheetURL, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            # Print columns A to Z, which correspond to indices 0 to 25.
            for x in range(25):
                try:
                    FilteredDomain = ValidateDomain(row[x])
                    if FilteredDomain is not None:
                        arrSource.append(FilteredDomain)
                except IndexError:
                    continue
    return arrSource


def ValidateDomain(url):
    filter= ""
    if url.startswith('!') == True:
        return None
        
    delimeter_location= url.find('$')
    if delimeter_location is not -1:
        filter= url[:url.find('$')]
    filter= filter.replace('#', '').replace('|', '').replace('^', '')
    ext = tldextract.extract(filter)

    ret= None
    if ext.domain.strip() != '' and ext.suffix.strip() != '':
        if ext.subdomain.strip() == '':
            ret = (ext.domain +'.'+ ext.suffix)
        else:
            ret = (ext.subdomain +'.'+ ext.domain +'.'+ ext.suffix)
        if url.find('third-party') != -1:
            ret += " (third-party)"
        if url.find('domain') != -1:
            ret += " (domain)"
    return ret

def readSourceFromABPFilters(url):
    arrSource= []   
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = response.data.decode('utf-8')
    for line in data.splitlines():
        FilteredDomain = ValidateDomain(line)
        if FilteredDomain is not None:
            arrSource.append(FilteredDomain)
    print('done')
    return arrSource

def savePickle(target):
    with open('dump.filters', 'wb') as f:
        pickle.dump(target, f)

def openPickle():
    with open('dump.filters', 'rb') as f:
        data = pickle.load(f)
    return data

def saveTXT(target):
    with open('dump.filters', 'w', encoding='UTF-8', newline='') as f:
        for item in target:
            f.write("%s\n" % item)

def openTXT():
    arrLines= []
    with open('dump.filters', encoding='UTF-8') as file:
        for line in file:
            line = line.strip() #preprocess line
            arrLines.append(line)
    return arrLines

def main():
    global service

    list_all = []
    start_time = time.time()
    # if path.exists("dump.filters"):
    #     opened= openTXT()
    #     print(opened)
    # else:
    arr_source = readSourceFromABPFilters("https://easylist-downloads.adblockplus.org/koreanlist+easylist.txt")
    list_all.append("! [koreanlist+easylist.txt]")
    list_all.extend(arr_source)

    #readSheet("16XngdfajuFrCzi_fIUr6kyNiRRfVM_aVQfIKk38G4Oc", "")
    arrSheet= getSheetList("18epO6j4tKn0fsh8zYUSWHO0u_7Q3eRF2K3DT-Z7Quhg")
    print(arrSheet)
    for sheet in arrSheet:
        list_all.append("! [" + sheet + " of 18epO6j4tKn0fsh8zYUSWHO0u_7Q3eRF2K3DT-Z7Quhg]")
        arr_source2 = readSheet("18epO6j4tKn0fsh8zYUSWHO0u_7Q3eRF2K3DT-Z7Quhg", sheet)
        list_all.extend(arr_source2)
        

        list_all_disticted = list(set(list_all))
        saveTXT(list_all_disticted)

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