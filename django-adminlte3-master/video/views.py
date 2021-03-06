from django.shortcuts import render,HttpResponse,redirect
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth.models import Permission,Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from wsgiref.util import FileWrapper
import math
import os

from .models import videos_watched_status
from lms.models import *
from exam.models import *

# Create your views here.

video_key = []
video_request_counter = 0
def randomstring():
    import secrets
    import string

    N = 7
    res = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(N))

    return str(res)
###
@login_required(login_url='')
def video(request,course):
    videos = "media/videos/courses/"+course
    thumbs = "media/videos/thumb/"+course
    videolist = []
    for v in os.listdir(videos):
        videolist.append(v.split(".")[0])

    videolist.sort()

    watch = videos_watched_status.objects.filter(user=request.user,course=course)
    watch = [x.watched for x in watch]
    if len(videolist):
        per = math.floor((len(watch)/len(videolist))*100)
    else:
        per = 0

    global video_key
    key = randomstring()
    video_key = key

    return render(request,'video.html',{'course':course,'videos':videolist,'watched':watch,'per':per,'key':key})

###
@xframe_options_sameorigin
@login_required(login_url='')
def videoframe(request,course,video,key):

    # if key in video_key:
    return render(request,'videoframe.html',{'course':course,'video':video,'key':key})
    # else:
    #     return HttpResponse("Sorry Bad request")

###
@login_required(login_url='')
def v(request,course,video,key):
    global video_key,video_request_counter

    if key == video_key:
        # video_request_counter +=1
        # video_key = ""
        if len(videos_watched_status.objects.filter(user=request.user, course=course, watched=video)) == 0:
            status = videos_watched_status(user=request.user, course=course, watched=video)
            status.save()

        videolink = "media/videos/courses/"+course+"/"+video+".mp4"

        file = FileWrapper(open(videolink, 'rb'))
        response = HttpResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = 'attachment; filename=my_video.mp4'
        return response
    else:
        # video_key = ""
        video_request_counter = 0
        return HttpResponse("Sorry Bad request")


###
@login_required(login_url='')
def video_sync(request):
    import cv2

    # Opens the Video file
    courses = "media/videos/courses/"
    thumbp = "media/videos/thumb/"
    for c in os.listdir(courses):
        for v in os.listdir(courses+c):
            vname = v.split('.')[0]
            video = courses+c+"/"+v
            t = thumbp+c+"/"+vname
            cap = cv2.VideoCapture(video)

            ret, frame = cap.read()
            cv2.imwrite(t + '.jpg', frame)

            cap.release()
            cv2.destroyAllWindows()

            try:
                p = Permission(content_type_id=6,codename=vname,name=vname)
                p.save()
            except:
                pass

    messages.success(request,"Videos Synced Successfully")
    return redirect('index')

###
@login_required(login_url='')
def videopermissions(request,view='false'):
    if request.method == 'POST':
        gname = request.POST['gname']
        gp = Group.objects.get(name=gname)
        gpinfo = groupsinfo.objects.get(group_id=gp.id)

        # cname = request.POST['cname']

        if request.POST.getlist('videopermission'):
            for p in gp.permissions.all():
                if p.name not in request.POST.getlist('videopermission'):
                    gp.permissions.remove(p.id)
            for p in request.POST.getlist('videopermission'):
                p = Permission.objects.get(name=p)
                if p not in gp.permissions.all():
                    gp.permissions.add(p)

            permissions = {'video': request.POST.get('pervideo'), 'exam': request.POST.get('perexam'),
                           'notes': request.POST.get('pernotes')}
            for p in permissions:
                if permissions.get(p) == 'on':
                    gp.permissions.add(Permission.objects.get(name=p))
                else:
                    gp.permissions.remove(Permission.objects.get(name=p))

        gp_permissions = gp.permissions.all()

        videolist = []

        videos = "media/videos/courses/" + gpinfo.course
        if os.path.exists(videos):
            for v in os.listdir(videos):
                videolist.append(v.split(".")[0])


        up = user_profile.objects.all().filter(user_id=request.user.id)[0]

        courses = course.objects.values_list('name', flat=True).distinct()
        return render(request, 'videopermissions.html',
                      {'gname': gp, 'permissions': Permission.objects.all()[68::],'up': up, 'vpermissions': videolist,
                       'courses': courses,'gpinfo': gpinfo, 'gp_permissions': gp_permissions, 'view': view})
    groups = Group.objects.all()
    courses = course.objects.values_list('name', flat=True).distinct()

    return render(request,'videopermissions.html',{'groups': groups, 'courses': courses, 'view': view})


###
@login_required(login_url='')
def watched_video(request):
    course = request.GET['course']
    vid = request.GET['video']
    if len(videos_watched_status.objects.filter(user=request.user,course=course,watched=vid))==0:
        status = videos_watched_status(user=request.user,course=course,watched=vid)
        status.save()
    return HttpResponse("")

def getnewvideokey(request):
    global video_key
    key = randomstring()
    video_key = key
    return HttpResponse(str(key))
