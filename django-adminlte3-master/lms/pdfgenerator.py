
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
from django.views.decorators.clickjacking import xframe_options_exempt

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
        file_path = os.path.join(os.path.abspath(os.path.dirname("__file__")), "", 'lms/static/'+file_name)
        with open(file_path, 'wb') as pdf:
            pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf)
        return [file_name, file_path]

###
class offerletter(View):

    def get(self, request):
        # sales = Sales.objects.all()
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
        SHEET_NAME = "Apr - Mar " +datetime.now().strftime("%Y")
        up = user_profile.objects.get(user_id=request.user.id)
        range = "!"+str(up.student_performance_row)+':'+str(up.student_performance_row)
        values = sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

        params = {
            'id':request.user.id,
            'addate': datetime.strptime(values[0][student_performance.index('Admission Date')],"%Y-%m-%d"),
            'name': request.user.first_name,
            'contact': values[0][3]
        }
        # Render.render_to_file('student/pdf.html',params)
        return Render.render('student/pdf.html', params)
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
class certificate(View):
    def get(self,request):
        # sales = Sales.objects.all()
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
        SHEET_NAME = "Apr - Mar " +datetime.now().strftime("%Y")
        up = user_profile.objects.get(user_id=request.user.id)
        range = "!"+str(up.student_performance_row)+':'+str(up.student_performance_row)
        values = sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

        params = {
            'id':request.user.id,
        }
        return Render.render('student/certificate.html', params)



def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def render_pdf_view(request):
    template_path = 'student/certificate.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class certificate1(View):

    @xframe_options_exempt
    def get(request):
        # sales = Sales.objects.all()
        SPREADSHEET_ID = extra_data.objects.get(name='student_performance').value
        SHEET_NAME = "Apr - Mar " +datetime.now().strftime("%Y")
        up = user_profile.objects.get(user_id=request.user.id)
        range = "!"+str(up.student_performance_row)+':'+str(up.student_performance_row)
        values = sheetvalues(SPREADSHEET_ID=SPREADSHEET_ID, sheetname=SHEET_NAME, range=range)

        params = {
            'id':request.user.id,
        }
        return render(request,'student/certificate.html')

    def render_to_file(request,path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        # file_name = "{0}-{1}.pdf".format(params['request'].user.first_name, randint(1, 1000000))
        file_name = "Offer Letter.pdf"
        file_path = os.path.join(os.path.abspath(os.path.dirname("__file__")), "", file_name)
        with open(file_path, 'wb') as pdf:
            pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf)
        return HttpResponse(str([file_name, file_path]))
