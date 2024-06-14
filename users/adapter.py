from allauth.account.adapter import DefaultAccountAdapter

from core.utils import get_base_email_vars


class AccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        vars = get_base_email_vars()
        context.update(vars)
        super().send_mail(template_prefix, email, context)
