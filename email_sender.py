import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    def __init__(self, host: str, port: int, user: str, app_password: str):
        self.host = host
        self.port = port
        self.user = user
        self.app_password = app_password

    def send(self, from_addr: str, to_addr: str, subject: str, html_body: str) -> None:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(self.host, self.port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.user, self.app_password)
            server.sendmail(from_addr, to_addr, msg.as_string())
