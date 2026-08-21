"""
Supervisor Agent (Health Checker & Inter-Agent Communicator)
------------------------------------------------------------
Este agente supervisa el estado de salud de todos los módulos/agentes del sistema Bot-Bip.
Si detecta una falla:
1. Notifica por consola / logs la falla específica.
2. Comunica el diagnóstico a los demás agentes.
3. Genera un reporte detallado y pide aprobación al usuario antes de ejecutar la solución.
"""

import sys
import os
import requests
from typing import Dict, Any

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db.supabase_client import check_db_connection
except ImportError:
    check_db_connection = None



class HealthSupervisorAgent:
    def __init__(self):
        self.reports = []

    def check_database_agent(self) -> Dict[str, Any]:
        """Comprueba el estado del Database & Security Agent."""
        if check_db_connection is None:
            return {
                "agent": "Database & Security Agent",
                "status": "FAIL",
                "details": "Faltan librerías requeridas ('supabase' o 'python-dotenv').",
                "proposed_fix": "Ejecutar `pip install -r requirements.txt` o activar el entorno virtual."
            }
        try:
            connected = check_db_connection()

            if connected:
                return {"agent": "Database & Security Agent", "status": "OK", "details": "Conexión a Supabase correcta."}
            else:
                return {
                    "agent": "Database & Security Agent",
                    "status": "FAIL",
                    "details": "No se pudo conectar a la base de datos de Supabase. Revisa SUPABASE_URL y SUPABASE_KEY en .env.",
                    "proposed_fix": "Verificar validez de las credenciales en .env o el estado de la tabla registros_diarios."
                }
        except Exception as e:
            return {
                "agent": "Database & Security Agent",
                "status": "FAIL",
                "details": f"Error inesperado al probar Supabase: {str(e)}",
                "proposed_fix": "Revisar la configuración de red y librerías de supabase."
            }

    def check_telegram_bot_agent(self) -> Dict[str, Any]:
        """Comprueba el estado del Telegram Bot Agent."""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return {
                "agent": "Telegram Bot Agent",
                "status": "FAIL",
                "details": "Falta la variable TELEGRAM_BOT_TOKEN en el entorno.",
                "proposed_fix": "Añadir TELEGRAM_BOT_TOKEN válido en el archivo .env."
            }

        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200 and res.json().get("ok"):
                bot_info = res.json().get("result", {})
                return {
                    "agent": "Telegram Bot Agent",
                    "status": "OK",
                    "details": f"Bot activo en Telegram (@{bot_info.get('username')})."
                }
            else:
                return {
                    "agent": "Telegram Bot Agent",
                    "status": "FAIL",
                    "details": f"Respuesta inválida de Telegram API (código {res.status_code}). Token erróneo.",
                    "proposed_fix": "Obtener un nuevo token válido desde @BotFather en Telegram y actualizar .env."
                }
        except Exception as e:
            return {
                "agent": "Telegram Bot Agent",
                "status": "FAIL",
                "details": f"Error de conexión con Telegram API: {str(e)}",
                "proposed_fix": "Verificar la conexión a Internet o el estado de los servidores de Telegram."
            }

    def check_dashboard_agent(self) -> Dict[str, Any]:
        """Comprueba el estado del Dashboard Agent."""
        dashboard_app = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dashboard", "app.py")
        if not os.path.exists(dashboard_app):
            return {
                "agent": "Dashboard Agent",
                "status": "FAIL",
                "details": "El archivo dashboard/app.py no existe.",
                "proposed_fix": "Reconstruir dashboard/app.py para la interfaz Streamlit."
            }
        return {"agent": "Dashboard Agent", "status": "OK", "details": "Script dashboard/app.py encontrado y listo."}

    def run_health_check(self) -> bool:
        """Ejecuta la supervisión completa de todos los agentes."""
        print("🔍 [SUPERVISOR AGENT] Iniciando diagnóstico del sistema Bot-Bip...\n")
        
        results = [
            self.check_database_agent(),
            self.check_telegram_bot_agent(),
            self.check_dashboard_agent()
        ]

        failures = [r for r in results if r["status"] == "FAIL"]

        for r in results:
            symbol = "✅" if r["status"] == "OK" else "❌"
            print(f"{symbol} [{r['agent']}] {r['details']}")

        if not failures:
            print("\n🎉 Todos los agentes operan correctamente.")
            return True

        print("\n⚠️ [SUPERVISOR AGENT] ¡Se han detectado fallos en los agentes!")
        print("📢 Comunicando el diagnóstico entre los agentes y preparando informe para el usuario...\n")

        for f in failures:
            print("----------------------------------------------------------------------")
            print(f"🚨 PROBLEMA DETECTADO en {f['agent']}")
            print(f"📄 Detalles: {f['details']}")
            print(f"💡 SOLUCIÓN PROPUESTA: {f['proposed_fix']}")
            print("----------------------------------------------------------------------")

        print("\n🛑 ATENCIÓN AL USUARIO:")
        print("Antes de aplicar cualquier corrección, se requiere tu autorización.")
        return False


if __name__ == "__main__":
    supervisor = HealthSupervisorAgent()
    supervisor.run_health_check()
