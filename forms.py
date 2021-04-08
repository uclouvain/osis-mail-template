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
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils.translation import gettext_lazy as _

from osis_mail_template.models import MailTemplate


class MailTemplateConfigureForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        fields = [
            'subject',
            'body',
        ]
        widgets = {
            'body': CKEditorWidget(config_name='osis_mail_template')
        }

    def check_tokens(self, field):
        from osis_mail_template import templates

        tokens = templates.get_example_values(self.instance.identifier)
        data = self.cleaned_data[field]
        try:
            data.format(**tokens)
        except KeyError as e:
            raise forms.ValidationError(
                _("The token '%(token)s' is not specified, please use only valid tokens from the list.") % {
                    'token': e.args[0],
                }
            )
        return data

    def clean_subject(self):
        return self.check_tokens('subject')

    def clean_body(self):
        return self.check_tokens('body')
