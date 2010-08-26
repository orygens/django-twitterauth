#-*- coding:utf-8 -*-

from django.test import TestCase

from django.conf import settings
from django.core.urlresolvers import reverse

class TestCase(TestCase):
    
    def test_login_twitter(self):
        """
        Login no Twitter
        
        - Chama a view de efetuar login;
                
                - É redirecionado para a url do twitter;
                - Retorna para a url do sistema de callback;
                
        - Apresenta ao usuário o formulário de login com uma url do twitter.com para pegar o pincode;
        - Insere o pincode no formulário de acesso;
        - Chama a view de callback passando o pincode;
        - Salva o usuário no banco de dados;
        
        """
        response = self.client.get(reverse('auth_login'))
        if settings.DEBUG:
            self.assertContains(response, "https://api.twitter.com/oauth/authorize", status_code=200, 
                            msg_prefix="Não retornou a url de autorização do twitter.")
            
        else:
            self.assertNotEqual("302", response.status_code, "Não redirecionou para o twitter")
            self.assertTrue(response['Location'].startswith('https://api.twitter.com/oauth/authorize'), 
                            "Não retornou a url correta do twitter.")