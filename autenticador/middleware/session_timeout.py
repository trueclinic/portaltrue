from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'AUTO_LOGOUT_DELAY', 5)  # minutos

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        try:
            last_activity = request.session['last_activity']
            elapsed = datetime.now() - datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")
            if elapsed > timedelta(minutes=self.timeout):
                logout(request)
                request.session.flush()
        except KeyError:
            pass

        request.session['last_activity'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.get_response(request)
