from django.contrib import admin

from .models import CodingProblem, InputOutput


class InputOutputInline(admin.TabularInline):
    model = InputOutput


class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'public')
    list_filter = ('public',)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [InputOutputInline]


admin.site.register(CodingProblem, CodingProblemAdmin)
