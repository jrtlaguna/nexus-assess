import pytz
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from ...tasks import send_contact_us_emails_to_admin
from ...utils import get_base_email_vars

User = get_user_model()


class ContactUsView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            name = request.data.get("name", "")
            email = request.data.get("email", "")
            subject = request.data.get("subject", "")
            message = request.data.get("message", "")

            if not all([name, email, message]):
                return Response(
                    {"error": "Name, Email, and Message fields are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Send email to administrators (convert time to EST)
            date_time_submitted_utc = timezone.now()
            date_time_submitted_est = date_time_submitted_utc.astimezone(
                pytz.timezone(settings.DEFAULT_TIMEZONE)
            )

            admins = User.objects.filter(
                user_type=User.UserType.ADMINISTRATOR, is_active=True
            )

            vars = get_base_email_vars()
            vars.update(
                {
                    "date_submitted": f"{date_time_submitted_est.strftime('%B %d, %Y %I:%M%p')} EST",
                    "name": name,
                    "email": email,
                    "subject": subject,
                    "message": message,
                }
            )

            send_contact_us_emails_to_admin.delay(
                list(admins.values_list("id", flat=True)),
                vars,
            )

            return Response(
                {"success": "Message sent successfully"}, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
