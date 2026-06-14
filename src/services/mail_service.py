# IMPORTS
import os
import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

# CLASS: MAIL CONFIGURATION ERROR
class MailConfigurationError(RuntimeError):
    pass

# FUNCTION: CHECK FLAG
def env_flag(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

# FUNCTION: GET SMTP SETTINGS
def get_smtp_settings():

    # GET SMTP SETTINGS
    settings = {
        "host": os.getenv("SMTP_HOST"),
        "port": os.getenv("SMTP_PORT"),
        "username": os.getenv("SMTP_USERNAME"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("SMTP_FROM_EMAIL"),
        "from_name": os.getenv("SMTP_FROM_NAME", "kanbun"),
        "use_tls": env_flag("SMTP_USE_TLS", True),
        "use_ssl": env_flag("SMTP_USE_SSL", False),
    }

    # STOP, IF REQUIRED SETTINGS ARE MISSING
    if not all([ settings["host"], settings["port"], settings["username"], settings["password"], settings["from_email"]]):

        # RAISE ERROR
        raise MailConfigurationError("SMTP ENVIRONMENT VARIABLES ARE MISSING OR INVALID")

    # RETURN SETTINGS
    return settings


# FUNCTION: SEND 2FA EMAIL
def send_two_factor_code_email(user, code):

    # GET SMTP SETTINGS
    settings = get_smtp_settings()

    # BUILD MESSAGE
    message = EmailMessage()
    message["Subject"] = "Your kanbun sign-in code"
    message["From"] = f'{settings["from_name"]} <{settings["from_email"]}>'
    message["To"] = user.email
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=settings["from_email"].split("@", 1)[-1])

    # DEFINE MESSAGE CONTENT
    message.set_content(
        "Use this code to finish signing in to kanbun:\n\n" 
        f"{code}\n\n"
        "This code expires in 10 minutes."
    )

    # CONNECT AND SEND
    smtp_class = smtplib.SMTP_SSL if settings["use_ssl"] else smtplib.SMTP

    # SMPT CLASS
    with smtp_class(settings["host"], int(settings["port"])) as server:

        # CHECK FOR TLS SETTINGS
        if settings["use_tls"] and not settings["use_ssl"]:

            # START TLS
            server.starttls()

        # LOGIN TO SERVER
        server.login(settings["username"], settings["password"])

        # SEND MESSAGE
        server.send_message(
            message,
            from_addr=settings["from_email"],
            to_addrs=[user.email],
        )
