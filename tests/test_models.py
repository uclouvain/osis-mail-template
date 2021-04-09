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

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.utils.translation import gettext_lazy as _

from osis_mail_template.exceptions import (
    MissingToken,
    UnknownMailTemplateIdentifier,
    UnknownLanguage,
    EmptyMailTemplateContent,
)
from osis_mail_template.models import MailTemplate


class MailTemplateModelTest(SimpleTestCase):
    def setUp(self):
        self.template = MailTemplate(
            identifier='test-mail-template',
            language='en',
            subject='This is a test subject {token}',
            body='<p>This is a test body {token}</p>',
        )

    def test_display(self):
        self.assertEqual(str(self.template), 'test-mail-template-en')

    def test_display_language(self):
        self.assertEqual(self.template.get_language_display(), _("English"))

    def test_rendering_subject(self):
        self.assertEqual(self.template.render_subject({
            'token': 'example',
        }), 'This is a test subject example')

    def test_rendering_with_example(self):
        with patch('osis_mail_template.templates') as tpl:
            tpl.get_example_values.return_value = {
                'token': 'example value',
            }
            self.assertEqual(self.template.render_subject(), 'This is a test subject example value')

    def test_rendering_body_html(self):
        self.assertEqual(self.template.body_as_html({
            'token': 'example',
        }), '<p>This is a test body example</p>')

    def test_rendering_body_plain(self):
        self.assertEqual(self.template.body_as_plain({
            'token': 'example',
        }), 'This is a test body example\n\n')

    def test_rendering_missing_token(self):
        with self.assertRaises(MissingToken):
            self.template.render_subject({})

    def test_create_non_existant(self):
        with patch('osis_mail_template.templates') as tpl:
            tpl.get_mail_templates.return_value = {}
            with self.assertRaises(ValidationError):
                self.template.full_clean()


class MailTemplateManagerTest(TestCase):
    TEMPLATE_ID = 'test-mail-template'

    def setUp(self):
        self.template = MailTemplate.objects.create(
            identifier=self.TEMPLATE_ID,
            language='en',
            subject='This is a test subject {token}',
            body='<p>This is a test body {token}</p>',
        )

    def test_get_by_id(self):
        self.assertEqual(MailTemplate.objects.get_by_id(self.TEMPLATE_ID), [self.template])

    def test_get_non_existant(self):
        with self.assertRaises(UnknownMailTemplateIdentifier):
            MailTemplate.objects.get_by_id('unknown')

    def test_get_non_existant_content(self):
        with patch('osis_mail_template.templates') as tpl:
            tpl.get_mail_template.return_value = None
            with self.assertRaises(EmptyMailTemplateContent):
                MailTemplate.objects.get_by_id('known')

    def test_get_non_existant_language(self):
        with self.assertRaises(UnknownLanguage):
            MailTemplate.objects.get_mail_template(self.TEMPLATE_ID, 'de')

    def test_get_non_existant_content_for_language(self):
        with self.assertRaises(EmptyMailTemplateContent):
            MailTemplate.objects.get_mail_template(self.TEMPLATE_ID, 'fr-be')
