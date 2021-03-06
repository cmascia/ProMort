from django.db import models
from django.contrib.auth.models import User


class Case(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    import_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Case %s' % self.id

    def _get_slides_list(self):
        return self.slide_set.all()
    slides = property(_get_slides_list)


class Slide(models.Model):
    STAINING = (
        ('HE', 'H&E'),
        ('TRI', 'Trichrome')
    )
    id = models.CharField(max_length=25, primary_key=True)
    case = models.ForeignKey(Case, on_delete=models.PROTECT,
                             blank=False, related_name='slides')
    import_date = models.DateTimeField(auto_now_add=True)
    omero_id = models.IntegerField(blank=True, null=True,
                                   default=None)
    image_type = models.CharField(max_length=15, blank=True,
                                  null=True)
    image_microns_per_pixel = models.FloatField(default=0.0)
    staining = models.CharField(
        max_length=5, choices=STAINING, blank=True,
        null=True, default=None
    )

    def __unicode__(self):
        return 'Slide %s [img type: %s --- OMERO id: %r]' % (self.id, self.image_type,
                                                             self.omero_id)


class SlideQualityControl(models.Model):
    from reviews_manager.models import ROIsAnnotationStep

    NOT_ADEQUACY_REASONS_CHOICES = (
        ('BAD_TILES', 'Bad tiles stitching'),
        ('BAD_FOCUS', 'Non uniform focus'),
        ('DMG_SMP', 'Damaged samples'),
        ('OTHER', 'Other (see notes)')
    )
    slide = models.ForeignKey(Slide, on_delete=models.PROTECT,
                              blank=False, unique=False)
    rois_annotation_step = models.OneToOneField(ROIsAnnotationStep, on_delete=models.PROTECT,
                                                blank=False, unique=True,
                                                related_name='slide_quality_control')
    adequate_slide = models.BooleanField(blank=False)
    not_adequacy_reason = models.CharField(
        max_length=10, choices=NOT_ADEQUACY_REASONS_CHOICES,
        blank=True, null=True, default=None
    )
    notes = models.TextField(blank=True, null=True)
    reviewer = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    acquisition_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        if self.adequate_slide:
            return 'Adequate'
        else:
            return 'Not adequate (reason: %s)' % self.get_not_adequacy_reason_display()
