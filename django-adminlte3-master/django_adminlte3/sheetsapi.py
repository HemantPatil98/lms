from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
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
    if not os.path.exists('student_performance.txt'):
        # print("start")

        student_performance = ['id', 'Name', 'Contact No', 'Email ID', 'Admission Date', 'Training Mode',
                               'Course Start Date', 'Course',
                               'Course Start From', 'Current Module',
                               'C Trainer Name', 'C module end date', 'Theory ( Out of 40)', 'Practical (Out of 40)',
                               'Oral ( Out of 20)', 'Total Marks',
                               'Sql Trainer Name', 'Sql module end date', 'Theory ( Out of 40)',
                               'Practical (Out of 40)',
                               'Oral ( Out of 20)', 'Total Marks',
                               'WD Trainer Name', 'WD module end date', 'Theory ( Out of 40)', 'Practical (Out of 40)',
                               'Oral ( Out of 20)', 'Total Marks',
                               'Portfolio URL', 'Mock Interview Remark - 1( Excellent/Good/Poor)', 'Project Guide',
                               'Mini Project', 'Module End Date',
                               'Core Trainer Name', 'Core module end date', 'Core Theory ( Out of 40)',
                               'Core Practical (Out of 40)', 'Core Oral ( Out of 20)', 'Total Marks',
                               'Mock Interview Remark - 2( Excellent/Good/Poor)',
                               'Adv Trainer Name', 'Adv module end date', 'Adv Theory ( Out of 40)',
                               'Adv Practical (Out of 40)', 'Adv Oral ( Out of 20)', 'Total Marks',
                               'Full Course End Date', 'Cravita Poject Start Date',
                               'Mock Interview Remark - 3( Excellent/Good/Poor)',
                               'Soft Skills Marks ( Out of 100 )', 'Final Mock Interview', 'Total Marks ( Out of 700 )',
                               'Eligible For Placement(Y/N)', 'Remark'
                               ]

        SPREADSHEET_ID = createsheet('Student Performance',student_performance)

        fp = open('student_performance.txt', 'a')
        fp.write(SPREADSHEET_ID)
        fp.close()

    if not os.path.exists('student_profile.txt'):
        # print("start")

        student_profile = []
        basic = ["center", "dateofadmission", "course", "batchstartdate","module start from","trainingmode"]
        personal_details = ["name", "address", "dateofbirth", "contact", "emailid", "alternatecontact"]
        educational_details = ['examination', 'stream', 'collegename', 'boardname', 'yearofpassing', 'percentage']
        fees = ["fees", "mode", "regammount", "installment1", "installment2", "installment3", "regdate",
                "installment1date",
                "installment2date", "installment3date"]

        remark = ["remark"]

        student_profile = ["id", 'datetime'] + basic + personal_details + educational_details + fees + remark

        SPREADSHEET_ID = createsheet('Student Profile',student_profile)

        fp = open('student_profile.txt', 'a')
        fp.write(SPREADSHEET_ID)
        fp.close()

#Create Spreadsheet
def createsheet(name,columns):
    # print("create")
    sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
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
    # print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))
    # global SPREADSHEET_ID
    global SPREADSHEET_ID
    SPREADSHEET_ID = spreadsheet.get('spreadsheetId')

    addcolumns(sheetname,columns)

    return SPREADSHEET_ID



def addcolumns(sheetname,columns):

    sheet_fields = columns
    # print(sheet_fields)

    sheet_fields = [x.upper() for x in sheet_fields]
    # print(sheet_fields)

    values = [sheet_fields]
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=sheetname+'!A1:1',
        body={
        'majorDimension': 'ROWS',
        'values': values
    }
    ).execute()

def addsheet():
    print(sheet.get(spreadsheetId=SPREADSHEET_ID))
    sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
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
    addcolumns(sheetname)
    # print(response)

def sheetvalues(SPREADSHEET_ID,sheetname,range='!A2:AS'):

    # fields = "sheets(data(rowMetadata(hiddenByFilter)),properties/sheetId)"
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=sheetname+range).execute()
    values = result.get('values', [])

    if not values:
        return None
    else:
        return values


def appendsheet(sheetid,values):
    SPREADSHEET_ID = sheetid
    values = [values]
    sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
    properties = sheet.get(spreadsheetId=SPREADSHEET_ID).execute().get("sheets")
    # print(properties)
    sheets = []
    flag = 1
    for item in properties:
        sheets.append(item.get("properties").get('title'))
        # print(sheets)
    for s in sheets:
        # print(s,sheetname)
        if s == sheetname:
            flag = 0
            break

    if flag:
        addsheet()

        # sheet_id = (item.get("properties").get('sheetId'))

    value_range_body = {
        'majorDimension': 'ROWS',
        'values': values
    }
    # print(sheet.getActiveSpreadsheet())

    res = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=sheetname+'!E:E',
        body=value_range_body
    ).execute()
    print(res)

    # get last row index
    p = res.compile('^.*![A-Z]+\d+:[A-Z]+(\d+)$')
    match = p.match(res['tableRange'])
    lastrow = match.group(1)
    print(lastrow)


def updatesheet(request,row,col,value):
    body = {
        "values": [
            [
                value
            ]
        ]
    }
    fp = open('student_profile.txt', 'r')
    SPREADSHEET_ID = fp.read()
    fp.close()
    request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                                    range="Apr - Mar 2021!"+str(chr(col+64))+str(row+1)+":"+str(chr(col+64))+str(row+1),
                                    valueInputOption="USER_ENTERED", body=body)
    response = request.execute()
    print(response)
    print(str(chr(col+64))+str(row+1),value)
    return HttpResponse("")