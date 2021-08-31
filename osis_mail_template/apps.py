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
from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy as _


class OsisMailTemplateConfig(AppConfig):
    name = 'osis_mail_template'
    verbose_name = _("Mail templates")

    def ready(self):
        # This loads mail_templates.py from each app for registration
        autodiscover_modules('mail_templates')

        # Add custom CKEditor config
        settings.CKEDITOR_CONFIGS['osis_mail_template'] = {
            'linkShowTargetTab': False,
            'linkShowAdvancedTab': False,
            'extraPlugins': ','.join(['pastefromword']),
            'toolbar': 'Custom',
            'toolbar_Custom': [
                {'name': 'clipboard', 'items': ['PasteFromWord', '-', 'Undo', 'Redo']},
                ['Bold', 'Italic', 'Underline'],
                ['NumberedList', 'BulletedList', '-', 'Blockquote'],
                ['Link', 'Unlink'],
                {'name': 'insert', 'items': ['Table']},
            ],
        }
