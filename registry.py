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
from collections import OrderedDict
from typing import List, Dict, NamedTuple

from osis_mail_template.exceptions import (
    DuplicateMailTemplateIdentifier,
    UnknownMailTemplateIdentifier,
)

"""
A token describing a placeholder that will be replaced when rendering email content
"""
Token = NamedTuple('Token', [
    ('name', str),
    ('description', str),
    ('example', str),
])

"""
A template describing a message type
"""
Template = NamedTuple('Template', [
    ('identifier', str),
    ('description', str),
    ('tokens', List[Token]),
    ('tag', str),
])
Template._field_defaults = {'tag' : ''}


class MailTemplateRegistry:
    """
    The registry that contains mail templates.

    This is a singleton, you should use the 'templates' variable from osis_mail_template
    """
    templates = None

    def __init__(self) -> None:
        self.templates = {}

    def register(self, identifier: str, description: str, tokens: List[Token], tag: str = '') -> None:
        if identifier in self.templates:
            raise DuplicateMailTemplateIdentifier(identifier)
        self.templates[identifier] = Template(identifier, description, tokens, tag)

    def unregister(self, identifier: str) -> None:
        if identifier not in self.templates:
            raise UnknownMailTemplateIdentifier(identifier)
        del self.templates[identifier]

    def get_mail_templates(self) -> Dict[str, Template]:
        return self.templates

    def get_mail_template(self, identifier: str) -> Template:
        if identifier not in self.templates:
            raise UnknownMailTemplateIdentifier(identifier)
        return self.templates[identifier]

    def get_tokens(self, identifier: str) -> List[Token]:
        return self.get_mail_template(identifier).tokens

    def get_example_values(self, identifier: str) -> Dict[str, str]:
        return {t.name: t.example for t in self.get_mail_template(identifier).tokens}

    def get_description(self, identifier: str) -> str:
        return self.get_mail_template(identifier).description

    def get_list_by_tag(self) -> Dict[str, Dict[str, str]]:
        ret = OrderedDict()
        for template in sorted(self.templates.values(), key=lambda i: i.tag):
            if template.tag not in ret:
                ret[template.tag] = {}
            ret[template.tag][template.identifier] = template.description
        return ret
