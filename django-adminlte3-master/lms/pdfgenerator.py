
from io import BytesIO,StringIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.views.generic import View
from django.utils import timezone
from .models import *
import os
from datetime import datetime
from .sheetsapi import sheetvalues
from .sheetfields import student_performance

###
class Render:

    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)


        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

    @staticmethod
    def render_to_file(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        # file_name = "{0}-{1}.pdf".format(params['request'].user.first_name, randint(1, 1000000))
        file_name = "Offer Letter.pdf"
        file_path = os.path.join(os.path.abspath(os.path.dirname("__file__")), "", file_name)
        with open(file_path, 'wb') as pdf:
            pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf)
        return [file_name, file_path]

###
class Pdf(View):

    def get(self, request):
        # sales = Sales.objects.all()
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
        SHEET_NAME = "Apr - Mar " +datetime.now().strftime("%Y")
        up = user_profile.objects.get(user_id=request.user.id)
        range = "!"+str(up.student_performance_row)+':'+str(up.student_performance_row)
        values = sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

        # print(values)
        today = timezone.now()
        print(values[0])
        params = {
            'id':request.user.id,
            'addate': datetime.strptime(values[0][student_performance.index('Admission Date')],"%Y-%m-%d"),
            'name': request.user.first_name,
            'contact': values[0][2]
        }
        # Render.render_to_file('student/pdf.html',params)
        return Render.render('student/pdf.html', params)

