import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #These are needed for Cloudflare TURNSTILE: https://developers.cloudflare.com/turnstile/
    #The Default values are for testing and will "Always Allow": https://developers.cloudflare.com/turnstile/reference/testing/
    TURNSTILE_SITE_KEY = os.environ.get('TURNSTILE_SITE_KEY') or "1x00000000000000000000AA"
    TURNSTILE_SITE_SECRET = os.environ.get('TURNSTILE_SITE_SECRET') or "1x0000000000000000000000000000000AA"
    #Disabling this flag until the Flask-TURNSTILE issue is resolved
    TURNSTILE_ENABLED = False