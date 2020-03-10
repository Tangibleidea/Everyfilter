from __future__ import print_function
from collections import OrderedDict
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
import urllib3
from urllib.request import urlopen
import time
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# How long the google spreadsheet id is.
SPREADSHEET_ID_DIGIT = 44

service = None
def getSheetList(sheetURL):
    global service
    if(service is None):
        service= getSheetService()
        
    sheet_metadata = service.spreadsheets().get(spreadsheetId=sheetURL).execute()

    sheetList = []
    properties = sheet_metadata.get('sheets')
    for  item in properties:
        #print(item)
        sheetName= item.get("properties").get('title')
        #print(sheetName)
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
    filter= url
    if url.strip() == '':
        return None
    if url.startswith('!') == True:
        return None

    # blocking filter
    delimeter_location= url.find('$')
    if delimeter_location != -1:
        filter= filter[:delimeter_location]

    # hiding filter
    delimeter_location= url.find('##')
    if delimeter_location != -1:
        filter= filter[:delimeter_location]

    filter= filter.replace('#', '').replace('|', '').replace('^', '')
    ext = tldextract.extract(filter)

    ret= None
    if ext.domain.find(' ') != -1:
        return None

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
    
        # could have plural filters in 1 line.
        delimeter= line.find(',')
        option_marker= line.find('$')
        is_comment = line.startswith('!')
        if delimeter != -1 and option_marker is -1 and not is_comment:   # if there is ',' + no '$'
            multi_filters= line.split(',') # then split it by ','
            for line_mf in multi_filters:  # and loop to validate every filter
                FilteredDomain = ValidateDomain(line_mf)
                if FilteredDomain is not None:
                    arrSource.append(FilteredDomain)

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

def AddSource(source):
    arr_source = []
    print("Updating latest filters from " + source + "...")
    if "adblockplus.org/" in source:
        arr_source.append("! [" + source + "]")
        arr_source.extend(readSourceFromABPFilters(source))
    elif "docs.google.com/spreadsheets" in source:
        splited= source.split('/')
        target_gid= None
        for x in splited:
            if len(x) == SPREADSHEET_ID_DIGIT:
                target_gid= x
        if target_gid != None:
            arrSheet = getSheetList(target_gid)
            for sheet in arrSheet:
                print("Sheet name: " + sheet + " of ID: " +target_gid)
                arr_source.append("! [Sheet name: " + sheet + " of ID: " +target_gid + "]")
                arr_source.extend(readSheet(target_gid, sheet))
    return arr_source


def main():
    global service

    list_all = []
    start_time = time.time()
    
    list_all.extend( AddSource("https://easylist-downloads.adblockplus.org/koreanlist+easylist.txt") )
    #list_all.extend( AddSource("https://docs.google.com/spreadsheets/d/18epO6j4tKn0fsh8zYUSWHO0u_7Q3eRF2K3DT-Z7Quhg") )
    #list_all.extend( AddSource("https://docs.google.com/spreadsheets/d/16XngdfajuFrCzi_fIUr6kyNiRRfVM_aVQfIKk38G4Oc") )
            
    list_all_disticted = list(OrderedDict.fromkeys(list_all))
    saveTXT(list_all_disticted)

    print("--- %s seconds ---" % (time.time() - start_time))

    
    

if __name__ == '__main__':
    main()
