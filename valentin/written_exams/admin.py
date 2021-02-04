from django.contrib import admin
from . import models


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session", "last_updated")
    list_filter = ("session",)
    search_fields = ("user__first_name", "user__last_name", "user__username")

    readonly_fields = ("last_updated",)
