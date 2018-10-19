import django.contrib.auth.views
from django.conf.urls import url

import apps.users.views as views

urlpatterns = [
    url(
        r'^accounts/profile/',
        views.ProfileView.as_view(),
        name="profile"
    ),

    url(
        r'^logout/$',
        django.contrib.auth.views.LogoutView.as_view(),
        name="logout"
    ),
]
