from django.db import models
from django.utils.translation import ugettext as _
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
    input = models.TextField(blank=True, null=False)
    output = models.TextField(blank=True, null=False)

    times = models.PositiveSmallIntegerField(default=1,
                                             help_text=_("Number of times to evaluate this case, applicable only if input or output are dynamic"))

    dynamic_input = models.BooleanField(default=False,
                                        help_text=_("if input is dynamic, it should be a Python script that will generate the actual input"))
    dynamic_output = models.BooleanField(default=False,
                                         help_text=_("if output is dynamic, it should be the correct solution implemented in Python"))

    def __str__(self):
        return str(self.problem) + " case" + (" (example)" if self.example else "")


class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = (
        ("C",  "C"),
        ("CP", "C++"),
        ("HA", "Haskell"),
        ("JA", "Java"),
        ("JS", "Javascript (Node)"),
        ("PE", "Perl"),
        ("PH", "PHP"),
        ("PY", "Python"),
        ("RA", "Racket"),
        ("RU", "Ruby"),
        ("SC", "Scala"),
        ("SH", "Shell (Bash)"),
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
        return "{} submission ({})".format(self.problem, self.status)

    class Meta:
        get_latest_by = "submission_time"
