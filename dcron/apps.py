from django.apps import AppConfig
from .version import get_version


class CustomConfig(AppConfig):
    name = 'dcron'
    verbose_name = "dcron - v" + get_version()
