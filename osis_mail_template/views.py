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
from dal import autocomplete
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import resolve_url
from django.utils.translation import gettext_lazy as _
from django.views import generic

from osis_mail_template.forms import MailTemplateConfigureForm
from osis_mail_template.models import MailTemplate
from osis_role.contrib.views import PermissionRequiredMixin


class MailTemplateListView(PermissionRequiredMixin, generic.TemplateView):
    template_name = 'osis_mail_template/list.html'
    permission_required = 'osis_mail_template.configure'

    def get_context_data(self, **kwargs):
        from osis_mail_template import templates

        context = super().get_context_data(**kwargs)
        context['tagged'] = templates.get_list_by_tag()
        return context


class MailTemplateChangeView(PermissionRequiredMixin, generic.FormView):
    forms = None
    template_name = 'osis_mail_template/change.html'
    permission_required = 'osis_mail_template.configure'

    def get_success_url(self) -> str:
        if self.request.POST.get('_preview'):
            return resolve_url('osis_mail_template:preview', identifier=self.kwargs['identifier'])
        return resolve_url('osis_mail_template:list')

    def get_forms(self, form_class=None):
        if not self.forms:
            identifier = self.kwargs['identifier']
            instances = MailTemplate.objects.get_by_id(identifier)
            self.forms = [
                MailTemplateConfigureForm(
                    data=self.request.POST or None,
                    instance=instance,
                    prefix=instance.language,
                )
                for instance in instances
            ]
        return self.forms

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if all(form.is_valid() for form in forms):
            for form in forms:
                form.save()
            messages.info(self.request, _("Mail template saved successfully."))
            return self.form_valid(forms)
        return self.form_invalid(forms)

    def form_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_context_data(self, **kwargs):
        from osis_mail_template import templates

        identifier = self.kwargs['identifier']

        kwargs['view'] = self
        kwargs['identifier'] = identifier
        kwargs['tokens'] = templates.get_tokens(identifier)
        kwargs['description'] = templates.get_description(identifier)

        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms()
        return kwargs


class MailTemplatePreview(PermissionRequiredMixin, generic.TemplateView):
    template_name = 'osis_mail_template/preview.html'
    permission_required = 'osis_mail_template.configure'

    def get_context_data(self, **kwargs):
        from osis_mail_template import templates

        context = super().get_context_data(**kwargs)
        identifier = self.kwargs['identifier']
        context['instances'] = MailTemplate.objects.get_by_id(identifier)
        context['description'] = templates.get_description(identifier)
        return context


class MailTemplateAutocomplete(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        from osis_mail_template import templates

        choices = templates.get_mail_templates().items()

        tag = self.forwarded.get('tag', None)
        if tag is not None:
            choices = filter(lambda couple: couple[1][2] == tag, choices)
        if self.q:
            choices = filter(lambda couple: self.q in couple[1][0], choices)
        choices = sorted(choices, key=lambda couple: couple[1][0])

        results = [{'id': value, 'text': template[0]} for value, template in choices]
        return JsonResponse({'results': results}, content_type='application/json')
