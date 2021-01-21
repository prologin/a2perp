from django.contrib import admin
from . import models

@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'id', 'upstream_id', 'status', 'date_start', 'date_end')
    list_filter = ('status',)
    search_fields = ('display_name', 'id', 'upstream_id')


    readonly_fields = ('id',)

    fieldsets = (
        ('Infos générales', {
            'fields': (
                'id',
                'display_name',
                'status',
            ),
        }),
        ('Infos site Prologin', {
            'fields': (
                'upstream_id',
            ),
        }),
        ('Sujet et Instructions', {
            'fields': (
                'subject',
                'contestant_instructions',
            ),
        }),
        ('Début et fin de la période de rendu', {
            'fields': (
                'date_start',
                'date_end',
            )
        })
    )