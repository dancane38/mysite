from django.contrib import admin

from .models import VideoFile, VideoFrame, Prediction, Observation

class VideoFrameInline(admin.TabularInline):
    model = VideoFrame
    extra = 3

class ObservationInline(admin.TabularInline):
    model = Observation
    extra = 3

class VideoFileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['ct_id', 'site_id', 'filename', 'video_id']}),
        ('Dates', {'fields': ['date_start', 'date_end'], 'classes': ['collapse']}),
        ('Monkeys Detected', {'fields': ['objects_detected', 'max_confidence']}),
    ]
    inlines = [VideoFrameInline, ObservationInline]
    list_display = ('filename', 'date_start', 'date_end', 'objects_detected', 'max_confidence')
    list_filter = ['objects_detected']
    search_fields = ['filename']



admin.site.register(VideoFile, VideoFileAdmin)
