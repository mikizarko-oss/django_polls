
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ..forms.poll_form import PollForm
from ..forms.vote_form import VoteForm
from ..models import Poll, Choice, Vote


def home(request):
    polls = Poll.objects.select_related('author').all()

    return render(request, 'polls/polls/home.html', {
        'polls': polls
    })

def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    visit_count = request.session.get('poll_visits', {}).get(str(poll.id), 0)

    if request.user.is_authenticated:
        already_voted = Vote.objects.filter(
            choice__poll=poll,
            user=request.user
        ).exists()
    else:
        already_voted = False

        if request.session.session_key:
            already_voted = Vote.objects.filter(
                choice__poll=poll,
                session_key=request.session.session_key,
                user__isnull=True
            ).exists()

    # Ako je korisnik već glasao ili je anketa zatvorena,
    # prikazujemo rezultate.
    if already_voted or not poll.is_open:
        return render(request, 'polls/votes/results.html', {
            'poll': poll,
            'results': poll.get_results(),
            'visit_count': visit_count
        })

    form = VoteForm(poll=poll)

    return render(request, 'polls/polls/detail.html', {
        'poll': poll,
        'form': form,
        'already_voted': already_voted,
        'visit_count': visit_count
    })


@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollForm(request.POST)

        if form.is_valid():
            poll = Poll.objects.create(
                question=form.cleaned_data['question'],
                closes_at=form.cleaned_data['closes_at'],
                author=request.user
            )

            choices = form.cleaned_data['choices']

            for choice_text in choices:
                Choice.objects.create(
                    poll=poll,
                    text=choice_text
                )

            return redirect('home')

    else:
        form = PollForm()

    return render(request, 'polls/polls/create.html', {
        'form': form
    })
