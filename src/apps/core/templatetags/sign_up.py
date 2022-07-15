from django import template


register = template.Library()


@register.inclusion_tag("templatetags/sign_up.html")
def sign_up(form, action, action_button_name="Create account", addition_btn="Add device"):
    return {"form": form, "action": action, "button_name": action_button_name, "second_button_name": addition_btn}
