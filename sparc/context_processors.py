from .models import Notification


def notification_counts(request):
    """Return unread notifications for the current user."""
    if not request.user.is_authenticated:
        return {}

    unread_qs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')

    return {
        'notifications': unread_qs[:10],
        'unread_count': unread_qs.count(),
    }
