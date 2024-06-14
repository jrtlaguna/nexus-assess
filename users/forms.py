from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str, user_username
from dj_rest_auth.forms import AllAuthPasswordResetForm

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest

from core.utils import get_base_email_vars


class AllAuthPasswordResetForm(AllAuthPasswordResetForm):
    """
    Overridden the default form to send to the user using the frontend's password reset url
    """

    def save(self, request: HttpRequest, **kwargs) -> str:
        current_site = get_current_site(request)
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)
        for user in self.users:
            temp_key = token_generator.make_token(user)

            # send the password reset email
            domain = get_current_site(request).domain
            protocol = request.scheme

            # change to use frontend reset password url if needed
            url = (
                f"{protocol}://{domain}/password/reset/?uid={user_pk_to_url_str(user)}&token={temp_key}"
                if not settings.FRONTEND_URL
                else f"{settings.FRONTEND_URL}/password-reset/?uid={user_pk_to_url_str(user)}&token={temp_key}"
            )

            context = get_base_email_vars()
            context.update(
                {
                    "current_site": current_site,
                    "user": user,
                    "password_reset_url": url,
                    "request": request,
                }
            )
            if (
                app_settings.AUTHENTICATION_METHOD
                != app_settings.AuthenticationMethod.EMAIL
            ):
                context["username"] = user_username(user)
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )

        return self.cleaned_data["email"]
