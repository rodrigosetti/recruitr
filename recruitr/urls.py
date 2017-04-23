"""recruitr URL Configuration """

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from candidates.views import update_candidate
from coding_problems.views import coding_problem, CodingProblemListView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),

    url(r'^$', TemplateView.as_view(template_name='index.html')),

    url(
        r'^problems?/(?P<slug>[-\w]+)/$',
        coding_problem,
        name='coding-problem-detail'),

    url(
        r'^problems/$',
        login_required(CodingProblemListView.as_view()),
        name='coding-problem-list'),

    url(r'^accounts/login/$', TemplateView.as_view(template_name='login.html')),
    url(r'^accounts/profile/$', update_candidate, name='account-profile'),
]
