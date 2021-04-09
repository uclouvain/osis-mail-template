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
from typing import Dict

import html2text
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from osis_mail_template.exceptions import (
    EmptyMailTemplateContent,
    MissingToken,
    UnknownMailTemplateIdentifier,
    UnknownLanguage,
)


class MailTemplateManager(models.Manager):
    def get_by_id(self, identifier: str):
        """Get a list of mail template instances by identifier"""
        instances = list(self.get_queryset().filter(identifier=identifier))
        if not instances:
            from osis_mail_template import templates
            try:
                templates.get_mail_template(identifier)
            except UnknownMailTemplateIdentifier:
                raise
            raise EmptyMailTemplateContent(identifier)
        return instances

    def get_mail_template(self, identifier: str, language: str):
        """Get a single mail template instance by identifier and language"""
        try:
            assert language in dict(settings.LANGUAGES)
        except AssertionError:
            raise UnknownLanguage(language)
        try:
            return self.get_queryset().get(identifier=identifier, language=language)
        except MailTemplate.DoesNotExist:
            raise EmptyMailTemplateContent(identifier, language)


def check_mail_template_identifier(identifier):
    from osis_mail_template import templates
    if identifier not in templates.get_mail_templates():
        raise UnknownMailTemplateIdentifier(identifier)


class MailTemplate(models.Model):
    identifier = models.CharField(
        max_length=255,
        verbose_name=_("Identifier"),
        validators=[check_mail_template_identifier],
    )
    language = models.CharField(
        max_length=25,
        verbose_name=_("Language"),
        choices=(lang for lang in settings.LANGUAGES),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
    )
    body = models.TextField(
        verbose_name=_("Body"),
    )

    objects = MailTemplateManager()

    class Meta:
        verbose_name = _("Mail template")
        verbose_name_plural = _("Mail templates")
        unique_together = [
            ['identifier', 'language'],
        ]

    def __str__(self):
        return '{}-{}'.format(self.identifier, self.language)

    def _replace_tokens(self, field: str, tokens: Dict[str, str] = None) -> str:
        if tokens is None:
            from osis_mail_template import templates
            tokens = templates.get_example_values(self.identifier)
        try:
            return getattr(self, field).format(**tokens)
        except KeyError as e:
            raise MissingToken(e.args[0])

    def render_subject(self, tokens: Dict[str, str] = None) -> str:
        """Renders the subject with the given tokens, or example values"""
        return self._replace_tokens('subject', tokens)

    def body_as_html(self, tokens: Dict[str, str] = None) -> str:
        """Renders the body as HTML with the given tokens, or example values"""
        return self._replace_tokens('body', tokens)

    def body_as_plain(self, tokens: Dict[str, str] = None) -> str:
        """Renders the body as plain text with the given tokens, or example values"""
        formatted_body = self.body_as_html(tokens)

        h = html2text.HTML2Text()
        h.links_each_paragraph = True
        h.body_width = 80
        h.inline_links = False
        h.wrap_links = False
        h.wrap_list_items = True
        h.use_automatic_links = True
        return h.handle(formatted_body)
