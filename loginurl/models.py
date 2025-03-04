from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from loginurl.utils import create_key

@python_2_unicode_compatible
class Key(models.Model):
    """
    A simple key store.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    key = models.CharField(max_length=40, unique=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    usage_left = models.IntegerField(null=True, blank=True, default=1)
    expires = models.DateTimeField(null=True, blank=True)
    next = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return '{} ({})'.format(self.key, self.user.get_username())

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = create_key(self.user)

        return super(Key, self).save(*args, **kwargs)

    def is_valid(self):
        """
        Check if the key is valid.

        Key validation checks the value of ``usage_left`` and ``expires``
        properties of the key. If both are ``None`` then the key is always
        valid.
        """
        if self.usage_left is not None and self.usage_left <= 0:
            return False
        if self.expires is not None and self.expires < timezone.now():
            return False
        return True

    def update_usage(self):
        """
        Update key usage counter.

        This only relevant if the ``usage_left`` property is used.
        """
        if self.usage_left is not None and self.usage_left > 0:
            self.usage_left -= 1
            self.save()
