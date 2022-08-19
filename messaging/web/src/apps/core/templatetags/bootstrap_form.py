from django import template


register = template.Library()


@register.inclusion_tag("templatetags/bootstrap_form.html")
def bs_form(form, action, action_button_name="Next"):
    return {"form": form, "action": action, "button_name": action_button_name}
