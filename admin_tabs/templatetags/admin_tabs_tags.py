# -*- coding: utf-8 -*-
from django import template
from django.contrib.admin.helpers import Fieldset, InlineAdminFormSet
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured

register = template.Library()

@register.simple_tag(takes_context=True)
def render_fieldsets_for_admincol(context, admin_col):
    """
    Render the fieldsets and inlines of a col.
    """
    out = ""
    admin_form = context['adminform']
    if not 'request' in context:
        raise ImproperlyConfigured(
               '"request" missing from context. Add django.core.context_processors.request to your TEMPLATE_CONTEXT_PROCESSORS')
    request = context['request']
    obj = context.get('original', None)
    fieldsets = admin_col.get_elements(request, obj, include_inlines=True)
    readonly_fields = admin_form.model_admin.get_readonly_fields(request, obj)
    template = "admin/includes/fieldset.html"
    # Make a dict matching to retrieve inline_admin_formsets
    # {"inline class name": inline_formset_instance}
    inline_matching = dict((inline.opts.__class__.__name__, inline) for inline in context["inline_admin_formsets"])
    for name, options in fieldsets:
        if "fields" in options:
            f = Fieldset(admin_form.form, name,
                readonly_fields=readonly_fields,
                model_admin=admin_form.model_admin,
                **options
            )
            context["fieldset"] = f
            out += render_to_string(template, context)
        elif "inline" in options:
            try:
                inline_admin_formset = inline_matching[options["inline"]]
                context["inline_admin_formset"] = inline_admin_formset
                out += render_to_string(inline_admin_formset.opts.template, context)
            except KeyError:  # The user does not have the permission
                pass
    return out

