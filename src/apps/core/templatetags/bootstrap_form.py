from django import template


register = template.Library()


@register.inclusion_tag("templatetags/bootstrap_form.html")
def bs_form(form, action):
    return {"form": form, "action": action}
