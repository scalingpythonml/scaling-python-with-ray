from datetime import date
from typing import Literal

from django.conf import settings
from django.utils import timezone

from sqlalchemy import create_engine, extract, or_, select
from sqlalchemy.orm import sessionmaker

from .models import SmsItem


engine = create_engine(settings.OUTSIDE_DATA_NETLOC)

Session = sessionmaker(engine)

user_messages_filter = lambda twillion_number: or_(
    SmsItem.sender_phone_number == twillion_number,
    SmsItem.recipient_phone_number == twillion_number,
)


def get_user_message_count(
    twillion_number: str, period: Literal["day", "month", "year"]
):
    period_condition = getattr(timezone.now(), period)
    with Session() as session:
        count = (
            session.query(SmsItem)
            .where(
                user_messages_filter(twillion_number),
                extract(period, SmsItem.sms_date) == period_condition,
            )
            .count()
        )
        session.close()

    return count
