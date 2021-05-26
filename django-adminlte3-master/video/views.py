from django.shortcuts import render,HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin,xframe_options_exempt
from django.contrib.auth.models import Permission
# Create your views here.
from .models import videos_watched_status
import os
from wsgiref.util import FileWrapper
import math
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

def videopermissions(request):
    return render(request,'videopermissions.html')

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

