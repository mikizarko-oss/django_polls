
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from .models import Poll, Choice, Vote


class PollModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.poll = Poll.objects.create(
            question='Koji jezik preferirate?',
            author=self.user,
            closes_at=timezone.now() + timedelta(days=7)
        )

        self.choice_1 = Choice.objects.create(
            poll=self.poll,
            text='Python'
        )

        self.choice_2 = Choice.objects.create(
            poll=self.poll,
            text='JavaScript'
        )

    def test_poll_is_open(self):
        self.assertTrue(self.poll.is_open)

    def test_poll_is_closed(self):
        self.poll.closes_at = timezone.now() - timedelta(days=1)
        self.poll.save()

        self.assertFalse(self.poll.is_open)

    def test_poll_total_votes(self):
        Vote.objects.create(
            choice=self.choice_1,
            user=self.user
        )

        self.assertEqual(self.poll.total_votes, 1)

    def test_poll_results(self):
        Vote.objects.create(
            choice=self.choice_1,
            user=self.user
        )

        results = self.poll.get_results()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['votes'], 1)
        self.assertEqual(results[0]['percent'], 100.0)

    def test_choice_belongs_to_poll(self):
        self.assertEqual(self.choice_1.poll, self.poll)

class VoteViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='voter',
            password='testpassword123'
        )

        self.poll = Poll.objects.create(
            question='Koji jezik preferirate?',
            author=self.user,
            closes_at=timezone.now() + timedelta(days=7)
        )

        self.choice_1 = Choice.objects.create(
            poll=self.poll,
            text='Python'
        )

        self.choice_2 = Choice.objects.create(
            poll=self.poll,
            text='JavaScript'
        )

        self.vote_url = f'/polls/{self.poll.id}/vote/'

    def test_authenticated_user_can_vote(self):
        self.client.login(
            username='voter',
            password='testpassword123'
        )

        response = self.client.post(
            self.vote_url,
            {'choice': self.choice_1.id}
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Vote.objects.filter(
                choice__poll=self.poll,
                user=self.user
            ).count(),
            1
        )

    def test_authenticated_user_cannot_vote_twice(self):
        self.client.login(
            username='voter',
            password='testpassword123'
        )

        self.client.post(
            self.vote_url,
            {'choice': self.choice_1.id}
        )

        self.client.post(
            self.vote_url,
            {'choice': self.choice_2.id}
        )

        self.assertEqual(
            Vote.objects.filter(
                choice__poll=self.poll,
                user=self.user
            ).count(),
            1
        )

    def test_anonymous_user_can_vote(self):
        response = self.client.post(
            self.vote_url,
            {'choice': self.choice_1.id}
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Vote.objects.filter(
                choice__poll=self.poll,
                user__isnull=True
            ).count(),
            1
        )

    def test_anonymous_user_cannot_vote_twice(self):
        self.client.post(
            self.vote_url,
            {'choice': self.choice_1.id}
        )

        self.client.post(
            self.vote_url,
            {'choice': self.choice_2.id}
        )

        self.assertEqual(
            Vote.objects.filter(
                choice__poll=self.poll,
                user__isnull=True
            ).count(),
            1
        )

    def test_closed_poll_rejects_vote(self):
        self.poll.closes_at = timezone.now() - timedelta(days=1)
        self.poll.save()

        response = self.client.post(
            self.vote_url,
            {'choice': self.choice_1.id}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Vote.objects.filter(choice__poll=self.poll).count(),
            0
        )

class PollPageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            password='testpassword123'
        )

        self.poll = Poll.objects.create(
            question='Koji jezik preferirate?',
            author=self.user,
            closes_at=timezone.now() + timedelta(days=7)
        )

        self.choice_1 = Choice.objects.create(
            poll=self.poll,
            text='Python'
        )

        self.choice_2 = Choice.objects.create(
            poll=self.poll,
            text='JavaScript'
        )

        self.detail_url = f'/polls/{self.poll.id}/'

    def test_poll_detail_page_loads(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.poll.question)

    def test_nonexistent_poll_returns_404(self):
        response = self.client.get('/polls/99999/')

        self.assertEqual(response.status_code, 404)

    def test_closed_poll_displays_results(self):
        self.poll.closes_at = timezone.now() - timedelta(days=1)
        self.poll.save()

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'polls/votes/results.html'
        )

    def test_voted_user_sees_results(self):
        Vote.objects.create(
            choice=self.choice_1,
            user=self.user
        )

        self.client.login(
            username='author',
            password='testpassword123'
        )

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'polls/votes/results.html'
        )
class PollVisitMiddlewareTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='visitor',
            password='testpassword123'
        )

        self.poll = Poll.objects.create(
            question='Test anketa',
            author=self.user,
            closes_at=timezone.now() + timedelta(days=7)
        )

        Choice.objects.create(
            poll=self.poll,
            text='Python'
        )

        Choice.objects.create(
            poll=self.poll,
            text='JavaScript'
        )

        self.url = reverse(
            'poll_detail',
            args=[self.poll.id]
        )

    def test_visit_count_increases(self):
        self.client.get(self.url)

        session = self.client.session
        visits = session['poll_visits']

        self.assertEqual(visits[str(self.poll.id)], 1)

        self.client.get(self.url)

        session = self.client.session
        visits = session['poll_visits']

        self.assertEqual(visits[str(self.poll.id)], 2)

    def test_different_polls_have_separate_visit_counts(self):
        second_poll = Poll.objects.create(
            question='Druga anketa',
            author=self.user,
            closes_at=timezone.now() + timedelta(days=7)
        )

        Choice.objects.create(poll=second_poll, text='Da')
        Choice.objects.create(poll=second_poll, text='Ne')

        self.client.get(self.url)

        second_url = reverse(
            'poll_detail',
            args=[second_poll.id]
        )

        self.client.get(second_url)

        visits = self.client.session['poll_visits']

        self.assertEqual(visits[str(self.poll.id)], 1)
        self.assertEqual(visits[str(second_poll.id)], 1)
