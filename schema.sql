-- ==============================================================================
-- DATABASE & SECURITY AGENT - ESQUEMA Y POLÍTICAS DE SEGURIDAD EN SUPABASE
-- Tabla: registros_diarios
-- ==============================================================================

-- 1. Crear extensión para generación de UUID (si no está habilitada)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Crear la tabla registros_diarios
CREATE TABLE IF NOT EXISTS public.registros_diarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,                           -- ID de usuario de Telegram
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,           -- Fecha del registro (sin hora)
    energia INT NOT NULL CHECK (energia >= 1 AND energia <= 10), -- Nivel de energía (1-10)
    humor INT NOT NULL CHECK (humor >= 1 AND humor <= 10),       -- Nivel de humor/ánimo (1-10)
    sueno_horas NUMERIC(3,1) DEFAULT 8.0 CHECK (sueno_horas >= 0 AND sueno_horas <= 24), -- Horas de descanso/sueño
    comentarios TEXT DEFAULT '',                        -- Comentarios u observaciones
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),  -- Marca de tiempo exacta
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),  -- Fecha de última actualización

    -- Restricción para garantizar máximo 1 registro diario por usuario (permite Upsert)
    CONSTRAINT unq_user_fecha UNIQUE (user_id, fecha)
);

-- 3. Índices para optimizar consultas de filtrado y rango de fechas
CREATE INDEX IF NOT EXISTS idx_registros_user_id ON public.registros_diarios(user_id);
CREATE INDEX IF NOT EXISTS idx_registros_fecha ON public.registros_diarios(fecha);
CREATE INDEX IF NOT EXISTS idx_registros_user_fecha ON public.registros_diarios(user_id, fecha);

-- 4. Trigger para actualizar el campo updated_at automáticamente (con search_path seguro)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Revocar permisos de ejecución directa vía API REST pública
REVOKE EXECUTE ON FUNCTION public.update_updated_at_column() FROM PUBLIC, anon, authenticated;

DROP TRIGGER IF EXISTS set_updated_at ON public.registros_diarios;
CREATE TRIGGER set_updated_at
BEFORE UPDATE ON public.registros_diarios
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- CONFIGURACIÓN DE RLS (ROW LEVEL SECURITY) Y PERMISOS DE API
-- ==============================================================================

-- Habilitar Row Level Security (RLS) en la tabla
ALTER TABLE public.registros_diarios ENABLE ROW LEVEL SECURITY;

-- Política 1: Lectura para clientes con Anon Key o Authenticated
CREATE POLICY "Permitir lectura publica o anonima"
ON public.registros_diarios
FOR SELECT
TO anon, authenticated
USING (true);

-- Política 2: Inserción validando que el user_id no sea nulo
CREATE POLICY "Permitir insercion a rol anon y authenticated"
ON public.registros_diarios
FOR INSERT
TO anon, authenticated
WITH CHECK (user_id IS NOT NULL);

-- Política 3: Actualización validando la presencia de user_id
CREATE POLICY "Permitir actualizacion a rol anon y authenticated"
ON public.registros_diarios
FOR UPDATE
TO anon, authenticated
USING (user_id IS NOT NULL)
WITH CHECK (user_id IS NOT NULL);

-- ==============================================================================
-- Tabla: contactos_emergencia (Red de Apoyo)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.contactos_emergencia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,                           -- ID de usuario de Telegram
    nombre TEXT NOT NULL,                              -- Nombre del contacto cifrado
    telefono TEXT NOT NULL,                            -- Teléfono cifrado
    relacion TEXT DEFAULT 'Red de Apoyo',              -- Relación cifrada
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.contactos_emergencia ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir insercion de contactos"
ON public.contactos_emergencia
FOR INSERT
TO anon, authenticated
WITH CHECK (user_id IS NOT NULL AND nombre IS NOT NULL);

CREATE POLICY "Permitir lectura de contactos"
ON public.contactos_emergencia
FOR SELECT
TO anon, authenticated
USING (true);

-- ==============================================================================
-- Tabla: recordatorios_config (Configuración de hora de aviso diario por usuario)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS public.recordatorios_config (
    user_id BIGINT PRIMARY KEY,                        -- ID de usuario / chat de Telegram
    hora TEXT NOT NULL,                                -- Hora programada HH:MM (ej: "09:00")
    timezone TEXT DEFAULT 'Europe/Madrid',             # Zona horaria del usuario
    activo BOOLEAN DEFAULT TRUE,                        # Estado de la alarma
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.recordatorios_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir lectura de recordatorios"
ON public.recordatorios_config
FOR SELECT
TO anon, authenticated
USING (true);

CREATE POLICY "Permitir insercion/actualizacion de recordatorios"
ON public.recordatorios_config
FOR ALL
TO anon, authenticated
USING (true)
WITH CHECK (true);

