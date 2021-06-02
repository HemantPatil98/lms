from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
from .models import extra_data
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

        student_performance = ['id', 'Name', 'Contact No', 'Email ID', 'Admission Date', 'Training Mode',
                               'Course Start Date', 'Course',
                               'Course Start From', 'Current Module',
                               'C Trainer Name', 'C module start date','C module end date', 'Theory ( Out of 40)', 'Practical (Out of 40)',
                               'Oral ( Out of 20)', 'Total Marks',
                               'Sql Trainer Name', 'Sql module start date', 'Sql module end date', 'Theory ( Out of 40)',
                               'Practical (Out of 40)',
                               'Oral ( Out of 20)', 'Total Marks',
                               'WD Trainer Name', 'WD module start date', 'WD module end date', 'Practical (Out of 150)',
                               'Oral ( Out of 50)', 'Total Marks',
                               'Portfolio URL', 'Mock Interview Remark - 1( Excellent/Good/Poor)', 'Project Guide',
                               'Mini Project',
                               'Core Trainer Name', 'Core module start date', 'Core module end date', 'Core Theory ( Out of 40)',
                               'Core Practical (Out of 40)', 'Core Oral ( Out of 20)', 'Total Marks',
                               'Mock Interview Remark - 2( Excellent/Good/Poor)',
                               'Adv Trainer Name', 'Adv module start date', 'Adv module end date', 'Adv Theory ( Out of 40)',
                               'Adv Practical (Out of 40)', 'Adv Oral ( Out of 20)', 'Total Marks',
                               'Full Course End Date', 'Cravita Poject Start Date',
                               'Mock Interview Remark - 3( Excellent/Good/Poor)',
                               'Soft Skills Marks ( Out of 100 )', 'Final Mock Interview', 'Total Marks ( Out of 700 )',
                               'Eligible For Placement(Y/N)', 'Remark'
                               ]
        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Student Performance',columns=student_performance,sheetname=sheetname)

        ex = extra_data(name='student_performance',value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='student_profile'):

        basic = ["center", "date of admission", "course", "batch start date","module start from","trainingmode"]
        personal_details = ["name", "address", "date of birth", "contact", "alternate contact", "emailid"]
        educational_details = ['examination', 'stream', 'college name', 'boardname', 'year of passing', 'percentage']
        fees = ["fees", "mode", "reg ammount", "installment1", "installment2", "installment3", "reg date",
                "installment1 date",
                "installment2 date", "installment3 date"]

        remark = ["remark"]

        student_profile = ["id", 'datetime'] + basic + personal_details + educational_details + fees + remark

        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Student Profile',columns=student_profile,sheetname=sheetname)

        ex = extra_data(name='student_profile', value=SPREADSHEET_ID)
        ex.save()
    # print(os.path.exists('attendance.txt'))
    if not extra_data.objects.filter(name='attendance'):
        attendance = ["id","name","contact","emailid"]

        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Attendance',columns=attendance,sheetname=sheetname)

        ex = extra_data(name='attendance', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='feedback'):
        feedback = ["id","date","student name","contact no","email id","course name","trainer name/mentor name","Does your class starts on time?",
                    "Has your trainer solved all your queries with regards to technical skills","Does your menotor gives you practical sessoins",
                    "How much you will rate your trainer/mentor","How much will you rate overall fortune clouds it training service",
                    "Any suggestions for trainer & fortune Cloud Technologies","would you like to refer friend","friends name","friends contact"]

        sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
        SPREADSHEET_ID = createsheet(name='Feedback',columns=feedback,sheetname=sheetname)

        ex = extra_data(name='feedback', value=SPREADSHEET_ID)
        ex.save()

    if not extra_data.objects.filter(name='batch schedule'):
        attendance = ["time","module name","start date","mentor name","end date",
                      "upcoming module start date","upcoming module name","mentor name"]

        sheetname = "Sheet 1"
        SPREADSHEET_ID = createsheet(name='batch schedule',columns=attendance,sheetname=sheetname)


        ex = extra_data(name='Batch Schedule', value=SPREADSHEET_ID)
        ex.save()


#Create Spreadsheet
def createsheet(name,columns,sheetname):
    # print("create")
    # sheetname = "Apr - Mar " +datetime.datetime.now().strftime("%Y")
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

    addcolumns(SPREADSHEET_ID,sheetname,columns)

    return SPREADSHEET_ID



def addcolumns(SPREADSHEET_ID,sheetname,columns):

    sheet_fields = columns
    # print(sheet_fields)

    sheet_fields = [x.upper() for x in sheet_fields]
    # print(sheet_fields)

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
    print(sheet.get(spreadsheetId=SPREADSHEET_ID))
    # sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
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
    # print(response)

def sheetvalues(SPREADSHEET_ID,sheetname,range='!A2:BE'):

    # fields = "sheets(data(rowMetadata(hiddenByFilter)),properties/sheetId)"
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=sheetname+range).execute()
    values = result.get('values', [])
    # print(values)
    if not values:
        return None
    else:
        return values


def getsheetnames(SPREADSHEET_ID):
    properties = sheet.get(spreadsheetId=SPREADSHEET_ID).execute().get("sheets")
    sheets = []
    for item in properties:
        sheets.append(item.get("properties").get('title'))
    return sheets


def appendsheet(SPREADSHEET_ID,values,range='!A:A',dimension='ROWS',sheetname="Apr - Mar "+datetime.datetime.now().strftime("%Y")):
    # SPREADSHEET_ID = sheetid
    # values = [values]
    # sheetname = "Apr - Mar "+datetime.datetime.now().strftime("%Y")
    properties = sheet.get(spreadsheetId=SPREADSHEET_ID).execute().get("sheets")
    # print(properties)
    sheets = []
    flag = 1
    # assert isinstance(properties, object)
    for item in properties:
        sheets.append(item.get("properties").get('title'))
        # print(sheets)
    for s in sheets:
        # print(s,sheetname)
        if s == sheetname:
            flag = 0
            break

    if flag:
        addsheet(SPREADSHEET_ID=SPREADSHEET_ID,sheetname=sheetname)

        # sheet_id = (item.get("properties").get('sheetId'))

    value_range_body = {
        'majorDimension': dimension,
        'values': values
    }
    # print(sheet.getActiveSpreadsheet())

    res = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        valueInputOption='USER_ENTERED',
        range=sheetname+range,
        body=value_range_body
    ).execute()

    # print(res)
    import re
    try:
        txt = res['tableRange'].split(':')[1]
        x = re.search('[0-9]', txt)
    except:
        txt = res['updates']['updatedRange'].split('!')[1].split(':')[1]
        x = re.search('[0-9]',txt)
        # print(x)
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
                                    range=SHEET_NAME+"!"+str(chr(col+64))+str(row)+":"+str(chr(col+64))+str(row),
                                    valueInputOption="USER_ENTERED", body=body)
    else:
        body = {
            'majorDimension': dimension,
            "values": [value]
        }

        if dimension == 'ROWS':
            request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=SHEET_NAME+"!"+str(row)+":"+str(row+len(value)),
                                    valueInputOption="USER_ENTERED", body=body)
        else:
            request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,range=SHEET_NAME + "!"+str(chr(col+64)) +":"+str(chr(col+64)),
                                            valueInputOption="USER_ENTERED", body=body)
    # print(str(chr(col+64)))
    response = request.execute()
    print(response)
