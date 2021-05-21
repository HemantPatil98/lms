from django.shortcuts import render,HttpResponse
from django.views.decorators.clickjacking import xframe_options_sameorigin,xframe_options_exempt
# Create your views here.
import os
from wsgiref.util import FileWrapper
def video(request,course):
    videos = "media/videos/courses/"+course
    thumbs = "media/videos/thumb/"+course
    # print(os.listdir(videos))
    # print(os.listdir(thumbs))
    videolist = []
    for v in os.listdir(videos):
        videolist.append(v.split(".")[0])

    return render(request,'video.html',{'course':course,'videos':videolist})

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
            video = courses+c+"/"+v
            t = thumbp+c+"/"+v.split(".")[0]
            # print(video,t)
            cap = cv2.VideoCapture(video)

            ret, frame = cap.read()
            cv2.imwrite(t + '.jpg', frame)

            cap.release()
            cv2.destroyAllWindows()

    return HttpResponse("")

def videopermissions(request):
    return render(request,'videopermissions.html')