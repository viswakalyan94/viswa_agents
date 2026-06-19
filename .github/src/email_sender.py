import smtplib
from email.message import EmailMessage

def send_email(sender, password, receiver, subject, html_file):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    msg.set_content("Attached SQL analysis report.")

    with open(html_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="html",
            filename="report.html"
        )

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('viswak57@gmail.com', 'Nikki143$visu')
        smtp.send_message(msg)