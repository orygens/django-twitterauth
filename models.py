import urllib
import datetime
from oauth import oauth
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from twitterauth.twitter import TwitterAPI
from django.utils import simplejson


class User(models.Model):
    username = models.CharField(max_length=40)
    thumbnail = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    last_login = models.DateTimeField(_('last login'), default=datetime.datetime.now)
    date_joined = models.DateTimeField(_('date joined'), default=datetime.datetime.now)

    key = models.CharField(max_length=200)
    secret = models.CharField(max_length=200)

    def __unicode__(self):
        return self.username

    _twitter_api = None
    @property
    def twitter_api(self):
        if self._twitter_api is None:
            self._twitter_api = TwitterAPI()
        return self._twitter_api

    def get_absolute_url(self):
        return reverse('user', kwargs={'id': self.id})

    def to_string(self, only_key=False):
        # so this can be used in place of an oauth.OAuthToken
        if only_key:
            return urllib.urlencode({'oauth_token': self.key})
        return urllib.urlencode({'oauth_token': self.key, 'oauth_token_secret': self.secret})

    def get_and_delete_messages(self): pass

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_authorized(self): 
        return True

    def is_twauthorized(self):
        return bool(self.twitter_api.verify_credentials())

    def tweet(self, status):
        return simplejson.loads(self.twitter_api.make_request(
            'https://twitter.com/statuses/update.json',
            self.token(),
            http_method='POST',
            status=status
        ))


class AnonymousUser(object):
    username = ''
    
    key = ''
    secret = ''

    def __unicode__(self):
        return 'AnonymousUser'

    def to_string(self, only_key=False):
        raise NotImplemented

    _twitter_api = None
    @property
    def twitter_api(self):
        if self._twitter_api is None:
            self._twitter_api = TwitterAPI()
        return self._twitter_api

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

    def tweet(self, status):
        raise NotImplemented

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

    def is_twauthorized(self):
        return False
