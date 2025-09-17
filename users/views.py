from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import get_backends
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactForm
from django.conf import settings
from .models import ContactSubmission
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

from .forms import ContactForm
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = get_backends()[0]  # Choose the first backend in settings.py
            login(request, user, backend=backend.__class__.__module__ + "." + backend.__class__.__name__)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})



def features(request):
    return render(request, "users/features.html")

def pricing(request):
    return render(request, "users/pricing.html")

def about(request):
    return render(request, "users/about.html")




import logging

# Set up logging
logger = logging.getLogger(__name__)

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            # ✅ Save in DB
            ContactSubmission.objects.create(
                name=name,
                email=email,
                message=message
            )

            # Use DEFAULT_FROM_EMAIL as fallback if ADMIN_EMAIL is not set
            admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)

            try:
                # 📩 Email to Admin
                subject = f"📩 New Contact Form Submission from {name}"
                html_content = render_to_string("users/admin_email.html", {
                    "name": name,
                    "email": email,
                    "message": message
                })
                email_admin = EmailMultiAlternatives(
                    subject=subject,
                    body=message,  # Plain text fallback
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[admin_email],
                )
                email_admin.attach_alternative(html_content, "text/html")
                email_admin.send()

                # 📩 Auto-reply to User
                user_subject = "✅ Thanks for Contacting NeuroBuddy"
                html_user = render_to_string("users/user_reply.html", {
                    "name": name,
                })
                email_user = EmailMultiAlternatives(
                    subject=user_subject,
                    body=f"Hi {name}, thank you for contacting us. We will respond within 24 hours.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                email_user.attach_alternative(html_user, "text/html")
                email_user.send()

                # Success alert
                messages.success(request, "✅ Your message has been sent successfully!")
                
            except Exception as e:
                # Log the error but don't show it to the user
                logger.error(f"Email sending failed: {str(e)}")
                # Still show success message to user
                messages.success(request, "✅ Your message has been received! We'll get back to you soon.")
            
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "users/contact.html", {"form": form})