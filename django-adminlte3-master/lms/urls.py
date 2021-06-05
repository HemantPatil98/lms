
from django.urls import path
from . import views,models,sheetsapi,pdfgenerator
sheetsapi.startsheet()

urlpatterns = [
    path('accounts/login/',views.login_form),
    path('',views.login_form,name='login_form'),
    path('login/',views.log_in,name='login'),
    path('logout/', views.log_out, name='logout'),
    path('respass/', views.reset_password, name='resspass'),
    path('sendotp/', views.sendotp, name='sendotp'),

    path('index/',views.index,name='index'),
    path('add/student/',views.addstudent,name='addstudents'),
    # path('view_data/student/',views.viewstudent,name='viewstudents'),
    # path('view_data/performance/', views.viewperformance, name='viewperformance'),
    path('add/groups/',views.addgroups,name='addgroups'),
    path('view/groups/<slug:view>/',views.addgroups,name='viewgroups'),
    path('add/users/',views.addusers,name='addusers'),
    path('user_permissions/',views.user_permissions,name='user_permissions'),
    path('view_data/members/', views.viewmembers, name='viewmembers'),
    path('profile/', views.viewprofile, name='viewprofile'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance_update/', views.attendance_update, name='attendance_update'),
    path('studentattendance/', views.studentattendance, name='studentsattendance'),
    path('attendance/', views.attendance, name='attendance'),
    path('add/notice/',views.addnotice,name='addnotice'),
    path('view/notice/',views.viewnotice,name='viewnotice'),
    path('add/certificate/', views.addcertificate, name='addcertificate'),
    path('get/certificate/', views.getcertificate, name='getcertificate'),
    path('set/certificate/', views.setcertificate, name='setcertificate'),

    path('timeline/', models.timeline.viewtimeline, name='timeline'),
    path('timelinedata/', models.timeline.timelinedata, name='timelinedata'),
    path('addtimeline/', models.timeline.addtimeline, name='addtimeline'),
    path('deletetimeline/', models.timeline.deletetimeline, name='deletetimeline'),

    path('addfeedback/', views.addfeedback, name='addfeedback'),
    # path('viewfeedback/', views.viewfeedback, name='viewfeedback'),

    path('request_certificate/',views.request_certificate,name='request_certificate'),

    path('getdata/<slug:table>/',views.get_data,name='getdata'),
    path('setdata/<slug:table>/',views.set_data,name='setdata'),

    path('getuser/',views.get_user,name='getuser'),
    path('setuser/',views.set_user,name='setuser'),

    # path('calender/',views.calender,name='calender'),
    path('schedule/',views.schedule,name='schedule'),
    # path('getcalenderevents/',views.getcalenderevents,name='getcalenderevents'),
    path('students_groups/<slug:gname>/',views.students_groups,name='students_groups'),
    path('students_current_groups/<slug:gname>/',views.students_current_groups,name='students_current_groups'),
    path('pdftest/',views.pdftest,name='pdftest'),
    path('render/pdf/', pdfgenerator.Pdf.as_view(),name='pdf'),

    path('sheetdata/<slug:table>/',views.sheetdata,name='sheetdata')

]