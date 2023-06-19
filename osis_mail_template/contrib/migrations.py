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

from django.conf import settings
from django.db.migrations import RunPython


class MailTemplateMigration(RunPython):
    def __init__(self, identifier: str, subjects: Dict[str, str], contents: Dict[str, str], remove_on_reverse=True):
        def forward(apps, schema_editor):
            from osis_mail_template import templates
            from osis_mail_template.exceptions import EmptyMailTemplateContent, UnknownToken

            MailTemplate = apps.get_model('osis_mail_template', 'MailTemplate')
            for lang, _ in settings.LANGUAGES:
                # Some basic validation
                tokens = templates.get_example_values(identifier)
                try:
                    subjects[lang].format(**tokens)
                    contents[lang].format(**tokens)
                except KeyError as e:
                    raise UnknownToken(e.args[0], identifier)

                # Save the model instance
                try:
                    MailTemplate.objects.update_or_create(
                        identifier=identifier,
                        language=lang,
                        defaults=dict(
                            subject=subjects[lang],
                            body=contents[lang],
                        ),
                    )
                except KeyError:  # pragma: no cover
                    raise EmptyMailTemplateContent(identifier, lang)

        def reverse(apps, schema_editor):
            MailTemplate = apps.get_model('osis_mail_template', 'MailTemplate')
            # Remove all model instances
            MailTemplate.objects.filter(identifier=identifier).delete()

        super().__init__(forward, reverse_code=reverse if remove_on_reverse else RunPython.noop)
