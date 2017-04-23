from django.contrib import admin

from .models import CodingProblem, CodeSubmission, InputOutput


class InputOutputInline(admin.TabularInline):
    model = InputOutput


class CodingProblemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    inlines = [InputOutputInline]


admin.site.register(CodingProblem, CodingProblemAdmin)
