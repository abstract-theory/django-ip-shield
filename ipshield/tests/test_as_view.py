# from django.http import HttpResponse
import os
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from .urls import maxAllowed


TEST_TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.dirname(__file__), ],
    },
]



@override_settings(ROOT_URLCONF="ipshield.tests.urls", TEMPLATES=TEST_TEMPLATES)
class AsViewTests(TestCase):

    # good bots must reach the template.
    def test_good_bots_template_as_view(self):

        # add max allowed number of events younger than findTime
        for n in range(maxAllowed):
            res = self.client.get('/test-hello-template/')
            # requests are not blocked
            self.assertEqual(res.status_code, 200)

        res = self.client.get('/test-hello-template/')
        # now request should be blocked
        self.assertEqual(res.status_code, 429)

