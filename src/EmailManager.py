import smtplib
from email.message import EmailMessage
import mimetypes
import os
from src.email.envio_correo import credenciales_data_smtp
from pathlib import Path


def enviar_correo(smtp_info, destinatarios, asunto, cuerpo, ruta_excel):
    try:
        # Crear el mensaje
        msg = EmailMessage()
        msg["Subject"] = asunto
        msg["From"] = smtp_info['user_smtp']
        msg["To"] = ", ".join(destinatarios)
        msg.set_content(cuerpo)

        # Adjuntar el archivo Excel
        if os.path.exists(ruta_excel):
            with open(ruta_excel, "rb") as f:
                contenido = f.read()
                mime_type, _ = mimetypes.guess_type(ruta_excel)
                maintype, subtype = mime_type.split("/")
                msg.add_attachment(contenido, maintype=maintype, subtype=subtype, filename=os.path.basename(ruta_excel))
        else:
            print("El archivo no fue encontrado:", ruta_excel) 
            return

        # Conexión al servidor SMTP
        with smtplib.SMTP(smtp_info['server_smtp'], int(smtp_info['port_smtp'])) as smtp:
            smtp.starttls()  # Seguridad
            smtp.login(smtp_info['user_smtp'], smtp_info['pass_smtp'])
            smtp.send_message(msg)

        print("✅ Correo enviado exitosamente.")
        
    except Exception as e:
        print("❌ Error al enviar el correo:", e)

def preparar_correo():
    smtp_data = credenciales_data_smtp(id_unico=1)
    if not smtp_data:
        print("❌ No se pudo preparar el correo: credenciales inválidas.")
        return None, None, None, None, None

    smtp_info = {
        'server_smtp': smtp_data[0],
        'port_smtp': smtp_data[1],
        'user_smtp': smtp_data[2],
        'pass_smtp': smtp_data[3]
    }

    destinatarios = ['aprendiz.serviciosti@gruporeditos.com']
    asunto = 'Reporte Amazon Scraping'
    cuerpo = 'Hola,\n\nAdjunto encontrarás el archivo solicitado.\n\nSaludos.'
    ruta_excel = Path.home() / "Desktop" / "ScrapingWeb-main" / "productos_amazon.xlsx"

    return smtp_info, destinatarios, asunto, cuerpo, str(ruta_excel)
