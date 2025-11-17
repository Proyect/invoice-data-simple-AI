"""
Migración inicial - Modelos mejorados del sistema

Revision ID: 001_enhanced_models
Revises: 
Create Date: 2024-10-14 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_enhanced_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crear todas las tablas del sistema mejorado"""
    
    # Crear tipos enum
    document_type_enum = postgresql.ENUM(
        'factura', 'recibo', 'contrato', 'formulario', 'cedula', 
        'pasaporte', 'licencia', 'certificado', 'otro',
        name='documenttype'
    )
    document_status_enum = postgresql.ENUM(
        'uploaded', 'processing', 'processed', 'failed', 
        'reviewing', 'approved', 'rejected',
        name='documentstatus'
    )
    ocr_provider_enum = postgresql.ENUM(
        'tesseract', 'google_vision', 'aws_textract', 'azure_ocr', 'hybrid',
        name='ocrprovider'
    )
    extraction_method_enum = postgresql.ENUM(
        'regex', 'spacy', 'llm', 'hybrid', 'manual',
        name='extractionmethod'
    )
    user_role_enum = postgresql.ENUM(
        'admin', 'manager', 'operator', 'reviewer', 'user', 'readonly',
        name='userrole'
    )
    user_status_enum = postgresql.ENUM(
        'active', 'inactive', 'suspended', 'pending', 'banned',
        name='userstatus'
    )
    auth_provider_enum = postgresql.ENUM(
        'local', 'google', 'microsoft', 'github', 'ldap',
        name='authprovider'
    )
    job_status_enum = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed', 'cancelled', 'timeout', 'retry',
        name='jobstatus'
    )
    job_type_enum = postgresql.ENUM(
        'document_ocr', 'document_extraction', 'document_classification',
        'batch_processing', 'data_export', 'cleanup', 'backup', 'report_generation',
        name='jobtype'
    )
    step_status_enum = postgresql.ENUM(
        'pending', 'running', 'completed', 'failed', 'skipped',
        name='stepstatus'
    )
    
    # Crear enums en PostgreSQL
    document_type_enum.create(op.get_bind(), checkfirst=True)
    document_status_enum.create(op.get_bind(), checkfirst=True)
    ocr_provider_enum.create(op.get_bind(), checkfirst=True)
    extraction_method_enum.create(op.get_bind(), checkfirst=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)
    user_status_enum.create(op.get_bind(), checkfirst=True)
    auth_provider_enum.create(op.get_bind(), checkfirst=True)
    job_status_enum.create(op.get_bind(), checkfirst=True)
    job_type_enum.create(op.get_bind(), checkfirst=True)
    step_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Tabla de organizaciones
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('document_limit', sa.Integer(), nullable=True),
        sa.Column('storage_limit_mb', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)
    
    # Tabla de usuarios mejorada
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('auth_provider', auth_provider_enum, nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('status', user_status_enum, nullable=True),
        sa.Column('role', user_role_enum, nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('phone_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False),
        sa.Column('two_factor_secret', sa.String(length=255), nullable=True),
        sa.Column('documents_processed', sa.Integer(), nullable=False),
        sa.Column('total_processing_time', sa.Float(), nullable=False),
        sa.Column('last_document_processed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('daily_document_limit', sa.Integer(), nullable=True),
        sa.Column('monthly_document_limit', sa.Integer(), nullable=True),
        sa.Column('storage_limit_mb', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=True)
    op.create_index('ix_users_org_role', 'users', ['organization_id', 'role'], unique=False)
    op.create_index('ix_users_status_created', 'users', ['status', 'created_at'], unique=False)
    op.create_index('ix_users_provider_external', 'users', ['auth_provider', 'external_id'], unique=False)
    
    # Tabla de documentos mejorada
    op.create_table('documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('document_type', document_type_enum, nullable=True),
        sa.Column('status', document_status_enum, nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('ocr_provider', ocr_provider_enum, nullable=True),
        sa.Column('extraction_method', extraction_method_enum, nullable=True),
        sa.Column('ocr_cost', sa.Float(), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_hash', 'file_size', name='uq_document_hash_size')
    )
    op.create_index(op.f('ix_documents_filename'), 'documents', ['filename'], unique=False)
    op.create_index(op.f('ix_documents_uuid'), 'documents', ['uuid'], unique=True)
    op.create_index(op.f('ix_documents_file_hash'), 'documents', ['file_hash'], unique=False)
    op.create_index('ix_documents_user_status', 'documents', ['user_id', 'status'], unique=False)
    op.create_index('ix_documents_type_created', 'documents', ['document_type', 'created_at'], unique=False)
    
    # Tabla de versiones de documentos
    op.create_table('document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('extracted_data_snapshot', sa.JSON(), nullable=True),
        sa.Column('confidence_score_snapshot', sa.Float(), nullable=True),
        sa.Column('ocr_provider_snapshot', sa.String(length=50), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('change_reason', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'version_number', name='uq_document_version')
    )
    
    # Tabla de extracciones de documentos
    op.create_table('document_extractions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('extraction_method', extraction_method_enum, nullable=False),
        sa.Column('ocr_provider', ocr_provider_enum, nullable=True),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabla de tags de documentos
    op.create_table('document_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sa.String(length=100), nullable=False),
        sa.Column('tag_value', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'tag_name', name='uq_document_tag')
    )
    
    # Tabla de sesiones de usuario
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('device_info', sa.JSON(), nullable=True),
        sa.Column('location_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_session_token'), 'user_sessions', ['session_token'], unique=True)
    
    # Tabla de API keys
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('key_prefix', sa.String(length=10), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True),
        sa.Column('rate_limit_per_day', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)
    
    # Tabla de logs de auditoría
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabla de jobs de procesamiento
    op.create_table('processing_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('job_type', job_type_enum, nullable=False),
        sa.Column('status', job_status_enum, nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('cpu_usage_percentage', sa.Float(), nullable=True),
        sa.Column('worker_id', sa.String(length=100), nullable=True),
        sa.Column('worker_hostname', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('max_retries', sa.Integer(), nullable=False),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processing_jobs_job_id'), 'processing_jobs', ['job_id'], unique=True)
    
    # Tabla de pasos de procesamiento
    op.create_table('processing_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(length=100), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('status', step_status_enum, nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['processing_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices adicionales para búsqueda full-text
    op.execute("CREATE INDEX IF NOT EXISTS ix_documents_search_vector ON documents USING gin(search_vector)")


def downgrade() -> None:
    """Eliminar todas las tablas"""
    op.drop_table('processing_steps')
    op.drop_table('processing_jobs')
    op.drop_table('audit_logs')
    op.drop_table('api_keys')
    op.drop_table('user_sessions')
    op.drop_table('document_tags')
    op.drop_table('document_extractions')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('users')
    op.drop_table('organizations')
    
    # Eliminar enums
    op.execute('DROP TYPE IF EXISTS stepstatus')
    op.execute('DROP TYPE IF EXISTS jobtype')
    op.execute('DROP TYPE IF EXISTS jobstatus')
    op.execute('DROP TYPE IF EXISTS authprovider')
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS extractionmethod')
    op.execute('DROP TYPE IF EXISTS ocrprovider')
    op.execute('DROP TYPE IF EXISTS documentstatus')
    op.execute('DROP TYPE IF EXISTS documenttype')















