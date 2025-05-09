import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from app import create_db_connection


# Twilio configuration
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"  
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"    
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"  

# Email configuration
SMTP_SERVER = "smtp.gmail.com"  
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@example.com"  
EMAIL_PASSWORD = "your_email_password"    


def get_users_by_location():
    """
    Fetch users grouped by their location from the database.

    Returns:
        dict: A dictionary where keys are locations and values are lists of users in that location.
    """
    connection = create_db_connection()
    if not connection:
        return {}

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT full_name, email, phone, location FROM users")
        users = cursor.fetchall()

        # Group users by location
        users_by_location = {}
        for user in users:
            location = user['location']
            if location not in users_by_location:
                users_by_location[location] = []
            users_by_location[location].append(user)

        return users_by_location
    finally:
        connection.close()


def send_sms(phone_number, message):
    """
    Send an SMS to a user.

    Args:
        phone_number (str): The recipient's phone number.
        message (str): The message to send.
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )


def send_email(email_address, subject, message):
    """
    Send an email to a user.

    Args:
        email_address (str): The recipient's email address.
        subject (str): The email subject.
        message (str): The email body.
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email_address
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


def send_recommendations(recommendations):
    """
    Send recommendations to users based on their location.

    Args:
        recommendations (dict): A dictionary where keys are locations and values are recommendations.
    """
    users_by_location = get_users_by_location()

    for location, users in users_by_location.items():
        if location in recommendations:
            recommendation = recommendations[location]
            for user in users:
                # Send SMS
                if user['phone']:
                    try:
                        send_sms(user['phone'], recommendation)
                        print(f"SMS sent to {user['full_name']} at {user['phone']}")
                    except Exception as e:
                        print(f"Failed to send SMS to {user['phone']}. Error: {e}")

                # Send Email
                if user['email']:
                    try:
                        send_email(user['email'], f"Recommendation for {location}", recommendation)
                        print(f"Email sent to {user['full_name']} at {user['email']}")
                    except Exception as e:
                        print(f"Failed to send email to {user['email']}. Error: {e}")