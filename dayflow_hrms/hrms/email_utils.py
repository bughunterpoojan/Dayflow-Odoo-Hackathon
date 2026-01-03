from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_styled_mail(subject, plain_text, recipients, template_name='email/styled_email.html', context=None, from_email=None):
    """Render an HTML email using the project's email template and send it.

    - `plain_text` is used as the text fallback.
    - `recipients` is a list of recipient addresses.
    - `context` is merged with `title` and `content` for rendering.
    """
    if context is None:
        context = {}
    context = context.copy()
    context.setdefault('title', subject)
    context.setdefault('content', plain_text)

    html_message = render_to_string(template_name, context)

    # Use Django's send_mail with html_message fallback
    send_mail(subject, plain_text, from_email, recipients, html_message=html_message)
