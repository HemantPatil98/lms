from django.shortcuts import render,HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin,xframe_options_exempt
from django.contrib.auth.models import Permission,Group
# Create your views here.
from .models import videos_watched_status
import os
from wsgiref.util import FileWrapper
import math
from lms.models import *
from lms import sheetsapi
from exam.models import *
def video(request,course):
    videos = "media/videos/courses/"+course
    thumbs = "media/videos/thumb/"+course
    # print(os.listdir(videos))
    # print(os.listdir(thumbs))
    videolist = []
    for v in os.listdir(videos):
        videolist.append(v.split(".")[0])

    watch = videos_watched_status.objects.filter(user=request.user,course=course)
    watch = [x.watched for x in watch]
    print((len(watch)/len(videolist))*100)
    per = math.floor((len(watch)/len(videolist))*100)
    return render(request,'video.html',{'course':course,'videos':videolist,'watched':watch,'per':per})

@xframe_options_sameorigin
def videoframe(request,course,video):
    return render(request,'videoframe.html',{'course':course,'video':video})


def v(request,course,video):
    # print(os.listdir())
    # thumb()
    videolink = "media/videos/courses/"+course+"/"+video+".mp4"
    file = FileWrapper(open(videolink, 'rb'))
    response = HttpResponse(file, content_type='video/mp4')
    response['Content-Disposition'] = 'attachment; filename=my_video.mp4'
    return response

def thumb(request):
    import cv2

    # Opens the Video file
    courses = "media/videos/courses/"
    thumbp = "media/videos/thumb/"
    for c in os.listdir(courses):
        for v in os.listdir(courses+c):
            vname = v.split('.')[0]
            video = courses+c+"/"+v
            t = thumbp+c+"/"+vname
            # print(video,t)
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

    return HttpResponse("Videos Synced Successfully")

def videopermissions(request,view='false'):
    print(request.POST)
    print(view)
    if request.method == 'POST':
        gname = request.POST['gname']
        # course = request.POST['cname']
        # cname = ''
        gp = Group.objects.get(name=gname)
        # gpinfo = ''

        # print(gp.id)
        gpinfo = groupsinfo.objects.get(group_id=gp.id)

        cname = request.POST['cname']

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
        # print(permissions)

        gp_permissions = gp.permissions.all()

        videolist = []

        videos = "media/videos/courses/" + cname
        # print(os.listdir(videos))
        for v in os.listdir(videos):
            videolist.append(v.split(".")[0])

        # print(videolist)
        # notice1 = ""
        try:
            notice1 = notice.objects.all().order_by('-generateddate')[0:5]
        except:
            notice1 = ""
        up = user_profile.objects.all().filter(user_id=request.user.id)[0]
        # print(memb)
        courses = course.objects.values_list('name', flat=True).distinct()
        print(gpinfo.enddate)
        return render(request, 'videopermissions.html',
                      {'gname': gp, 'permissions': Permission.objects.all()[68::],
                       'up': up, 'notice': notice1, 'vpermissions': videolist, 'courses': courses,
                       'gpinfo': gpinfo, 'gp_permissions': gp_permissions, 'view': view})
    groups = Group.objects.all()
    courses = course.objects.values_list('name', flat=True).distinct()

    # up = user_profile.objects.all().filter(user_id=request.user.id)[0]
    # return render(request, 'student/videopermissions.html', {'groups': groups, 'courses': courses, 'view': view})

    # return render(requet,'student/test.html')

    return render(request,'videopermissions.html',{'groups': groups, 'courses': courses, 'view': view})

def blank(request):
    return HttpResponse("")

def watched_video(request):
    course = request.GET['course']
    vid = request.GET['video']
    print(course,video)
    if len(videos_watched_status.objects.filter(user=request.user,course=course,watched=vid))==0:
        status = videos_watched_status(user=request.user,course=course,watched=vid)
        status.save()
    return HttpResponse("")

