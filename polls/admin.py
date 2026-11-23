
from django.contrib import admin
from .models import Poll, Choice, Vote


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'author',
        'created_at',
        'closes_at',
        'is_open',
        'total_votes',
    )

    list_filter = ('created_at', 'closes_at')
    search_fields = ('question', 'author__username')

    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'poll')
    search_fields = ('text', 'poll__question')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('choice', 'user', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('choice__text', 'user__username')
