from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import VideoFile, VideoFrame
from django.shortcuts import get_object_or_404, render, redirect
from .forms import UploadFileForm
import logging
from .VideoProcessor import VideoProcessor
from cameratrap.tasks import process_video_async
from .CocoUtils import CocoUtils

class IndexView(generic.ListView):
    template_name = 'cameratrap/index.html'
    context_object_name = 'latest_video_files'
    model = VideoFile
    paginate_by = 25
    ordering = ['-uploaded_at']


class DetailView(generic.DetailView):
    model = VideoFile
    context_object_name = 'videoFile'
    template_name = 'cameratrap/detail.html'


def UploadFileView(request):
    form = UploadFileForm()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        files = request.FILES.getlist("document")
        if form.is_valid():
            for f in files:
                #new_video_file = form.save()
                logging.debug("file upload successful ")
                instance = VideoFile(document=f)
                instance.ct_id = form.cleaned_data.get("ct_id")
                instance.site_id = form.cleaned_data.get("site_id")
                instance.video_status = VideoFile.VideoStatus.UPLOADED
                instance.save()

                logging.debug(f"processing video in the background with pkid: {instance.pk}")
                process_video_async.delay(instance.pk)
            return redirect('cameratrap:index')
    else:
        form = UploadFileForm()
    return render(request, 'cameratrap/upload.html', {
        'form': form
    })


def SyncProcessVideoView(request, video_pkid):
    print("Sync SyncProcessVideoView Called")
    video_file = VideoFile.objects.get(pk=video_pkid)
    vp = VideoProcessor(video_file)
    vp.processVideo()
    print("Sync SyncProcessVideoView Completed")
    return HttpResponseRedirect(reverse('cameratrap:detail', args=(video_pkid,)))


def ASyncProcessVideoView(request, video_pkid):
    print("ASync ASyncProcessVideoView Called")
    process_video_async.delay(video_pkid)
    print("ASync ASyncProcessVideoView Completed")
    return HttpResponseRedirect(reverse('cameratrap:detail', args=(video_pkid,)))


def CocoVideoFrameView(request, video_pkid, video_frame_pkid):
    print("CocoVideoFrameView Called")
    video_frame = VideoFrame.objects.get(pk=video_frame_pkid)
    coco_util = CocoUtils(video_frame)
    coco_util.process_frame_to_coco()
    print("CocoVideoFrameView Completed")
    return HttpResponseRedirect(reverse('cameratrap:detail', args=(video_pkid,)))