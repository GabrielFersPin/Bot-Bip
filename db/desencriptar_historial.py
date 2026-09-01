"""
Script de migración para desencriptar comentarios antiguos en Supabase.
Si deseas des-encriptar todos los registros almacenados que comiencen por 'ENC::'
y dejarlos en texto plano en la base de datos, puedes ejecutar este script.
"""

import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migracion_desencriptar")

sys.path.insert(0, ".")
from db.supabase_client import get_db_client, decrypt_val

def desencriptar_historial_comentarios():
    try:
        db = get_db_client(use_service_role=True)
    except Exception as e:
        logger.error(f"Error al conectar con Supabase: {e}")
        return

    # Consultar todos los registros directamente de Supabase sin descifrado automático
    res = db.client.table("registros_diarios").select("id, user_id, fecha, comentarios").execute()
    registros = res.data or []
    
    logger.info(f"Se encontraron {len(registros)} registros diarios en total.")
    modificados = 0

    for r in registros:
        com_original = r.get("comentarios", "")
        if com_original and isinstance(com_original, str) and com_original.startswith("ENC::"):
            com_desencriptado = decrypt_val(com_original)
            reg_id = r["id"]
            
            # Actualizar el registro en la base de datos con el texto plano
            try:
                db.client.table("registros_diarios").update({
                    "comentarios": com_desencriptado
                }).eq("id", reg_id).execute()
                
                modificados += 1
                logger.info(f"✅ Registro {reg_id} (Fecha: {r.get('fecha')}) desencriptado con éxito.")
            except Exception as update_err:
                logger.error(f"❌ Error actualizando registro {reg_id}: {update_err}")

    logger.info(f"🎉 Migración finalizada. Se desencriptaron {modificados} comentarios exitosamente.")

if __name__ == "__main__":
    desencriptar_historial_comentarios()
