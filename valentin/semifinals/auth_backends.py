from social_core.backends.open_id_connect import OpenIdConnectAuth
from django.conf import settings


class ProloginOIDCBackend(OpenIdConnectAuth):
    name = "prologin"
    OIDC_ENDPOINT = settings.PROLOGIN_OIDC_ENDPOINT
