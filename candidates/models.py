from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


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
    phone = models.CharField(max_length=50, unique=True)
    referrer = models.CharField(max_length=100, blank=True, null=True)

    resume = models.FileField(blank=True, null=True, upload_to="uploads/%Y/%m/%d/")
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
