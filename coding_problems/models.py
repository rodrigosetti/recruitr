from django.db import models
from django.contrib.auth.models import User


class CodingProblem(models.Model):

    slug = models.SlugField()

    public = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    statement = models.TextField()
    specification = models.TextField()

    def __str__(self):
        return self.title

    @property
    def examples(self):
        return self.inputoutput_set.filter(example=True)

    def user_submissions(self, user):
        return self.codesubmission_set.filter(user=user).order_by('submission_time').reverse()


class InputOutput(models.Model):
    problem = models.ForeignKey(CodingProblem)
    example = models.BooleanField(default=False)
    input = models.TextField()
    output = models.TextField()

    def __str__(self):
        return str(self.problem) + " case" + (" (example)" if self.example else "")


class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = (
        ("PY", "Python"),
        ("JS", "Javascript (Node)")
    )

    STATUS_CHOICES = (
        ("C", "Canceled"),
        ("Q", "Queued"),
        ("R", "Running"),
        ("S", "Success"),
        ("F", "Failure"),
        ("L", "Output too large"),
        ("E", "Error"),
        ("T", "Timeout"),
    )

    problem = models.ForeignKey(CodingProblem)
    user = models.ForeignKey(User)
    submission_time = models.DateTimeField(auto_now_add=True)

    code = models.TextField()
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)

    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default="Q")
    error_output = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.problem} submission ({self.status})"

    class Meta:
        get_latest_by = "submission_time"
