from django import template


register = template.Library()


@register.inclusion_tag("templatetags/form_with_helpers.html")
def form_with_helpers(form, action, action_button_name="Create account"):
    return {"form": form, "action": action, "button_name": action_button_name}
