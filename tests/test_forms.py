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

from django.test import TestCase

from osis_mail_template.forms import MailTemplateConfigureForm
from osis_mail_template.models import MailTemplate


class MailTemplateModelTest(TestCase):
    def setUp(self):
        self.instance = MailTemplate.objects.create(
            identifier='test-mail-template',
            language='en',
        )

    @patch('osis_mail_template.templates')
    def test_check_form_valid(self, tpl):
        tpl.get_example_values.return_value = {
            'token': 'example value',
        }

        form = MailTemplateConfigureForm(data={
            'subject': 'This is a test subject {token}',
            'body': '<p>This is a test body {token}</p>'
        }, instance=self.instance)
        self.assertTrue(form.is_valid(), form.errors)

    @patch('osis_mail_template.templates')
    def test_check_form_invalid_missing_token(self, tpl):
        tpl.get_example_values.return_value = {}

        form = MailTemplateConfigureForm(data={
            'subject': 'This is a test subject',
            'body': '<p>This is a test body {token}</p>'
        }, instance=self.instance)
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)
