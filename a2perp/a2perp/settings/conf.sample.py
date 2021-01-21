from .common import *

DEBUG = False
ALLOWED_HOSTS = ['a2perp.prologin.dev']

# To obtain a Client ID and Client Secret you must contact
# a Prologin Root, the redirect uri will be https://<site_host>:<site_port>/social/login/prologin

SOCIAL_AUTH_PROLOGIN_KEY = 'CHANGE_ME' # This is the client ID given by a Prologin Root
SOCIAL_AUTH_PROLOGIN_SECRET = 'CHANGE_ME' # This is the client secret given by a Prologin Root
