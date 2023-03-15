from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import VideoFile
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .forms import UploadFileForm

#class IndexView(generic.View):
#    template_name = 'cameratrap/index.html'


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


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
