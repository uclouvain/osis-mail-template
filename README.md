OSIS Mail Template
==================

`OSIS Mail Template` is a Django application to manage mail templates across
OSIS platform.

Requirements
============

`OSIS Mail Template` requires:
  * Django 2.2+
  * django-ckeditor 5+
  * html2text
  * django-bootstrap3
  * django-autocomplete-light 3.5.1+


How to install ?
================

## For production

```bash
# From your osis install, with python environment activated
pip install git+https://github.com/uclouvain/osis-mail-template.git@dev#egg=osis_mail_template
```

## For development

```bash
# From your osis install, with python environment activated
git clone git@github.com:uclouvain/osis-mail-template.git
pip install -e ./osis-mail-template
```


Configuring Django
------------------

Add `osis_mail_template` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = (
    ...
    'osis_mail_template',
    ...
)
```

Using OSIS Mail Template
========================

`osis_mail_template` is based on the idea that you register mail templates
within a Django application. Each mail template subject and content will then be
configurable through a common interface. An email template consists of an
identifier and a list of token, each token maps a name with a description, and
an example value.

Declaring a mail template
-------------------------

To declare a mail template within a Django application:

* Create a package, **called `mail_templates`**, at the root of the app :

```
 <app_name>
 | api
     |__ #...
 | #...
 | mail_templates.py
```

* Register as many mail templates as you want, it is advised to use constants
  for mail template identifiers to prevent mismatching, and specify a tag to
  find easily the mail in administration. 

```python
from django.utils.translation import gettext_lazy as _
from osis_mail_template import templates, Token

OSIS_ADMISSION_MAIL_CREATE = 'osis-admission-creation'
templates.register(
    OSIS_ADMISSION_MAIL_CREATE,
    description=_("A short description about the mail template and when it is sent"),
    tokens=[
      Token(
          name='person_first_name',
          description=_("The first name of the person concerned by the admission"),
          example="John",
      ),
      Token(
        'person_last_name',
        _("The last name of the person concerned by the admission"),
        "Doe",
      ),
    ],
    tag='Admission',
)
```

* To prevent mail which templates have not been configured, it is strongly recommended creating a migration to initialize the content of a newly registered mail template:

```python
from django.db import migrations
from osis_mail_template import MailTemplateMigration

from myapp.mail_templates import MY_TEMPLATE_IDENTIFIER

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
        ...
    ]

    operations = [
        MailTemplateMigration(MY_TEMPLATE_IDENTIFIER, subjects, contents)
    ]
```

Configuring mail templates
--------------------------

As soon as a mail template is declared, it can be configured for both French and
English in the administration.

A list of all mail template is available for users who have the
permission `osis_mail_template.configure`, with the option to configure or preview a
mail template :

* when configuring, 2 forms (one for each language) with the list of tokens will
  be made available.
* when previewing, the mail template will be rendered with example values from
  the tokens

If a mail template is registered twice with same identifier, a
`DuplicateMailTemplateIdentifier` exception will be thrown.


Rendering a mail template
-------------------------

Upon an action of its choosing, the calling module can render a mail template
with the function `generate_email(mail_template_id, language, tokens, recipients, sender)`
. It will return an EmailMessage object ready to be sent through.

The following parameters are expected:

* `mail_template_id` is the mail template identifier as declared somewhere in
  a `mail_templates.py` file, will raise an `UnknownMailTemplateIdentifier`
  exception if the mail template does not exist
* `tokens` is a dictionary mapping token names to their value. Keys must
  reference all tokens declared, if any is missing, it will raise a
  `MissingToken` exception. Values must be a string or a lazy string, if not,
  it wil raise a `TypeError`
* `recipients` is a list of email as strings to send the email to
* `language` is a language identifier from `settings.LANGUAGES`, will raise
  an `UnknownLanguage` exception if the language does not exist
* `sender` is the e-mail for the sender, if not specified, will default
  to `settings.DEFAULT_FROM_EMAIL`

If the configured email template is not yet configured (has no content),
an `EmptyMailTemplateContent` exception will be thrown.

Overriding the HTML email base template
---------------------------------------

The HTML configured through the editor is, at rendering, injected into a base
template located at `osis_mail_template/base_email.html` in which the content is
located inside the `content` variable.

For the plain text alternative, the HTML content is passed through
the `html2text` function configured will the following parameters:

* `LINKS_EACH_PARAGRAPH = True` for putting links after every paragraph
* `BODY_WIDTH = 120` for wrapping long lines
* `INLINE_LINKS = False` to put links at the end of the text
* `WRAP_LINKS = False` to prevent link wrapping
* `WRAP_LIST_ITEMS = True` to allow list item wrapping
* `USE_AUTOMATIC_LINKS = True` to simplify self-targeted links

Getting only the rendered content
---------------------------------

It may be useful to get only the content of the subject and body of a mail
message, prior to sending it, so that the user can modify the contents. OSIS
Mail template allows that by providing
a `render_email_content(mail_template_id, language, tokens)` function, which returns a
tuple of subject and content.

This can be later used in a form for sending customized content by the user.

Getting a selector of mail templates
------------------------------------

It may be useful to offer the front-end user the possibility to select the mail template.
OSIS Mail template allows that by providing autocomplete views, usable with a
`ListSelect2` widget from django-autocomplete-light.

```python
from  django import forms
from dal import autocomplete, forward

class MailTemplateConfigureForm(forms.Form):
    # Example for autocompleting on all templates
    template = forms.CharField(
        widget=autocomplete.ListSelect2(url="osis_mail_template:autocomplete")
    )
    # Example for autocompleting on templates for a selected tag
    template_filtered_by_tag = forms.CharField(
        widget=autocomplete.ListSelect2(
          url="osis_mail_template:autocomplete",
          forward=(forward.Const('tag', 'Admission'),)
        )
    )
```

This can be later used in the form for sending customized content by the user.

