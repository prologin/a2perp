from .common import *

DEBUG = False
ALLOWED_HOSTS = ['valentin.prologin.dev']

'''
Application settings
'''
APP_SHOW_PIZZA_ICON = True
APP_NO_LOCAL_LOGIN = False

# Given as an indication to contestants, the real limit
# must be set in the reverse proxy configuration
APP_MAX_UPLOAD_SIZE = '4 Mo'


'''
Social Auth Settings
'''
# To obtain a Client ID and Client Secret you must contact
# a Prologin Root, the redirect uri will be https://<site_host>:<site_port>/social/complete/prologin

SOCIAL_AUTH_PROLOGIN_KEY = 'CHANGE_ME' # This is the client ID given by a Prologin Root
SOCIAL_AUTH_PROLOGIN_SECRET = 'CHANGE_ME' # This is the client secret given by a Prologin Root
