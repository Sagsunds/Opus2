from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin #flaw4
from django.contrib.auth.models import User
from .models import Choice, Question, Vote

from .models import Choice, Question


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin #flaw4
from django.contrib.auth.models import User
from .models import Choice, Question, Vote

class VoteInline(admin.TabularInline):# Flaw 4
    model = Vote
    extra = 0 
    readonly_fields = ['question', 'choice']

class UserAdmin(BaseUserAdmin):
    inlines = [VoteInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Question, QuestionAdmin)