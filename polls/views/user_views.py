
from django.shortcuts import render, redirect
from ..forms.user_form import RegisterForm
from django.contrib.auth.views import LoginView, LogoutView


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'polls/users/register.html', {
        'form': form
    })
