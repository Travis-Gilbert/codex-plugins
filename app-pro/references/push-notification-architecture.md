# Push Notification Architecture

> FCM, APNs, Django integration, Celery tasks.

## Architecture Overview

```
Mobile App                    Backend (Django)              Push Service
    |                              |                           |
    |  Register device token       |                           |
    |  POST /api/v1/mobile/device/ |                           |
    |  {platform, token} --------->|                           |
    |                              |  Store DeviceRegistration |
    |                              |                           |
    |                              |  Event triggers push      |
    |                              |  (new connection, reminder)|
    |                              |                           |
    |                              |  Celery task: send_push   |
    |                              |  -----------------------> |
    |                              |                           |  FCM / APNs
    |  <---------------------------------------------------- |  Deliver
    |  Handle notification         |                           |
    |  (foreground / background)   |                           |
```

## Django Models

```python
class DeviceRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=10,
        choices=[("ios", "iOS"), ("android", "Android"), ("web", "Web")])
    token = models.TextField()
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "token")

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    object_slug = models.SlugField()
    remind_at = models.DateTimeField(db_index=True)
    message = models.CharField(max_length=200, blank=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
```

## Celery Tasks

```python
@shared_task
def send_push(user_id, title, body, data=None):
    devices = DeviceRegistration.objects.filter(
        user_id=user_id, is_active=True
    )
    for device in devices:
        if device.platform in ('ios', 'android'):
            send_fcm(device.token, title, body, data)
        elif device.platform == 'web':
            send_web_push(device.token, title, body, data)

@shared_task
def check_reminders():
    """Run every minute via Celery Beat."""
    due = Reminder.objects.filter(
        sent=False, remind_at__lte=timezone.now()
    ).select_related('user')
    for reminder in due:
        send_push.delay(
            reminder.user_id,
            "Reminder",
            reminder.message or f"Check: {reminder.object_slug}",
            {"type": "reminder", "slug": reminder.object_slug}
        )
        reminder.sent = True
        reminder.sent_at = timezone.now()
        reminder.save(update_fields=['sent', 'sent_at'])
```

## Client-Side (Expo)

```typescript
import * as Notifications from 'expo-notifications';

// Request permission
const { status } = await Notifications.requestPermissionsAsync();

// Get token
const token = await Notifications.getExpoPushTokenAsync({
  projectId: Constants.expoConfig?.extra?.eas?.projectId,
});

// Register with backend
await api.post('/mobile/device/register/', {
  platform: Platform.OS,
  token: token.data,
});

// Handle foreground notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Handle tap (deep link routing)
const subscription = Notifications.addNotificationResponseReceivedListener(
  (response) => {
    const { slug } = response.notification.request.content.data;
    router.push(`/object/${slug}`);
  }
);
```

## Web Push (VAPID)

```python
# Generate VAPID keys once
# pip install py-vapid
# vapid --gen

VAPID_PRIVATE_KEY = env('VAPID_PRIVATE_KEY')
VAPID_PUBLIC_KEY = env('VAPID_PUBLIC_KEY')
VAPID_CLAIMS = {"sub": "mailto:admin@example.com"}
```

Client registers via `PushManager.subscribe()` with the public key.
Server sends via `pywebpush` library.
