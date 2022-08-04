from django import template


register = template.Library()


@register.inclusion_tag("templatetags/bootstrap_steps_form.html")
def bootstrap_steps_form(
    form, action, action_button_name_1="Save", action_button_name_2="Next"
):
    return {
        "form": form,
        "action": action,
        "button_name_1": action_button_name_1,
        "button_name_2": action_button_name_2,
    }
