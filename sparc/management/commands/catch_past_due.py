import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.urls import reverse

from sparc.models import Notification, TranchePayment

User = get_user_model()


class Command(BaseCommand):
    help = "Catches existing past-due tranches and creates notifications"

    def handle(self, *args, **kwargs):
        today = datetime.date.today()

        admin_users = list(User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)))

        overdue_payments = TranchePayment.objects.filter(
            expected_date__lt=today,
            status='Pending',
            past_due_notified=False,
        ).select_related('tranche_record')

        count = 0
        for payment in overdue_payments:
            notifications = [
                Notification(
                    user=admin,
                    message=(
                        f"⚠️ PAST DUE: Tranche #{payment.tranche_number}"
                        f" for {payment.tranche_record.project_name}"
                        f" was due on {payment.expected_date}"
                    ),
                    notification_type='warning',
                    link=reverse('view_tranche', args=[payment.tranche_record.id]),
                )
                for admin in admin_users
            ]
            Notification.objects.bulk_create(notifications)

            payment.past_due_notified = True
            payment.save()
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Caught and notified {count} past-due tranche(s)."
            )
        )
