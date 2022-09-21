from django import template


register = template.Library()


@register.inclusion_tag("templatetags/login_form.html")
def login_form(form, action, action_button_name="Log in"):
    return {"form": form, "action": action, "button_name": action_button_name}
