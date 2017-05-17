from django.contrib import admin

from recruitr.admin import admin_site
from .models import CodingProblem, InputOutput


class InputOutputInline(admin.TabularInline):
    model = InputOutput


class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'public')
    list_filter = ('public',)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [InputOutputInline]


admin_site.register(CodingProblem, CodingProblemAdmin)
