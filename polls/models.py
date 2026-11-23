
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Poll(models.Model):
    question = models.CharField(max_length=255)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='polls'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question

    @property
    def is_open(self):
        return self.closes_at > timezone.now()

    @property
    def total_votes(self):
        return Vote.objects.filter(choice__poll=self).count()

    def get_results(self):
        total = self.total_votes
        results = []

        choices = self.choices.annotate(
            vote_count=models.Count('votes')
        )

        for choice in choices:
            percent = (
                round(choice.vote_count * 100 / total, 1)
                if total else 0
            )

            results.append({
                'text': choice.text,
                'votes': choice.vote_count,
                'percent': percent,
            })

        return results


class Choice(models.Model):
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='choices'
    )

    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Vote(models.Model):
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='votes'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='votes'
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False) |
                    models.Q(session_key__isnull=False)
                ),
                name='vote_has_user_or_session'
            )
        ]

    def __str__(self):
        return f"Vote: {self.choice.text}"
