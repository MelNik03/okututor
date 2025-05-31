from firebase_functions import auth_fn, firestore_fn
from firebase_admin import initialize_app
import smtplib
from email.mime.text import MIMEText

initialize_app()

@auth_fn.on_user_create()
def send_welcome_email(event):
    user = event.data
    email = user.email
    display_name = user.display_name or "User"

    msg = MIMEText(f"Hello, {display_name}! Thank you for registering on Okututor.")
    msg["Subject"] = "Welcome to Okututor!"
    msg["From"] = "your-email@gmail.com"
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your-email@gmail.com", "your-app-password")
        server.sendmail("your-email@gmail.com", email, msg.as_string())

    return {"status": "Email sent"}

@firestore_fn.on_document_create("courses/{courseId}")
def notify_new_course(event):
    course = event.data
    course_id = event.params["courseId"]
    title = course.get("title")

    # Здесь можно отправить уведомление (например, через email или FCM)
    print(f"New course created: {title} (ID: {course_id})")
    return {"status": "Notified"}