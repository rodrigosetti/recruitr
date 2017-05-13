from .forms import CodeSubmissionForm
from .models import CodingProblem, CodeSubmission
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.views.generic import ListView
from .tasks import judge_code_submission


class CodingProblemListView(ListView):
    model = CodingProblem

    def get_queryset(self):
        return CodingProblem.objects.filter(public=True)


@login_required
def coding_problem(request, slug):
    problem = CodingProblem.objects.get(slug=slug)

    if request.method == 'POST':
        submission = CodeSubmission(
            problem=problem,
            user=request.user)
        submission_form = CodeSubmissionForm(request.POST, instance=submission)
        if submission_form.is_valid():
            submission_form.save()

            # send task
            judge_code_submission.delay(submission.id)

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

        latest_submission = problem.user_submissions(request.user).earliest()
        if latest_submission:
            submission_form.initial["language"] = latest_submission.language
            submission_form.initial["code"] = latest_submission.code

        return render(request, 'candidates/codingproblem_detail.html', {
            'problem': problem,
            'submission_form': submission_form,
            'examples': problem.examples,
            'submissions': problem.user_submissions(request.user)
        })
