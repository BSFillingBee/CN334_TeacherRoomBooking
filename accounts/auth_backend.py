import requests
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class TUAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if settings.MOCK_API:
            # Mock authentication matching the provided API structure
            if username and password == "tu1234":
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_unusable_password()
                    user.first_name = "สมชาย"
                    user.last_name = "ทดสอบ"
                    user.email = f"{username}@dome.tu.ac.th"
                    user.save()
                return user
            return None

        # Real TU REST API Authentication
        api_url = settings.TU_API_URL
        headers = {
            "Content-Type": "application/json",
            "Application-Key": settings.TU_APP_KEY
        }
        payload = {
            "UserName": username,
            "PassWord": password
        }

        try:
            print(f"--- TU API DEBUG ---")
            print(f"Attempting login for: {username}")
            print(f"API URL: {api_url}")
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            print(f"API Response Code: {response.status_code}")
            print(f"API Response Body: {response.text}") # ดูเนื้อหาที่ตอบกลับมาทั้งหมด
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == True:
                    print("Login Successful on TU API")
                    user, created = User.objects.get_or_create(username=username)
                    
                    # Update user info from documentation fields
                    user.set_unusable_password()
                    user.first_name = data.get('displayname_th', '')
                    user.last_name = f"({data.get('displayname_en', '')})"
                    user.email = data.get('email', f"{username}@tu.ac.th")
                    
                    if created and data.get('type') == 'employee':
                        user.role = 'LECTURER'
                    
                    user.save()
                    return user
                else:
                    print(f"TU API returned status=False: {data.get('message')}")
            
            elif response.status_code == 400:
                print("Error 400: User or Password Invalid from TU API")
            elif response.status_code == 403:
                print("Error 403: Application-Key is invalid or expired")
                
        except Exception as e:
            print(f"Connection Error: {str(e)}")
            
        return None
