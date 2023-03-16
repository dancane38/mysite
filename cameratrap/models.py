from django.db import models

class VideoFile(models.Model):

    def __str__(self):
        return self.filename

    ct_id = models.CharField(max_length=20, null=True)
    site_id = models.CharField(max_length=20, null=True)
    date_start = models.DateTimeField('start date', null=True)
    date_end = models.DateTimeField('end date', null=True)
    filename = models.CharField(max_length=50, null=True)
    video_id = models.CharField(max_length=20, null=True)
    stratum = models.CharField(max_length=20, null=True)
    rotation = models.CharField(max_length=20, null=True)
    objects_detected = models.BooleanField(default=False)
    max_confidence = models.IntegerField(default=0)
    document = models.FileField(upload_to='media/', null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)

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

