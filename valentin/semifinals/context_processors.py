from django.conf import settings

def application_settings(request):
    return {
        'settings': {
            'APP_SHOW_PIZZA_ICON': getattr(settings, 'APP_SHOW_PIZZA_ICON', True),
            'APP_NO_LOCAL_LOGIN': getattr(settings, 'APP_NO_LOCAL_LOGIN', True),
        }
    }
