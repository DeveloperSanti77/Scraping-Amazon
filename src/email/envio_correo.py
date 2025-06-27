from src.Fuji.get_data import get_datos_id


def credenciales_data_smtp(id_unico):
    smtp_info = get_datos_id(id_unico)

    try:
        server_smtp = smtp_info.get('server_smtp')
        port_smtp = smtp_info.get('port_smtp')
        user_smtp = smtp_info.get('user_smtp')
        pass_smtp = smtp_info.get('pass_smtp')  

        print("Credenciales SMTP obtenidas correctamente.")
        return server_smtp, port_smtp, user_smtp, pass_smtp

        
    except:
        print("No se encontraron datos SMTP para el ID proporcionado.")
    return None

credenciales_data_smtp(1)
