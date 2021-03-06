from django.conf import settings


def application_settings(request):
    return {
        "settings": {
            "APP_SHOW_PIZZA_ICON": getattr(settings, "APP_SHOW_PIZZA_ICON"),
            "APP_NO_LOCAL_LOGIN": getattr(settings, "APP_NO_LOCAL_LOGIN"),
            "APP_MAX_UPLOAD_SIZE": getattr(settings, "APP_MAX_UPLOAD_SIZE"),
            "APP_ITW_MEET_UNLOCK_BEFORE": getattr(
                settings, "APP_ITW_MEET_UNLOCK_BEFORE"
            ),
        }
    }
