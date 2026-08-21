import os
import logging
from datetime import date
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseManager:
    """
    Agente de Base de Datos y Supabase Helper.
    Administra la conexión segura a Supabase soportando Service Role y Anon Key.
    """
    def __init__(self, use_service_role: bool = False):
        self.url: str = os.getenv("SUPABASE_URL", "")
        self.anon_key: str = os.getenv("SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_SECRET_KEY", "")

        if not self.url:
            raise ValueError("Error: SUPABASE_URL no está configurada en las variables de entorno.")

        # Selección de clave según responsabilidad de agente
        if use_service_role and self.service_role_key:
            self.key = self.service_role_key
            logger.info("Conectando a Supabase usando Service Role / Secret Key.")
        elif self.anon_key:
            self.key = self.anon_key
            logger.info("Conectando a Supabase usando Anon / Publishable Key.")
        else:
            raise ValueError("Error: No se encontró una clave API válida de Supabase.")

        self.client: Client = create_client(self.url, self.key)

    def guardar_registro_diario(
        self,
        user_id: int,
        energia: int,
        humor: int,
        sueno_horas: float = 8.0,
        comentarios: str = "",
        fecha_registro: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Inserta o actualiza (upsert) un registro diario de energía, humor, horas de descanso y comentarios.
        """
        fecha_str = (fecha_registro or date.today()).isoformat()

        from datetime import datetime
        data = {
            "user_id": user_id,
            "fecha": fecha_str,
            "energia": energia,
            "humor": humor,
            "sueno_horas": sueno_horas,
            "comentarios": comentarios,
            "created_at": datetime.now().isoformat()
        }

        try:
            # Upsert utilizando la restricción única (user_id, fecha)
            response = self.client.table("registros_diarios").upsert(
                data, on_conflict="user_id,fecha"
            ).execute()
            logger.info(f"Registro diario guardado exitosamente para usuario {user_id} en fecha {fecha_str}.")
            return {"success": True, "data": response.data}
        except Exception as e:
            err_msg = str(e)
            if "sueno_horas" in err_msg or "PGRST204" in err_msg:
                logger.warning("La columna 'sueno_horas' aún no existe en Supabase. Guardando sin la columna sueno_horas...")
                data_legacy = data.copy()
                data_legacy.pop("sueno_horas", None)
                try:
                    res_legacy = self.client.table("registros_diarios").upsert(
                        data_legacy, on_conflict="user_id,fecha"
                    ).execute()
                    return {"success": True, "data": res_legacy.data}
                except Exception as e2:
                    return {"success": False, "error": str(e2)}

            logger.error(f"Error al guardar registro en Supabase: {err_msg}")
            return {"success": False, "error": err_msg}

    def obtener_registros(
        self,
        user_id: Optional[int] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Consulta el histórico de registros filtrando por usuario y/o rango de fechas.
        """
        try:
            query = self.client.table("registros_diarios").select("*")

            if user_id is not None:
                query = query.eq("user_id", user_id)
            if fecha_inicio:
                query = query.gte("fecha", fecha_inicio)
            if fecha_fin:
                query = query.lte("fecha", fecha_fin)

            # Ordenar por fecha descendente por defecto
            query = query.order("fecha", desc=True)
            response = query.execute()

            return response.data or []
        except Exception as e:
            logger.error(f"Error al consultar registros de Supabase: {str(e)}")
            return []

    def obtener_usuarios_unicos(self) -> List[int]:
        """
        Devuelve la lista de IDs de usuarios únicos registrados.
        """
        try:
            response = self.client.table("registros_diarios").select("user_id").execute()
            if response.data:
                usuarios = list({item["user_id"] for item in response.data if "user_id" in item})
                return usuarios
            return []
        except Exception as e:
            logger.error(f"Error al obtener usuarios únicos: {str(e)}")
            return []

    def guardar_contacto_emergencia(self, user_id: int, nombre: str, telefono: str, relacion: str = "Red de Apoyo") -> Dict[str, Any]:
        """Guarda un contacto de confianza en la red de apoyo del usuario."""
        try:
            data = {
                "user_id": user_id,
                "nombre": nombre,
                "telefono": telefono,
                "relacion": relacion
            }
            response = self.client.table("contactos_emergencia").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            logger.error(f"Error al guardar contacto de emergencia: {str(e)}")
            return {"success": False, "error": str(e)}

    def obtener_contactos_emergencia(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene la lista de contactos de confianza de un usuario."""
        try:
            response = self.client.table("contactos_emergencia").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error al obtener contactos de emergencia: {str(e)}")
            return []


# Instancia por defecto para importar fácilmente
def get_db_client(use_service_role: bool = False) -> SupabaseManager:
    return SupabaseManager(use_service_role=use_service_role)

def check_db_connection() -> bool:
    """Verifica la conectividad básica con Supabase."""
    try:
        url = os.getenv("SUPABASE_URL", "")
        key = (
            os.getenv("SUPABASE_ANON_KEY", "")
            or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
            or os.getenv("SUPABASE_SECRET_KEY", "")
        )
        if not url or not key:
            return False
        client = create_client(url, key)
        # Intento de consulta ligera
        client.table("registros_diarios").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"DEBUG SUPABASE ERROR: {type(e).__name__} - {str(e)}")
        return False

