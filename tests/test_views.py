# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
# ##############################################################################
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from mock import patch

from base.tests.factories.user import UserFactory
from osis_mail_template import Token
from osis_mail_template.models import MailTemplate


class TestMailTemplateViews(TestCase):
    registry = None
    TEMPLATE_ID = 'test-identifier'

    @classmethod
    def setUpTestData(cls):
        cls.registry = patch('osis_mail_template.templates', **{
            'get_list_by_tag.return_value': {
                'some tag': {
                    'identifier': 'Custom description'
                }
            },
            'get_tokens.return_value': [
                Token('token', 'Token description', 'Example value'),
            ],
            'get_description.return_value': 'Some mail template',
            'get_example_values.return_value': {
                'token': 'Example value',
            },
        })
        cls.url = reverse('osis_mail_template:change', kwargs={'identifier': cls.TEMPLATE_ID})
        cls.registry.start()
        cls.user = UserFactory()
        cls.user.user_permissions.add(Permission.objects.create(
            content_type=ContentType.objects.get_for_model(MailTemplate),
            codename='configure',
        ))

    def setUp(self):
        self.client.force_login(self.user)
        self.template = MailTemplate.objects.create(
            identifier=self.TEMPLATE_ID,
            language='en',
            subject='This is a subject with a {token}',
            body='<p>Hello,</p><p>This is a body with a {token}</p><p>--<br>The OSIS Team</p>',
        )

    @classmethod
    def tearDownClass(cls):
        cls.registry.stop()

    def test_list(self):
        response = self.client.get(reverse('osis_mail_template:list'))
        self.assertContains(response, "Custom description")

    def test_get(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Some mail template")
        self.assertContains(response, "{token}")
        self.assertContains(response, "Token description")
        self.assertContains(response, "Example value")

    def test_post_invalid(self):
        response = self.client.post(self.url, {
            'en-subject': 'This is a {wrong-token}',
            'en-body': 'This is a body',
        })
        self.assertFalse(response.context['forms'][0].is_valid())

    def test_post_valid(self):
        response = self.client.post(self.url, {
            'en-subject': 'This is a {token}',
            'en-body': 'This is a body with a {token}',
        })
        self.assertRedirects(response, reverse('osis_mail_template:list'))
        self.template.refresh_from_db()
        self.assertEqual(self.template.subject, 'This is a {token}')

    def test_preview(self):
        url = reverse('osis_mail_template:preview', kwargs={'identifier': self.TEMPLATE_ID})
        response = self.client.get(url)
        self.assertContains(response, "This is a subject with a Example value")
        self.assertContains(response, "<p>Hello,</p><p>This is a body with a Example value</p><p>--<br>The OSIS Team</p>")
