from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import VideoFile
from django.shortcuts import get_object_or_404, render, redirect
from .forms import UploadFileForm
import logging
from .VideoProcessor import VideoProcessor
import ntpath

class IndexView(generic.ListView):
    template_name = 'cameratrap/index.html'
    context_object_name = 'latest_video_files'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return VideoFile.objects.order_by('-date_start')[:5]


class DetailView(generic.DetailView):
    model = VideoFile
    context_object_name = 'videoFile'
    template_name = 'cameratrap/detail.html'


def UploadFileView(request):
    form = UploadFileForm()
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            new_video_file = form.save()
            logging.debug("file upload successful ")
            vp = VideoProcessor(new_video_file)
            vp.processVideo()
            return redirect('cameratrap:process', new_video_file.pk)
    else:
        form = UploadFileForm()
    return render(request, 'cameratrap/upload.html', {
        'form': form
    })


def AsyncProcessVideoView(request, video_pkid):
    video_file = VideoFile.objects.get(pk=video_pkid)
    vp = VideoProcessor(video_file)
    vp.processVideo()

    # return HttpResponse("Non-blocking HTTP request (via sync_to_async)")
    return HttpResponseRedirect(reverse('cameratrap:detail', args=(video_pkid,)))
