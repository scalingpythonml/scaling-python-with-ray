from django import template


register = template.Library()


@register.inclusion_tag("templatetags/bootstrap_save_form.html")
def bootstrap_save_form(form, action, action_button_name="Save"):
    return {"form": form, "action": action, "button_name": action_button_name}
