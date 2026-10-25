import smtplib

USUARIO = "cristianhernandez.ipedep@gmail.com"      
CLAVE = "vidr ffgq stli itmp"           
try:
    servidor = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
    print("1. Conectado")
    servidor.starttls()
    print("2. Conexión cifrada")
    servidor.login(USUARIO, CLAVE)
    print("3. Inicio de sesión correcto")
    servidor.quit()
except Exception as error:
    print("FALLÓ:", type(error).__name__, "-", error)