import requests
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class TUAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if settings.MOCK_API:
            if username and password == "tu1234":
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_unusable_password()
                    user.first_name = "สมชาย"
                    user.last_name = "ทดสอบ"
                user.email = getattr(settings, 'EMAIL_HOST_USER', f"{username}@dome.tu.ac.th")
                # superuser ให้ role ADMIN อัตโนมัติ
                if user.is_superuser and user.role == 'LECTURER':
                    user.role = 'ADMIN'
                user.save()
                return user
            return None

        # Real TU REST API Authentication
        try:
            response = requests.post(
                settings.TU_API_URL,
                json={"UserName": username, "PassWord": password},
                headers={
                    "Content-Type": "application/json",
                    "Application-Key": settings.TU_APP_KEY,
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') is True:
                    user, created = User.objects.get_or_create(username=username)
                    user.set_unusable_password()
                    user.first_name = data.get('displayname_th', '')
                    user.last_name = f"({data.get('displayname_en', '')})"
                    user.email = data.get('email', f"{username}@tu.ac.th")
                    if created and data.get('type') == 'employee':
                        user.role = 'LECTURER'
                    if user.is_superuser and user.role == 'LECTURER':
                        user.role = 'ADMIN'
                    user.save()
                    return user

        except Exception:
            pass

        return None
