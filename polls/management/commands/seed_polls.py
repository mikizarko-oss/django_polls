
import random

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from faker import Faker

from polls.models import Poll, Choice, Vote


fake = Faker()


QUESTIONS = [
    'Koji programski jezik najviše koristite?',
    'Da li koristite Django?',
    'Koji frontend framework preferirate?',
    'Da li radite od kuće?',
    'Koliko često učite nove tehnologije?',
    'Da li koristite Python na poslu?',
    'Koji editor koristite za programiranje?',
    'Koliko godina programirate?',
    'Da li koristite Git svakodnevno?',
    'Koja baza podataka vam je omiljena?',
]

ANSWERS = [
    'React',
    'Python',
    'JavaScript',
    'Django',
    'Next.js',
    'Node.js',
    'PHP',
    'Vue',
    'Angular',
    'Laravel',
    'PostgreSQL',
    'MySQL',
]


class Command(BaseCommand):

    help = 'Generiše test ankete, odgovore i glasove'

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            help='Broj anketa koje treba generisati'
        )

    def handle(self, *args, **options):

        count = options['count']

        if count < 1:
            self.stdout.write(
                self.style.ERROR(
                    'Broj anketa mora biti veći od 0.'
                )
            )
            return

        users = list(User.objects.all())

        if not users:
            self.stdout.write(
                self.style.ERROR(
                    'Prvo kreiraj korisnika.'
                )
            )
            return

        created_votes = 0
        created_registered_votes = 0
        created_anonymous_votes = 0

        with transaction.atomic():

            for _ in range(count):

                # Kreiranje ankete
                poll = Poll.objects.create(
                    question=fake.random_element(
                        elements=QUESTIONS
                    ),
                    author=fake.random_element(
                        elements=users
                    ),
                    closes_at=timezone.now() + timedelta(
                        days=fake.random_int(min=1, max=30)
                    )
                )

                # Kreiranje 2-6 različitih odgovora
                choice_count = fake.random_int(
                    min=2,
                    max=6
                )

                selected_answers = fake.random_elements(
                    elements=ANSWERS,
                    length=choice_count,
                    unique=True
                )

                choices = []

                for answer in selected_answers:
                    choice = Choice.objects.create(
                        poll=poll,
                        text=answer
                    )
                    choices.append(choice)

                # Registrovani glasovi
                registered_count = fake.random_int(
                    min=0,
                    max=min(len(users), 10)
                )

                selected_users = random.sample(
                    users,
                    registered_count
                )

                for user in selected_users:
                    Vote.objects.create(
                        choice=random.choice(choices),
                        user=user,
                        session_key=None
                    )

                    created_registered_votes += 1

                # Anonimni glasovi
                anonymous_count = fake.random_int(
                    min=5,
                    max=15
                )

                used_sessions = set()

                for _ in range(anonymous_count):

                    session_key = fake.uuid4()

                    while session_key in used_sessions:
                        session_key = fake.uuid4()

                    used_sessions.add(session_key)

                    Vote.objects.create(
                        choice=random.choice(choices),
                        user=None,
                        session_key=session_key
                    )

                    created_anonymous_votes += 1

        created_votes = (
            created_registered_votes +
            created_anonymous_votes
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Uspešno generisano {count} anketa!'
            )
        )

        self.stdout.write(
            f'Ukupno glasova: {created_votes}'
        )

        self.stdout.write(
            f'Registrovani glasovi: {created_registered_votes}'
        )

        self.stdout.write(
            f'Anonimni glasovi: {created_anonymous_votes}'
        )
