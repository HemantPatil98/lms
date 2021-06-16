from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
from .models import extra_data
from .sheetfields import *
# from .models import extra_data
from django.shortcuts import HttpResponse
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
global SPREADSHEET_ID
SPREADSHEET_ID = 'None'
if os.path.exists('spreadsheet_id.txt'):
    fp = open('spreadsheet_id.txt','r')
    SPREADSHEET_ID = fp.read()
    fp.close()
SAMPLE_RANGE_NAME = 'Sheet1!A1:E'

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
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)


service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

def startsheet():

    if not extra_data.objects.filter(name='student_performance'):
        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Student Performance',columns=student_performance,sheetname=sheetname)

        ex = extra_data(name='student_performance',value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='student_profile'):
        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Student Profile',columns=student_profile,sheetname=sheetname)

        ex = extra_data(name='student_profile', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='attendance'):
        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Attendance',columns=attendance,sheetname=sheetname)

        ex = extra_data(name='attendance', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='feedback'):
        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Feedback',columns=feedback,sheetname=sheetname)

        ex = extra_data(name='feedback', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='batch_schedule'):
        sheetname = "Sheet 1"
        SPREADSHEET_ID = createsheet(name='Batch Schedule',columns=batch_schedule,sheetname=sheetname)

        ex = extra_data(name='batch_schedule', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='MCQ'):
        sheetname = "Sheet 1"
        SPREADSHEET_ID = createsheet(name='MCQ',columns=mcq,sheetname=sheetname)

        ex = extra_data(name='MCQ', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='PRACTICAL'):
        sheetname = "Sheet 1"
        SPREADSHEET_ID = createsheet(name='PRACTICAL', columns=program, sheetname=sheetname)

        ex = extra_data(name='PRACTICAL', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='PROGRAM'):
        sheetname = "Sheet 1"
        SPREADSHEET_ID = createsheet(name='PROGRAM', columns=program, sheetname=sheetname)

        ex = extra_data(name='PROGRAM', value=SPREADSHEET_ID)
        ex.save()


#Create Spreadsheet
def createsheet(name,columns,sheetname):
    spreadsheet = {
        'properties': {
            'title': name
        },
        "sheets": [
            {
              "properties": {
                "title": sheetname
              }
            }
          ]
        }
    spreadsheet = sheet.create(body=spreadsheet,fields='spreadsheetId').execute()
    global SPREADSHEET_ID
    SPREADSHEET_ID = spreadsheet.get('spreadsheetId')

    addcolumns(SPREADSHEET_ID,sheetname,columns)

    return SPREADSHEET_ID



def addcolumns(SPREADSHEET_ID,sheetname,columns):
    sheet_fields = columns

    sheet_fields = [x.upper() for x in sheet_fields]

    values = [sheet_fields]
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=sheetname+'!1:1',
        body={
        'majorDimension': 'ROWS',
        'values': values
    }
    ).execute()

def addsheet(SPREADSHEET_ID,sheetname,columns):
    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheetname,

                }
            }
        }]
    }
    response = sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID,body=body).execute()
    addcolumns(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=sheetname,columns=columns)


def sheetvalues(SPREADSHEET_ID,sheetname,range='!A2:BE'):
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=sheetname+range).execute()
    values = result.get('values', [])

    if not values:
        return None
    else:
        return values


def getsheetnames(SPREADSHEET_ID):
    properties = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = []
    # print("p=",properties)
    for item in properties['sheets']:
        # print(item['properties']['title'])

        sheets.append(item.get("properties").get('title'))
    return sheets


def appendsheet(SPREADSHEET_ID,values,range='!A:A',dimension='ROWS',sheetname="Apr - Mar "+datetime.datetime.now().strftime("%Y")):
    properties = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = []
    flag = 1
    # print(sheetname+range)
    for item in properties['sheets']:
        sheets.append(item.get("properties").get('title'))

    for s in sheets:
        if s == sheetname:
            flag = 0
            break

    column = []
    if 'student_performance' == extra_data.objects.filter(value=SPREADSHEET_ID)[0].name:
        column = student_performance
    elif 'student_profile' == extra_data.objects.filter(value=SPREADSHEET_ID)[0].name:
        column = student_profile
    elif 'attendance' == extra_data.objects.filter(value=SPREADSHEET_ID)[0].name:
        column = attendance
    elif 'attendance' == extra_data.objects.filter(value=SPREADSHEET_ID)[0].name:
        column = attendance


    if flag:
        addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=sheetname,columns=column)

    value_range_body = {
        'majorDimension': dimension,
        'values': values
    }

    res = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=sheetname+range,
        body=value_range_body
    ).execute()

    import re
    try:
        txt = res['tableRange'].split(':')[1]
        x = re.search('[0-9]', txt)
    except:
        txt = res['updates']['updatedRange'].split('!')[1].split(':')[1]
        x = re.search('[0-9]',txt)

    return txt[x.span()[0]:len(txt)]

def updatesheet(SPREADSHEET_ID,SHEET_NAME,row,value,col=0,cell=False,dimension="ROWS"):
    if cell:
        body = {
            'majorDimension': dimension,
            "values": [
                    value
            ]
        }
        request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                    range=SHEET_NAME+"!"+col+str(row)+":"+col+str(row),
                                    valueInputOption="USER_ENTERED", body=body)
    else:
        body = {
            'majorDimension': dimension,
            "values": value
        }

        if dimension == 'ROWS':
            request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=SHEET_NAME+"!"+str(row)+":"+str(row+len(value)),
                                    valueInputOption="USER_ENTERED", body=body)
        else:
            request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=SHEET_NAME + "!"+str(chr(col+64)) +":"+str(chr(col+64)),
                                            valueInputOption="USER_ENTERED", body=body)
        # print(request)
    response = request.execute()
    print(response)

