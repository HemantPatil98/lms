from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic.base import TemplateView
from . import views,sheetsapi
from django.conf import settings
from django.conf.urls.static import static
from. import sheetsapi
sheetsapi.startsheet()

urlpatterns = [
    # path('',include('django_adminlte3.urls')),
    path('accounts/login/',views.login_form),
    path('',views.login_form,name='login_form'),
    path('login/',views.log_in,name='login'),
    path('logout/', views.log_out, name='logout'),
    path('respass/', views.reset_password, name='resspass'),
    path('sendotp/', views.sendotp, name='sendotp'),
    path('index/',views.index,name='index'),
    # path('adminpannel/',views.admin,name='adminpannel'),
    path('add/student/',views.addstudent,name='addstudents'),
    path('view_data/student/',views.viewstudent,name='viewstudents'),
    path('view_data/performance/', views.viewperformance, name='viewperformance'),
    path('add/groups/',views.addgroups,name='addgroups'),
    path('view/groups/<slug:view>/',views.addgroups,name='viewgroups'),
    # path('view_data/groups/', views.viewgroups, name='viewgroups'),
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
    path('view/certificate/', views.viewcertificate, name='viewcertificate'),
    path('get/certificate/', views.getcertificate, name='getcertificate'),
    path('set/certificate/', views.setcertificate, name='setcertificate'),
    # path('student_performance_in/',views.student_performance_in,name='student_performance_in'),
    # path('student_performance_out/',views.student_performance_out,name='student_performance_out'),
    # path('student_profile_in/', views.student_profile_in, name='student_profile_in'),
    # path('student_profile_out/', views.student_profile_out, name='student_profile_out'),
    # path('admin/include/studentupdate/', views.studentupdate, name='updatesheet'),
    path('timeline/', views.viewtimeline, name='timeline'),
    path('timelinedata/', views.timelinedata, name='timelinedata'),
    path('addtimeline/', views.addtimeline, name='addtimeline'),
    path('deletetimeline/', views.deletetimeline, name='deletetimeline'),
    path('addfeedback/', views.addfeedback, name='addfeedback'),
    path('viewfeedback/', views.viewfeedback, name='viewfeedback'),
    # path('admin/include/view_data/performance/<int:row>/<int:col>/<slug:value>/<slug:cell>/', views.studentpupdate,
    #      name='updatesheet')
    # path('student/profile/update/',views.addstudent,name='studentprofileupdate')
    path('request_certificate/',views.request_certificate,name='request_certificate'),
    path('getdata/<slug:table>/',views.get_data,name='getdata'),
    path('setdata/<slug:table>/',views.set_data,name='setdata'),
    path('getuser/',views.get_user,name='getuser'),
    path('setuser/',views.set_user,name='setuser'),
    path('test/',views.test,name='test'),
    # path('calender/',views.calender,name='calender'),
    path('schedule/',views.schedule,name='schedule'),
    # path('getcalenderevents/',views.getcalenderevents,name='getcalenderevents'),
    path('students_groups/<slug:gname>/',views.students_groups,name='students_groups'),
    path('students_current_groups/<slug:gname>/',views.students_current_groups,name='students_current_groups'),
    path('pdftest/',views.pdftest,name='pdftest'),
    path('render/pdf/', views.Pdf.as_view(),name='pdf')
    # path('admin/', admin.site.urls),
]