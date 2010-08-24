# -*- charset: utf8 -*-

from django.test import TestCase

import twitter


class MockHttplib:
    class HTTPConnection(object):
        
        def __init__(self, url, code=200, response=""):
            self.url = url
            self.code = code
            self.response = response
        
        def request(self, method, url):
            pass
        
        def getresponse(self):
            class Resp:
                def read(inself):
                    return self.response
            return Resp()
    
    class HTTPSConnection(HTTPConnection):
        pass

class fake_httplib(object):
    def __init__(self, module, response_handler):
        self.module = module
        self.original_httplib = module.httplib
        self.response_handler = response_handler
    
    def __enter__(self):
        self.module.httplib = MockHttplib()
    
    def __exit__(self):
        self.module.httplib = self.original_httplib

class TestTwitterCommunication(TestCase):
    
    def test_erro_400(self):
        with fake_httplib(twitter, 400):
            twitter = twitter.TwitterAPI()
            twitter.friends("rafaelcaricio")
        