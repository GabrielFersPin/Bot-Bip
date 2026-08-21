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
    Agente inteligente de bienestar multi-proveedor (Groq, OpenRouter, Gemini)
    con motor de análisis de reglas clínicas local de respaldo 100% gratuito.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        
        self.provider = None
        self.client = None

        # 1. Intentar Groq (API 100% gratuita y ultrarrápida Llama 3.1)
        if self.groq_key:
            try:
                import urllib.request
                import json
                self.provider = "groq"
                logger.info("AIInsightsAgent utilizando proveedor Groq (Llama 3.1).")
            except Exception as e:
                logger.error(f"Error al inicializar Groq: {e}")

        # 2. Intentar Gemini
        elif GEMINI_AVAILABLE and self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
                self.provider = "gemini"
                logger.info("AIInsightsAgent utilizando proveedor Gemini.")
            except Exception as e:
                logger.error(f"Error al inicializar Gemini: {e}")
        else:
            self.provider = "local"
            logger.info("AIInsightsAgent utilizando motor local analítico de respaldo.")

    def analizar_tendencias(self, registros: List[Dict[str, Any]]) -> str:
        """
        Toma la lista de registros y genera una interpretación empática y clínica.
        """
        if not registros:
            return "🌸 **Aviso:** No se encontraron registros para el período seleccionado. Registra datos diarios en Telegram para obtener una lectura personalizada."

        # Si hay Groq Key (Proveedor gratuito ultrarrápido)
        if self.provider == "groq" and self.groq_key:
            return self._analizar_con_groq(registros)

        # Si hay Gemini Key
        if self.provider == "gemini" and self.client:
            return self._analizar_con_gemini(registros)

        # Fallback local 100% garantizado (Motor de Reglas Clínicas de Apoyo)
        return self._analizar_local(registros)

    def _analizar_con_groq(self, registros: List[Dict[str, Any]]) -> str:
        import urllib.request
        import json

        resumen_datos = ""
        for r in registros[:14]:
            resumen_datos += f"- Fecha: {r.get('fecha')}, Energía: {r.get('energia')}/10, Humor: {r.get('humor')}/10, Sueño: {r.get('sueno_horas', '8.0')}h. Nota: {r.get('comentarios', 'Sin notas')}\n"

        prompt = (
            "Eres un especialista empático en apoyo psicoafectivo y ritmo circadiano.\n"
            "Analiza estos registros de bienestar:\n\n"
            f"{resumen_datos}\n\n"
            "Proporciona un reporte en Markdown con 3 secciones breves y cálidas:\n"
            "1. 📈 **Evaluación de Estabilidad de Ánimo y Descanso**\n"
            "2. ⚠️ **Detección Precoz de Alertas**\n"
            "3. 🌿 **Recomendaciones de Autocuidado y Sueño**"
        )

        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(data).encode("utf-8"),
            headers=headers
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error en API de Groq: {e}. Usando motor local...")
            return self._analizar_local(registros)

    def _analizar_con_gemini(self, registros: List[Dict[str, Any]]) -> str:
        resumen_datos = ""
        for r in registros[:14]:
            resumen_datos += f"- Fecha: {r.get('fecha')}, Energía: {r.get('energia')}/10, Humor: {r.get('humor')}/10, Sueño: {r.get('sueno_horas', '8.0')}h. Nota: {r.get('comentarios', 'Sin notas')}\n"

        prompt = (
            "Eres un especialista empático en apoyo psicoafectivo y ritmo circadiano.\n"
            f"{resumen_datos}\n"
            "Proporciona un reporte en Markdown con 3 secciones breves:\n"
            "1. 📈 **Evaluación de Estabilidad de Ánimo y Descanso**\n"
            "2. ⚠️ **Detección Precoz de Alertas**\n"
            "3. 🌿 **Recomendaciones de Autocuidado y Sueño**"
        )
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            return self._analizar_local(registros)

    def _analizar_local(self, registros: List[Dict[str, Any]]) -> str:
        import pandas as pd
        df = pd.DataFrame(registros)
        
        prom_e = round(df["energia"].mean(), 1) if "energia" in df.columns else 5
        prom_h = round(df["humor"].mean(), 1) if "humor" in df.columns else 5
        prom_s = round(df["sueno_horas"].mean(), 1) if "sueno_horas" in df.columns else 8

        # Reglas Clínicas de Autocuidado
        alerta = "✅ **Estabilidad General:** No se observan fluctuaciones extremas en el período evaluado."
        if prom_e >= 8 and prom_s <= 5:
            alerta = "⚠️ **Alerta de Sobreestimulación:** Se detecta un nivel de energía elevado junto a pocas horas de sueño. Procura descansar y regular el ritmo diario."
        elif prom_e <= 4 and prom_h <= 4:
            alerta = "💙 **Alerta de Estado Bajo:** Se registran puntuaciones moderadamente bajas de energía y estado de ánimo. Sé amable contigo y apóyate en personas de confianza."

        return f"""
### 📈 **Evaluación de Estabilidad de Ánimo y Descanso**
- **Promedio de Energía:** {prom_e}/10
- **Promedio de Estado de Ánimo:** {prom_h}/10
- **Descanso Medio:** {prom_s} horas por noche.

### ⚠️ **Detección de Patrones**
{alerta}

### 🌿 **Recomendaciones de Autocuidado**
1. **Regularidad del Sueño:** Procura acostarte y despertarte en horarios consistentes.
2. **Ritmo Diario:** Mantén pausas breves de relajación durante el día si notas aceleración.
3. **Red de Apoyo:** Ante cualquier duda sobre tu estabilidad, comparte este informe con tu profesional de confianza.
"""

def obtener_analisis_ia(registros: List[Dict[str, Any]]) -> str:
    agent = AIInsightsAgent()
    return agent.analizar_tendencias(registros)


# Función helper rápida
def obtener_analisis_ia(registros: List[Dict[str, Any]]) -> str:
    agent = AIInsightsAgent()
    return agent.analizar_tendencias(registros)
