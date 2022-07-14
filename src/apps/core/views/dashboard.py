from django.shortcuts import render
from django.views import View
from apps.core.consts import ProfileStepsEnum

from apps.core.outside_db.services import get_user_message_count


class DashboardView(View):
    template_name = "dashboard.html"

    def get(self, request):
        user = request.user
        # TODO select all in single query
        daily_message_count = get_user_message_count(
            user.twillion_number, "day"
        )
        monthly_message_count = get_user_message_count(
            user.twillion_number, "month"
        )
        yearly_message_count = get_user_message_count(
            user.twillion_number, "year"
        )
        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                "daily": daily_message_count,
                "monthly": monthly_message_count,
                "yearly": yearly_message_count,
            },
        )

    @property
    def base_context(self):
        return {
            "title": "Dashboard", 
            "navname": "Dashboard",
            "step" : ProfileStepsEnum.DASHBOARD.value
        }
