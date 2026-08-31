"""
Módulo de Internacionalización (i18n) para Bot-Bip.
Proporciona traducción dinámica para Español (es), Inglés (en) y Francés (fr).
"""

from typing import Dict, Any
from .es import STRINGS as ES
from .en import STRINGS as EN
from .fr import STRINGS as FR

LANG_MAP: Dict[str, Dict[str, str]] = {
    "es": ES,
    "en": EN,
    "fr": FR
}

def resolve_lang_code(raw_code: str) -> str:
    """
    Normaliza el código de idioma de Telegram (ej: 'en-US', 'fr-FR', 'es-ES')
    a los códigos soportados: 'es', 'en', 'fr'. Por defecto devuelve 'es'.
    """
    if not raw_code:
        return "es"
    code = str(raw_code).lower().strip()[:2]
    if code in LANG_MAP:
        return code
    # Si es otro idioma desconocido, usar español por defecto
    return "es"

def t(key: str, lang: str = "es", **kwargs: Any) -> str:
    """
    Obtiene la traducción correspondiente a la clave `key` en el idioma `lang`.
    Soporta formateo dinámico de variables mediante kwargs.
    """
    code = resolve_lang_code(lang)
    lang_dict = LANG_MAP.get(code, ES)
    
    # Obtener el texto; si no existe en el idioma objetivo, hacer fallback a español (ES) y luego a la clave
    text = lang_dict.get(key, ES.get(key, key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
