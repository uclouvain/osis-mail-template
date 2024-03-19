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
from django.conf import settings
from django.test import SimpleTestCase, TestCase

from osis_mail_template.models import MailTemplate
from osis_mail_template.utils import transform_html_to_text, generate_email, render_email_content

LINK_PARAGRAPH_HTML = """
<p>This is a <a href="http://test.com">link</a>, it should be rendered after the paragraph</p>
"""
LINK_PARAGRAPH_PLAIN = """This is a [link][1], it should be rendered after the paragraph

   [1]: http://test.com

"""

BODY_WIDTH_HTML = """
<p>This is a very long paragraph that should be wrapped after 80 characters, I'm adding more 
words to go beyond this limit.</p> 
"""
BODY_WIDTH_PLAIN = """This is a very long paragraph that should be wrapped after 80 characters, I'm
adding more words to go beyond this limit.

"""


class TransformHtmlToTextTestCase(SimpleTestCase):
    def test_link_paragraphs(self):
        self.assertEqual(transform_html_to_text(LINK_PARAGRAPH_HTML), LINK_PARAGRAPH_PLAIN)

    def test_body_width(self):
        self.assertEqual(transform_html_to_text(BODY_WIDTH_HTML), BODY_WIDTH_PLAIN)


class GenerateEmailMessageTestCase(TestCase):
    TEMPLATE_ID = 'test-identifier'

    def setUp(self):
        self.template = MailTemplate.objects.create(
            identifier=self.TEMPLATE_ID,
            language='en',
            subject='This is a subject with {token}',
            body='<p>Hello,</p><p>This is a body with {token}</p><p>--<br>The OSIS Team</p>',
        )

    def test_generate_message(self):
        tokens = {'token': 'my real value'}
        email_message = generate_email(self.TEMPLATE_ID, 'en', tokens, ['to@example.com'])
        self.assertTrue(email_message.is_multipart())
        self.assertEqual(email_message['From'], settings.DEFAULT_FROM_EMAIL)
        self.assertIn('<html', email_message.as_string())
        self.assertIn('my real value</p>', email_message.as_string())
        self.assertTrue(email_message.is_multipart())

        # Now check the payload of each part (plain text and html)
        plain_part = ''
        html_part = ''
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                plain_part = part.get_payload()
            elif part.get_content_type() == "text/html":
                html_part = part.get_payload(decode=True)
        self.assertEqual(plain_part, self.template.body_as_plain(tokens))
        self.assertIn(self.template.body_as_html(tokens), html_part.decode())
        self.assertEqual(
            email_message.get("subject"),
            self.template.render_subject(tokens),
        )


class RenderEmailContentTestCase(TestCase):
    TEMPLATE_ID = 'test-identifier'

    def setUp(self):
        self.template = MailTemplate.objects.create(
            identifier=self.TEMPLATE_ID,
            language='en',
            subject='This is a subject with {token}',
            body='<p>Hello,</p><p>This is a body with {token}</p><p>--<br>The OSIS Team</p>',
        )

    def test_generate_message(self):
        subject, body = render_email_content(self.TEMPLATE_ID, 'en', {'token': 'my real value'})
        self.assertEqual('This is a subject with my real value', subject)
        self.assertIn('my real value</p>', body)
