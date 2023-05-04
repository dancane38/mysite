from django.db import models
import ntpath
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

class VideoFile(models.Model):

    def __str__(self):
        return self.filename

    class VideoStatus(models.TextChoices):
        NONE = 'NON', _('None')
        UPLOADED = 'UPL', _('Uploaded')
        PROCESSING = 'PRO', _('Processing')
        REPROCESS = 'REP', _('Flagged for Reprocessing')
        COMPLETED = 'CPL', _('Completed')

    def video_status_readable(self) -> VideoStatus:
        # Get value from choices enum
        return self.VideoStatus(self.video_status).label

    def fn_video_location(instance, filename):
        return '/'.join(['videos', slugify(instance.site_id), slugify(instance.ct_id), filename])

    ct_id = models.CharField(max_length=20)
    site_id = models.CharField(max_length=20)
    date_start = models.DateTimeField('start date', null=True, blank=True)
    date_end = models.DateTimeField('end date', null=True, blank=True)
    filename = models.CharField(max_length=50, null=False)
    video_id = models.CharField(max_length=20, null=True)
    stratum = models.CharField(max_length=20, null=True, blank=True)
    rotation = models.CharField(max_length=20, null=True, blank=True)
    objects_detected = models.BooleanField(default=False)
    max_confidence = models.IntegerField(default=0)
    document = models.FileField(upload_to=fn_video_location, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    fps_video = models.IntegerField(null=True, blank=True)
    fps_inference = models.IntegerField(null=True, blank=True)
    video_status = models.CharField(max_length=3, choices=VideoStatus.choices, default=VideoStatus.NONE,)
    inference_model = models.CharField(max_length=20, null=True, blank=True)
    max_objects_detected = models.IntegerField(null=True, blank=True)
    video_height = models.IntegerField(null=True, blank=True)
    video_width = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.filename is None or self.filename is '':
            self.filename = ntpath.basename(self.document.path)
        if self.max_objects_detected is not None and int(self.max_objects_detected) > 0:
            self.objects_detected = True

        super(VideoFile, self).save(*args, **kwargs)


class Observation(models.Model):
    video_file = models.ForeignKey(VideoFile, on_delete=models.CASCADE)
    ob_date = models.DateTimeField('observation date')
    ob_class = models.CharField(max_length=50)
    ob_order = models.CharField(max_length=50)
    ob_genus = models.CharField(max_length=50)
    ob_species = models.CharField(max_length=50)
    ob_common_name = models.CharField(max_length=255)
    ob_count = models.IntegerField(default=0)
    ob_quality = models.IntegerField(default=0)
    ob_notes = models.CharField(max_length=4000)
    ob_observer = models.CharField(max_length=50)
    ob_observer_2 = models.CharField(max_length=50)

class VideoFrame(models.Model):
    video_file = models.ForeignKey(VideoFile, on_delete=models.CASCADE)
    frame_number = models.IntegerField(default=0)
    objects_detected = models.IntegerField(null=True, blank=True)
    filename = models.FileField()
    max_confidence = models.IntegerField(default=0)

    def videoTimestamp(self):
        return int(self.frame_number / self.video_file.fps_inference)

    def videoTimestampFormatted(self):
        video_timestamp = self.videoTimestamp()
        seconds = video_timestamp % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

class Prediction(models.Model):
    video_frame = models.ForeignKey(VideoFrame, on_delete=models.CASCADE)
    coord_top = models.IntegerField(default=0)
    coord_left = models.IntegerField(default=0)
    coord_bottom = models.IntegerField(default=0)
    coord_right = models.IntegerField(default=0)
    confidence = models.IntegerField(default=0)
    pred_class = models.CharField(max_length=255)

