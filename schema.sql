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

-- 4. Trigger para actualizar el campo updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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
-- Permite consultar datos de la base de datos (por ejemplo, desde el Dashboard de Streamlit)
CREATE POLICY "Permitir lectura publica o anonima"
ON public.registros_diarios
FOR SELECT
TO anon, authenticated
USING (true);

-- Política 2: Inserción y Modificación (Insert/Update)
-- Permite insertar registros tanto con Anon Key como con Service Role
CREATE POLICY "Permitir insercion a rol anon y authenticated"
ON public.registros_diarios
FOR INSERT
TO anon, authenticated
WITH CHECK (true);

CREATE POLICY "Permitir actualizacion a rol anon y authenticated"
ON public.registros_diarios
FOR UPDATE
TO anon, authenticated
USING (true);

-- Comentario explicativo sobre Service Role Key vs Anon Key:
-- Anon Key: Diseñada para operaciones cliente (ej. Dashboard de Streamlit). Respeta RLS.
-- Service Role Key: Clave secreta con privilegios de Administrador (Bypasses RLS).
--                    Debe usarse únicamente en entornos de servidor seguros (ej. el backend del Bot de Telegram).
