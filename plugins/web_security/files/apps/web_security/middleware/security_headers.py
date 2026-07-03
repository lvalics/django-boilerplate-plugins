from apps.web_security.models import SecuritySettings


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to responses.

    Adds common security headers to help protect against
    various web attacks.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Get security settings
        settings = SecuritySettings.get_settings()

        # Check if security headers are enabled
        if not settings.security_enabled or not settings.security_headers_enabled:
            return response

        # Add security headers
        # Prevent clickjacking
        if "X-Frame-Options" not in response:
            response["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        if "X-Content-Type-Options" not in response:
            response["X-Content-Type-Options"] = "nosniff"

        # Disable legacy XSS filter (deprecated, can introduce vulnerabilities in
        # legacy browsers); rely on Content-Security-Policy instead.
        if "X-XSS-Protection" not in response:
            response["X-XSS-Protection"] = "0"

        # Referrer policy
        if "Referrer-Policy" not in response:
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (formerly Feature-Policy)
        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = (
                "accelerometer=(), camera=(), geolocation=(), "
                "gyroscope=(), magnetometer=(), microphone=(), "
                "payment=(), usb=()"
            )

        return response
