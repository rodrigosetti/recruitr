import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def determine_upload_location(instance, filename):
    """
    Determine where files are going to be uploaded
    Args
      instance: Candidate user instance
      filename: filename of resumes being uploaded
    Return
      path of the resume
    """
    _, extension = os.path.splitext(filename)
    return os.path.join("resumes", instance.user.username + extension)


class Candidate(models.Model):
    LEVEL_CHOICES = (
        ("IN", "Intern"),
        ("NG", "New grad"),
        ("CL", "Career level"),
        ("SR", "Senior"),
        ("PR", "Principal"),
    )
    STATUS_CHOICES = (
        ("NEW", "New"),
        ("PHO", "Phone Screening"),
        ("ON", "Onsite Interview"),
        ("OF", "Offer"),
        ("CL", "Closed"),
        ("AC", "Accepted"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default="NEW")
    phone = models.CharField(max_length=50)
    referrer = models.CharField(max_length=100, blank=True, null=True)

    resume = models.FileField(blank=True,
                              null=True,
                              upload_to=determine_upload_location,
                              validators=[FileExtensionValidator(['pdf', 'txt', 'doc', 'docx'])])
    resume_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name()

    def name(self):
        n = []
        if self.user.first_name: n.append( self.user.first_name )
        if self.user.last_name: n.append( self.user.last_name )
        return " ".join(n) if n else str(self.user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_candidate(sender, instance, created, **kwargs):
    if created:
        Candidate.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_candidate(sender, instance, **kwargs):
    instance.candidate.save()
