
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views.poll_views import create_poll, home, poll_detail
from .views.user_views import register
from .views.vote_views import cast_vote


urlpatterns = [

    path('', home, name='home'),
    path('polls/create/', create_poll, name='create_poll'),
    path('polls/<int:poll_id>/', poll_detail, name='poll_detail'),
    path('polls/<int:poll_id>/vote/', cast_vote, name='cast_vote'),

    path('register/', register, name='register'),
    path(
        'login/',
        LoginView.as_view(
            template_name='polls/users/login.html'
        ),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),

]
