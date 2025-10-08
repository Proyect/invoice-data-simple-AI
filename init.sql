-- Configuración inicial de PostgreSQL
-- Habilitar extensiones necesarias

-- Para búsqueda full-text en español
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Para funciones de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Para operadores de texto
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Configurar búsqueda full-text en español
ALTER DATABASE document_extractor SET default_text_search_config = 'spanish';

-- Crear función para actualizar search_vector
CREATE OR REPLACE FUNCTION update_document_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('spanish', 
        COALESCE(NEW.raw_text, '') || ' ' || 
        COALESCE(NEW.extracted_data::text, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear trigger para actualizar search_vector automáticamente
CREATE TRIGGER update_document_search_vector_trigger
    BEFORE INSERT OR UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_document_search_vector();
