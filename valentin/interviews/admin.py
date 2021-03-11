from django.contrib import admin
from . import models


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
    list_display = ("name", "id", "status", "upstream_id")
    search_fields = ("name", "id")
    list_filter = ("status", "upstream_id")


@admin.register(models.Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("date_start", "date_end", "session")
    list_filter = ("session",)


@admin.register(models.Interviewer)
class InterviewerAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("__str__", "meet_link")
    search_fields = ("user__first_name", "user__last_name")


@admin.register(models.SlotInstance)
class SlotInstanceAdmin(admin.ModelAdmin):
    list_display = ("interviewer", "slot", "contestant_full_name")
    search_fields = ("contestant__first_name", "contestant__last_name")
    list_filter = (
        "slot__session",
        "interviewer",
        ("contestant", admin.EmptyFieldListFilter),
        ("slot__date_start", admin.DateFieldListFilter),
    )
    raw_id_fields = ("interviewer", "slot", "contestant")


@admin.register(models.InterviewScore)
class InterviewScoreAdmin(admin.ModelAdmin):
    list_display = ("contestant_full_name", "grade", "session")
    search_fields = ("contestant__first_name", "contestant__last_name")
    list_filter = ("session",)
    raw_id_fields = ("contestant",)
