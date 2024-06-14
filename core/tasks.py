from celery import shared_task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()


@shared_task
def send_contact_us_emails_to_admin(admin_ids, vars):
    try:
        admins = User.objects.filter(
            id__in=admin_ids,
            user_type=User.UserType.ADMINISTRATOR,
            is_active=True,
        )

        context = {
            "current_site": Site.objects.get_current(),
            "protocol": "http",
            "title": "Contact Us Submission",
        }
        context.update(vars)
        template = "core/email/contact_us.html"
        html_content = render_to_string(template, context)
        text_content = strip_tags(html_content)

        recipients = [admin.email for admin in admins]
        send_mail(
            subject="Nexus - Contact Us Submission Notification",
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
            html_message=html_content,
        )
    except Exception as e:
        return f"Error sending contact us emails: {str(e)}"
