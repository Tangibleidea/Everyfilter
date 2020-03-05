from __future__ import print_function
import tldextract # pip install tldextract
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
 
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1Pg30XVEQtW2dkhtmCR2uIJW8CfJhPzyvEJ1KO110CTM'
RANGE_NAME = 'top_3000_south_korea_traffic_new!A:A'
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

def main():
    global service
    getSheetList()
    
    #service = getSheetService()
    # Call the Sheets API
    # sheet = service.spreadsheets()
    # result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    # values = result.get('values', [])

    # if not values:
    #     print('No data found.')
    # else:
    #     print('Name, Major:')
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         #print('%s, %s' % (row[0], row[4]))
    #         print(row[0])

if __name__ == '__main__':
    main()