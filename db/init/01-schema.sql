-- Garante que o schema public exista e tenha permissões, mesmo em imagens
-- postgres que não o criam automaticamente (ex.: POSTGRES_DB != postgres).
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
