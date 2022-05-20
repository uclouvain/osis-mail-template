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
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

__all__ = [
    'DuplicateMailTemplateIdentifier',
    'UnknownMailTemplateIdentifier',
    'UnknownLanguage',
    'EmptyMailTemplateContent',
]


class DuplicateMailTemplateIdentifier(Exception):
    def __init__(self, identifier) -> None:
        super().__init__(_(
            "The mail template '%(identifier)s' is already registered."
        ) % {'identifier': identifier})


class UnknownMailTemplateIdentifier(ValidationError):
    def __init__(self, identifier) -> None:
        super().__init__(_(
            "The mail template '%(identifier)s' is not registered."
        ) % {'identifier': identifier})


class UnknownToken(Exception):
    def __init__(self, token, identifier) -> None:
        super().__init__(_(
            "The token '%(token)s' is not declared in '%(identifier)s' mail template."
        ) % {'token': token, 'identifier': identifier})


class EmptyMailTemplateContent(Exception):
    def __init__(self, identifier, language=None) -> None:
        if language:
            super().__init__(_(
                "The mail template '%(identifier)s' has no content for language %(language)s."
            ) % {'identifier': identifier, 'language': language})
        else:
            super().__init__(_(
                "The mail template '%(identifier)s' has no content."
            ) % {'identifier': identifier})


class UnknownLanguage(Exception):
    def __init__(self, language) -> None:
        super().__init__(_(
            "The language '%(language)s' is not defined in settings.LANGUAGES."
        ) % {'language': language})
