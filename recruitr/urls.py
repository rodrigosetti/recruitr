"""recruitr URL Configuration """

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import logout_then_login

from candidates.views import update_candidate
from coding_problems.views import coding_problem, CodingProblemListView
from .admin import admin_site

urlpatterns = [
    url(r'^admin/', admin_site.urls),
    url('', include('social_django.urls', namespace='social')),

    url(r'^$', TemplateView.as_view(template_name='index.html')),

    url(
        r'^challenges?/(?P<slug>[-\w]+)/$',
        coding_problem,
        name='coding-problem-detail'),

    url(
        r'^challenges/$',
        CodingProblemListView.as_view(),
        name='coding-problem-list'),

    url(r'^accounts/login/$', TemplateView.as_view(template_name='login.html')),
    url(r'^accounts/profile/$', update_candidate, name='account-profile'),

    url(r"^accounts/logout/$", logout_then_login, name="logout"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
