from django.contrib import admin
from . import models

@admin.register(models.FormInstance)
class FormInstanceAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'subject_path', 'id')
    search_fields = ('display_name', 'subject_path', 'id')
    readonly_fields = ('id', )

@admin.register(models.UserAnswers)
class UserAnswersAdmin(admin.ModelAdmin):
    list_display = ('user', 'form')
    list_filter = ('form', )
    search_fields = ('user__last_name', 'user__first_name')
    readonly_fields = ('last_updated', )
