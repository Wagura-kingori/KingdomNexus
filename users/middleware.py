from django.shortcuts import redirect

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    
    EXEMPT = {
        "/force-password-change/",
        "/login/",
        "/logout/",
    }

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.user.must_change_password
            and request.path not in self.EXEMPT
            and not request.path.startswith("/static/")
            and not request.path.startswith("/admin/")
        ):
            return redirect("/force-password-change/")

        return self.get_response(request)