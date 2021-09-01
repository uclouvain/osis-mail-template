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

from django.db import migrations
from osis_mail_template import MailTemplateMigration

from ..mail_templates import MAIL_TEMPLATE_TEST_MAIL

subjects = {
  'en': '[OSIS] A dummy subject',
  'fr-be': '[OSIS] Un sujet bidon'
}
contents = {
  'en': '''<p>Hello {first_name} {last_name},</p>

<p>This is the mail template to notify you about {reason}.</p>

<p>---<br/>
The OSIS Team</p>
''',
  'fr-be': '''<p>Bonjour {first_name} {last_name},</p>

<p>Ceci est un template d'email à propos de {reason}.</p>

<p>---<br/>
L'équipe OSIS</p>
''',
}


class Migration(migrations.Migration):
    dependencies = [
        ('osis_mail_template', '0001_initial'),
    ]

    operations = [
        MailTemplateMigration(MAIL_TEMPLATE_TEST_MAIL, subjects, contents)
    ]
