"""
AI Insights & Analytics Agent
-----------------------------
Agente especializado en utilizar Modelos de Lenguaje (LLM) para analizar el histórico
de registros de energía, humor y comentarios de Supabase, ofreciendo recomendaciones
personalizadas y detección de patrones de bienestar.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Intentar importar google.generativeai (Gemini) o proveedor por defecto
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIInsightsAgent:
    """
    Agente inteligente impulsado por LLM para generar diagnósticos y recomendaciones
    sobre las tendencias de bienestar del usuario.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        self.model = None

        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Usar modelo eficiente y actualizado
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("AI Insights Agent inicializado correctamente con Google Gemini LLM.")
            except Exception as e:
                logger.error(f"Error al configurar la LLM: {str(e)}")

    def is_configured(self) -> bool:
        """Verifica si la LLM está configurada y lista."""
        return self.model is not None

    def analizar_tendencias(self, registros: List[Dict[str, Any]]) -> str:
        """
        Toma una lista de registros diarios y genera un informe analítico inteligente.
        """
        if not registros:
            return "No se encontraron suficientes registros diarios para realizar el análisis con IA."

        if not self.is_configured():
            return (
                "⚠️ El agente de IA no está configurado.\n"
                "Para activar los análisis inteligentes con LLM, añade la variable `GEMINI_API_KEY` en tu archivo `.env`."
            )

        # Formatear el histórico para la prompt de la LLM
        resumen_datos = ""
        for r in registros[:14]:  # Últimos 14 registros
            resumen_datos += f"- Fecha: {r.get('fecha')}, Energía: {r.get('energia')}/10, Humor: {r.get('humor')}/10. Nota: {r.get('comentarios', 'Sin nota')}\n"

        prompt = f"""
Eres un asistente experto en bienestar personal, analítica de datos y psicología positiva.
Analiza la siguiente serie temporal de registros diarios de energía y humor de un usuario:

HISTÓRICO DE REGISTROS (Últimos días):
{resumen_datos}

Por favor, proporciona un análisis estructurado en formato Markdown con las siguientes secciones:
1. 📈 **Patrones y Tendencias**: (Identifica cómo se relacionan la energía, el humor y los comentarios).
2. 💡 **Observaciones Clave**: (Factores que parecen aumentar o disminuir el bienestar).
3. 🎯 **Recomendación Personalizada**: (1 o 2 consejos prácticos y empáticos para mejorar la rutina).

Mantén un tono motivador, cercano y profesional.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error al generar análisis con LLM: {str(e)}")
            return f"Ocurrió un error al procesar el análisis con IA: {str(e)}"


# Función helper rápida
def obtener_analisis_ia(registros: List[Dict[str, Any]]) -> str:
    agent = AIInsightsAgent()
    return agent.analizar_tendencias(registros)
