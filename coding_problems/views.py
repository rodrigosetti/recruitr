from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .tasks import judge_code_submission
from .forms import CodeSubmissionForm
from .models import CodingProblem, CodeSubmission


class CodingProblemListView(ListView):
    model = CodingProblem

    def get_queryset(self):
        return CodingProblem.objects.filter(public=True)


def coding_problem(request, slug):
    problem = CodingProblem.objects.get(slug=slug)
    user = request.user

    if request.method == 'POST':
        if not user.is_authenticated:
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(settings.LOGIN_URL)
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            return redirect_to_login(path,
                                     resolved_login_url,
                                     REDIRECT_FIELD_NAME)

        submission = CodeSubmission(
            problem=problem,
            user=user)
        submission_form = CodeSubmissionForm(request.POST, instance=submission)
        if submission_form.is_valid():
            submission_form.save()

            # send task
            judge_code_submission.delay(submission.id)

            # keep only the top 10 submissions
            for n, s in enumerate(CodeSubmission.objects.filter(user=user, problem=problem).order_by("submission_time").reverse()):
                if n >= 10:
                    s.delete()

            messages.success(request,
                             _('Your code was successfully submitted'))
            return redirect('coding-problem-detail', slug)
        else:
            messages.success(request,
                             _('Your code was successfully submitted'))
            messages.error(request,
                           _('Please correct the error below.'))
    else:
        submission_form = CodeSubmissionForm()

        if user.is_authenticated:
            submissions = problem.user_submissions(user)
            try:
                latest_submission = submissions.earliest()
                submission_form.initial["language"] = latest_submission.language
                submission_form.initial["code"] = latest_submission.code
            except CodeSubmission.DoesNotExist:
                pass
        else:
            submissions = []

        return render(request, 'candidates/codingproblem_detail.html', {
            'problem': problem,
            'submission_form': submission_form,
            'examples': problem.examples,
            'submissions': submissions
        })
