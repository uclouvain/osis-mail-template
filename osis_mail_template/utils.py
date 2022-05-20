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
from email.message import EmailMessage
from typing import List, Dict, Tuple

import html2text
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation


def generate_email(mail_template_id: str, language: str, tokens: Dict[str, str], recipients: List[str],
                   sender=None) -> EmailMessage:
    """
    Generate a pre-configured EmailMessage ready for sending

    :param mail_template_id: The mail template identifier (must exist)
    :param language: The mail template language (must exist)
    :param tokens: A dictionary of tokens with their corresponding value
    :param recipients: A list of recipients
    :param sender: The sender's email address (defaults to settings.DEFAULT_FROM_EMAIL)
    :return: an EmailMessage() object for sending
    """
    from osis_mail_template.models import MailTemplate

    # Get the mail template
    template = MailTemplate.objects.get_mail_template(mail_template_id, language)

    # Format the content in the provided language (in case of lazy translations in tokens)
    with translation.override(language):
        subject = template.render_subject(tokens)
        html_content = render_to_string('osis_mail_template/base_email.html', {
            'subject': subject,
            'language': language,
            'recipients': recipients,
            'sender': sender,
            'content': template.body_as_html(tokens),
        })
        text_content = template.body_as_plain(tokens)

    # Construct the message
    msg = EmailMessage()
    msg.set_charset(settings.DEFAULT_CHARSET)
    msg['Subject'] = subject
    msg['From'] = sender or settings.DEFAULT_FROM_EMAIL
    msg['To'] = recipients
    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")
    return msg


def render_email_content(mail_template_id: str, language: str, tokens: Dict[str, str]) -> Tuple[str, str]:
    """
    Render a mail template subject and body ready to use (e.g. in an user-facing form)

    :param mail_template_id: The mail template identifier (must exist)
    :param language: The mail template language (must exist)
    :param tokens: A dictionary of tokens with their corresponding value
    :return:
    """
    from osis_mail_template.models import MailTemplate

    # Get the mail template
    template = MailTemplate.objects.get_mail_template(mail_template_id, language)

    # Render subject and body
    subject = template.render_subject(tokens)
    body = template.body_as_html(tokens)
    return subject, body


def transform_html_to_text(html: str) -> str:
    """Transforms html markup to plain text for email sending

    :param html: THe html markup string to transform
    :return: The plain text formatted string
    """
    h = html2text.HTML2Text()
    h.links_each_paragraph = True
    h.body_width = 80
    h.inline_links = False
    h.wrap_links = False
    h.wrap_list_items = True
    h.use_automatic_links = True
    return h.handle(html)


class MissingTokenDict(dict):
    def __missing__(self, key):
        return "TOKEN_{}_UNDEFINED".format(key)
