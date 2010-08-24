# -*- charset: utf8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.conf import settings
from oauth import oauth
from models import User
from decorators import login_required
from twitterauth import REDIRECT_FIELD_NAME


SESSION_LOGIN_REDIRECT_KEY = '_login_redirect_key'
SESSION_TOKEN_KEY = '_token'


@login_required
def info(request):
    if 'POST' == request.method:
        request.user.email = request.POST['email']
        errors = request.user.validate()
        if not errors: request.user.save()
        return render_to_response('info.html', {
            'user': request.user,
            'errors': errors
        })
    return render_to_response('info.html', {'user': request.user})


def login(request, redirect_field_name=REDIRECT_FIELD_NAME):
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    request_token = request.user.twitter_api.get_request_token()
    #print 'Token', request_token
    request.session.set_test_cookie()
    request.session[SESSION_TOKEN_KEY] = request_token.to_string()
    request.session[SESSION_LOGIN_REDIRECT_KEY] = redirect_to
    
    authorization_url = request.user.twitter_api.get_authorization_url(request_token)
    #print 'Authorization url', authorization_url
    return HttpResponseRedirect(authorization_url)


def callback(request):
    request_token = request.session.get(SESSION_TOKEN_KEY, None)
    if request_token is None:
        return render_to_response('callback.html', {
            'token': True
        })
    request_token = oauth.OAuthToken.from_string(request_token)
    if request_token.key != request.GET.get('oauth_token', 'no-token'):
        return render_to_response('callback.html', {
            'mismatch': True
        })
    request.user.twitter_api.token = request.user.twitter_api.get_access_token(request_token)

    # Actually login
    credentials = request.user.twitter_api.verify_credentials()
    if credentials is None:
        return render_to_response('callback.html', {
            'username': True
        })

    from twitterauth import login, authenticate
    user, created = User.objects.get_or_create(username=credentials['screen_name'])
    if created or (user.key != request.user.twitter_api.token.key or 
                   user.secret != request.user.twitter_api.token.secret):
        user.key = request.user.twitter_api.token.key
        user.secret = request.user.twitter_api.token.secret
    user.thumbnail = credentials['profile_image_url']
    user.name = credentials['name']
    user.save()
    
    # Call authenticate to verify and add backend to the user object.
    user = authenticate(key=user.key, secret=user.secret)
    #print 'vamos'
    #print 'Aqui', user
    login(request, user)
    #print 'request.user: ', request.user
    #print '...................'
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    del request.session[SESSION_TOKEN_KEY]

    return HttpResponseRedirect(request.session[SESSION_LOGIN_REDIRECT_KEY])


def logout(request, next_page=None):
    from twitterauth import logout
    logout(request)
    return HttpResponseRedirect(next_page or request.path)
