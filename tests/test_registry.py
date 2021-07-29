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

from django.test import SimpleTestCase

from osis_mail_template.exceptions import (
    DuplicateMailTemplateIdentifier,
    UnknownMailTemplateIdentifier,
)
from osis_mail_template.registry import MailTemplateRegistry, Token


class MailTemplateRegistryTest(SimpleTestCase):
    IDENTIFIER = 'test-mail-template'

    def setUp(self):
        self.registry = MailTemplateRegistry()

    def test_registry_registers_and_unregisters(self):
        token = Token('test-token', 'Example token', 'value')
        self.registry.register(self.IDENTIFIER, "My awesome template", [token])
        self.assertIn(self.IDENTIFIER, self.registry.get_mail_templates())
        self.assertEqual([token], self.registry.get_tokens(self.IDENTIFIER))
        self.assertEqual("My awesome template", self.registry.get_description(self.IDENTIFIER))
        self.assertIn('test-token', self.registry.get_example_values(self.IDENTIFIER))
        self.registry.unregister(self.IDENTIFIER)
        self.assertNotIn(self.IDENTIFIER, self.registry.get_mail_templates())

    def test_cant_register_twice(self):
        token = Token('test-token', 'Example token', 'value')
        self.registry.register(self.IDENTIFIER, "My awesome template", [token])
        with self.assertRaises(DuplicateMailTemplateIdentifier):
            self.registry.register(self.IDENTIFIER, "My other template", [])

    def test_cant_unregister_bad_identifier(self):
        with self.assertRaises(UnknownMailTemplateIdentifier):
            self.registry.unregister('bad-identifier')
        with self.assertRaises(UnknownMailTemplateIdentifier):
            self.registry.get_tokens('bad-identifier')

    def test_get_list_by_tag_is_sorted(self):
        token = Token("test-token", "Example token", "value")
        self.registry.register(self.IDENTIFIER, "My awesome template", [token], tag="Last")
        self.registry.register('test-other-template', "My other template", [token], tag="First")

        self.assertListEqual(["First", "Last"], list(self.registry.get_list_by_tag().keys()))
