from django.db import models
import ntpath
from django.utils.translation import gettext_lazy as _

class VideoFile(models.Model):

    def __str__(self):
        return self.filename

    class VideoStatus(models.TextChoices):
        NONE = 'NON', _('None')
        UPLOADED = 'UPL', _('Uploaded')
        READY_FOR_PROCESSING = 'RDY', _('Ready for Processing')
        PROCESSED = 'PRO', _('Processed')

    ct_id = models.CharField(max_length=20, null=True)
    site_id = models.CharField(max_length=20, null=True)
    date_start = models.DateTimeField('start date', null=True, blank=True)
    date_end = models.DateTimeField('end date', null=True, blank=True)
    filename = models.CharField(max_length=50, null=True)
    video_id = models.CharField(max_length=20, null=True)
    stratum = models.CharField(max_length=20, null=True, blank=True)
    rotation = models.CharField(max_length=20, null=True, blank=True)
    objects_detected = models.BooleanField(default=False)
    max_confidence = models.IntegerField(default=0)
    document = models.FileField(upload_to='', null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    fps_video = models.IntegerField(null=True, blank=True)
    fps_inference = models.IntegerField(null=True, blank=True)
    video_status = models.CharField(max_length=3, choices=VideoStatus.choices, default=VideoStatus.NONE,)
    inference_model = models.CharField(max_length=20, null=True, blank=True)
    max_objects_detected = models.IntegerField(null=True, blank=True)
    video_height = models.IntegerField(null=True, blank=True)
    video_width = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.filename is None:
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
    objects_detected = models.BooleanField()
    filename = models.CharField(max_length=255)
    max_confidence = models.IntegerField(default=0)

class Prediction(models.Model):
    video_frame = models.ForeignKey(VideoFrame, on_delete=models.CASCADE)
    coord_x = models.IntegerField(default=0)
    coord_y = models.IntegerField(default=0)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    confidence = models.IntegerField(default=0)
    pred_class = models.CharField(max_length=255)

