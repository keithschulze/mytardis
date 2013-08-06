# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from tastypie.test import ResourceTestCase
from django.test.client import Client

from django.conf import settings
from django.contrib.auth.models import User

class ApiKeyDownloadTestCase(ResourceTestCase):

    def setUp(self):
        # create a test user
        self.username = 'test'
        self.email = 'test@example.com'
        self.password = 'passw0rd'
        self.user = User.objects.create_user(username=self.username,
                                             email=self.email,
                                             password=self.password)

    def tearDown(self):
        self.user.delete()

    def testView(self):
        download_api_key_url = reverse('tardis.tardis_portal.views.download_api_key')
        client = Client()

        # Expect redirect to login
        response = client.get(download_api_key_url)
        self.assertEqual(response.status_code, 302)

        # Login as user
        login = client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        response = client.get(download_api_key_url)
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename="{0}.key"'.format(self.username))
        self.assertEqual(response.status_code, 200)
        response_content = ""
        for c in response.streaming_content:
            response_content += c
        self.assertEqual(response_content,
                         self.create_apikey(username=self.username,
                                            api_key=user.api_key.key))
