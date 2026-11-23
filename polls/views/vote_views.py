
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from ..models import Poll, Vote
from ..forms.vote_form import VoteForm


def cast_vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if request.method != 'POST':
        return redirect('poll_detail', poll_id=poll.id)

    if not poll.is_open:
        messages.error(request, 'Ova anketa je zatvorena.')
        return redirect('poll_detail', poll_id=poll.id)

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        already_voted = Vote.objects.filter(
            choice__poll=poll,
            user=request.user
        ).exists()
    else:
        already_voted = Vote.objects.filter(
            choice__poll=poll,
            session_key=request.session.session_key,
            user__isnull=True
        ).exists()

    if already_voted:
        messages.warning(request, 'Već ste glasali u ovoj anketi.')
        return redirect('poll_detail', poll_id=poll.id)

    form = VoteForm(request.POST, poll=poll)

    if form.is_valid():
        Vote.objects.create(
            choice=form.cleaned_data['choice'],
            user=request.user if request.user.is_authenticated else None,
            session_key=None if request.user.is_authenticated else request.session.session_key
        )

        messages.success(request, 'Vaš glas je uspešno sačuvan.')
        return redirect('poll_detail', poll_id=poll.id)

    return redirect('poll_detail', poll_id=poll.id)
