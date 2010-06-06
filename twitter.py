import httplib
from django.conf import settings
from django.utils import simplejson as json
from django.core.exceptions import ImproperlyConfigured
from oauth import oauth


if not hasattr(settings, 'TWITTERAUTH_KEY') and \
       hasattr(settings, 'TWITTERAUTH_SECRET'):
    raise ImproperlyConfigured('Django twitterauth requires TWITTERAUTH_KEY and TWITTERAUTH_SECRET to be set in settings.py')


TWITTER_REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
TWITTER_AUTHORIZE_URL = 'https://twitter.com/oauth/authorize'
TWITTER_ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'
TWITTER_VERIFY_CREDENTIALS_URL = 'https://twitter.com/account/verify_credentials.json'

# Timeline Methods
TWITTER_PUBLIC_TIMELINE = "https://twitter.com/statuses/public_timeline.json"
TWITTER_FRIENDS_TIMELINE = "https://twitter.com/statuses/friends_timeline.json"
# Status Methods
TWITTER_UPDATE_STATUS = 'https://twitter.com/statuses/update.json'
# User Methods
TWITTER_FRIENDS = 'https://twitter.com/statuses/friends.json'
TWITTER_FOLLOWERS = 'https://twitter.com/statuses/followers.json'


class TwitterAPI(object):
    def __init__(self, token=None):
        self.consumer = oauth.OAuthConsumer(settings.TWITTERAUTH_KEY, settings.TWITTERAUTH_SECRET)
        self.conn = None
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.token = token

    @property
    def connection(self):
        if not self.conn:
            self.conn = httplib.HTTPSConnection('twitter.com')
        return self.conn

    def make_request(self, url, parameters=None, method='GET', token=None):
        if token is None:
            token = self.token
        if parameters is None:
            parameters = {}
            
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, 
                     http_url=url, parameters=parameters, http_method=method)
        request.sign_request(self.signature_method, self.consumer, token)
        return self._make_request(request)

    def _make_request(self, request):
        self.connection.request(request.http_method, request.to_url())
        result = self.connection.getresponse().read()
        return result

    def get_request_token(self):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, 
                                                             http_url=TWITTER_REQUEST_TOKEN_URL)
        request.sign_request(self.signature_method, self.consumer, None)
        return oauth.OAuthToken.from_string(self._make_request(request))

    def get_authorization_url(self, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=request_token,
                                                             http_url=TWITTER_AUTHORIZE_URL)
        request.sign_request(self.signature_method, self.consumer, request_token)
        return request.to_url()

    def get_access_token(self, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=request_token,
                                                             http_url=TWITTER_ACCESS_TOKEN_URL)
        request.sign_request(self.signature_method, self.consumer, request_token)
        return oauth.OAuthToken.from_string(self._make_request(request))

    def verify_credentials(self):
        return json.loads(self.make_request(TWITTER_VERIFY_CREDENTIALS_URL))
    
    def tweet(self, status):
        return self.make_request(
            TWITTER_UPDATE_STATUS,
            method='POST',
            parameters=dict(status=status)
        )
        
    def friends(self, screen_name):
        return self.make_request(
            TWITTER_FRIENDS,
            parameters=dict(screen_name=screen_name)
        )
        
    
