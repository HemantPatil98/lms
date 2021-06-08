student_performance = ['Id','Certificate No', 'Name', 'Contact No', 'Email ID', 'Admission Date', 'Training Mode',
                       'Course Start Date', 'Course', 'Course Start From', 'Current Module',
                       'C Trainer Name', 'C module start date', 'C module end date',
                       'C Theory (Out of 40)','C Practical (Out of 40)', 'C Oral (Out of 20)', 'C Total Marks (Out of 100)',
                       'Sql Trainer Name', 'Sql module start date', 'Sql module end date',
                       'Sql Theory (Out of 40)', 'Sql Practical (Out of 40)', 'Sql Oral (Out of 20)', 'Sql Total Marks (Out of 100)',
                       'WD Trainer Name', 'WD module start date', 'WD module end date',
                       'WD Practical (Out of 150)', 'WD Oral (Out of 50)', 'WD Total Marks (Out of 200)', 'Portfolio URL',
                       'Mock Interview Remark - 1',
                       'Core Trainer Name', 'Core module start date', 'Core module end date',
                       'Core Theory (Out of 40)', 'Core Practical (Out of 40)', 'Core Oral (Out of 20)', 'Core Total Marks (Out of 100)',
                       'Mock Interview Remark - 2',
                       'Adv Trainer Name', 'Adv module start date', 'Adv module end date',
                       'Adv Theory (Out of 40)','Adv Practical (Out of 40)', 'Adv Oral (Out of 20)', 'Adv Total Marks (Out of 100)',
                       'Full Course End Date','Project Guide', 'Cravita Poject Start Date',
                       'Mock Interview Remark - 3', 'Mock Interview Remark - 4',
                       'Soft Skills Marks (Out of 100)', 'Final Mock Interview', 'Total Marks (Out of 700)',
                       'Eligible For Certificate(Y/N)', 'Eligible For Placement(Y/N)', 'Certificate Issued On', 'Grade', 'Remark'
                       ]

basic = ["center", "date of admission", "course", "batch start date","module start from","training mode"]
personal_details = ["name", "address", "date of birth", "contact", "alternate contact", "emailid"]
educational_details = ['examination', 'stream', 'college name', 'boardname', 'year of passing', 'percentage']
fees = ["fees", "mode", "reg ammount", "installment1", "installment2", "installment3", "reg date",
        "installment1 date",
        "installment2 date", "installment3 date"]

remark = ["remark"]

student_profile = ["id", "datetime"] + basic + personal_details + educational_details + fees + remark

attendance = ["id","user_id","name","contact","emailid"]

feedback = ["id","date","student name","contact no","email id","course name","trainer name/mentor name",
            "Does your class starts on time?","Has your trainer solved all your queries with regards to technical skills",
            "Does your menotor gives you practical sessoins","How much you will rate your trainer/mentor",
            "How much will you rate overall fortune clouds it training service",
            "Any suggestions for trainer & fortune Cloud Technologies","would you like to refer friend","friends name",
            "friends contact"]

batch_schedule = ["time", "module name", "start date", "mentor name", "end date","upcoming module start date",
                  "upcoming module name", "mentor name"]

mcq = ["question","option1","option2","option3","option4","answer","explanation"]

program = ['Program']


all_fields = [student_performance,student_profile,attendance,feedback,mcq,program]
all_fields_index = {'student_performance':{},'student_profile':{},'attendance':{},'feedback':{},'mcq':{},'program':{}}

marks = {'C Total Marks (Out of 100)':'','Sql Total Marks (Out of 100)':'','WD Total Marks (Out of 200)':'','Core Total Marks (Out of 100)':'','Adv Total Marks (Out of 100)':'','Total Marks (Out of 700)':''}

from django.shortcuts import HttpResponse
def indexing_fields():
    for table,index_table in zip(all_fields,all_fields_index):
        i = ''
        ch = 'A'
        for field in table:
            all_fields_index[index_table][field] = i+ch
            if ch != 'Z':
                ch = chr(ord(ch) + 1)
            else:
                if i == '':
                    i = 'A'
                    ch = 'A'
                else:
                    i = chr(ord(i)+1)
                    ch = 'A'

    marks['C Total Marks (Out of 100)'] = '=sum(INDIRECT("'+all_fields_index['student_performance']['C Theory (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['C Practical (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['C Oral (Out of 20)']+'"&ROW()))'

    marks['Sql Total Marks (Out of 100)'] = '=sum(INDIRECT("'+all_fields_index['student_performance']['Sql Theory (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['Sql Practical (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['Sql Oral (Out of 20)']+'"&ROW()))'

    marks['WD Total Marks (Out of 200)'] = '=sum(INDIRECT("'+all_fields_index['student_performance']['WD Practical (Out of 150)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['WD Oral (Out of 50)']+'"&ROW()))'

    marks['Core Total Marks (Out of 100)'] = '=sum(INDIRECT("'+all_fields_index['student_performance']['Core Theory (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['Core Practical (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['Core Oral (Out of 20)']+'"&ROW()))'

    marks['Adv Total Marks (Out of 100)'] = '=sum(INDIRECT("'+all_fields_index['student_performance']['Adv Theory (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['Adv Practical (Out of 40)']+'"&ROW())'+\
                             ',INDIRECT("'+all_fields_index['student_performance']['Adv Oral (Out of 20)']+'"&ROW()))'

    marks['Total Marks (Out of 700)'] = '=sum(INDIRECT('""+all_fields_index['student_performance']['C Total Marks (Out of 100)']+'"&ROW())'+\
                                        ',INDIRECT("'+all_fields_index['student_performance']['Sql Total Marks (Out of 100)']+'"&ROW())'+ \
                                        ',INDIRECT("' + all_fields_index['student_performance']['WD Total Marks (Out of 200)'] + '"&ROW())' + \
                                        ',INDIRECT("' + all_fields_index['student_performance']['Core Total Marks (Out of 100)'] + '"&ROW())' + \
                                        ',INDIRECT("' + all_fields_index['student_performance']['Adv Total Marks (Out of 100)'] + '"&ROW())' + \
                                        ',INDIRECT("' + all_fields_index['student_performance']['Soft Skills Marks (Out of 100)'] + '"&ROW()))'
    # print(all_fields_index['student_performance'])

import os
def make_media_directory():
    media_structure = ['media','media/profile_photo','media/notice','media/certificate','media/programs','media/videos',
                       'media/videos/courses','media/videos/courses','media/videos/thumb']
    for path in media_structure:
        if not os.path.exists(path):
            os.mkdir(path)
