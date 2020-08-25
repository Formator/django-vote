from django.apps import AppConfig as BaseConfig
from django.utils.translation import gettext as _


class VoteAppConfig(BaseConfig):
    name = 'vote'
    verbose_name = _('Vote')

    def ready(self):
        from . import signals
