import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_password_email(to_email: str, new_password: str) -> None:
    sender = os.getenv("GMAIL_EMAIL")
    app_pw = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "SIRP - Recuperação de Senha"

    body = f"""SIRP - Recuperação de Senha

Olá,

Recebemos uma solicitação de recuperação de senha para sua conta.

Sua nova senha temporária é:

   {new_password}

Recomendamos alterá-la após o login acessando a página de Perfil.

Se você não solicitou esta alteração, ignore este email.
Sua conta permanece segura e ninguém mais teve acesso a ela.

Atenciosamente,
Equipe SIRP
"""
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_pw)
        server.sendmail(sender, [to_email], msg.as_string())
