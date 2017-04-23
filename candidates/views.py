from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from .forms import CandidateForm


@login_required
def update_candidate(request):
    if request.method == 'POST':
        print(request.FILES)
        user_form = UserForm(request.POST, instance=request.user)
        candidate_form = CandidateForm(request.POST, request.FILES,
                                       instance=request.user.candidate)
        if user_form.is_valid() and candidate_form.is_valid():
            user_form.save()
            candidate_form.save()
            messages.success(request,
                             _('Your profile was successfully updated!'))
            return redirect('account-profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        candidate_form = CandidateForm(instance=request.user.candidate)
    return render(request, 'profile.html', {
        'user_form': user_form,
        'candidate_form': candidate_form
    })
