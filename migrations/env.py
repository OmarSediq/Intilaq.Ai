from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from backend.database.models.base import Base
# Import models to register their metadata for Alembic (even if not used directly)
from backend.database.models import cv_models, hr_models , event_outbox_model , processed_events_models# noqa: F401

# =========================
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata الأساسي
target_metadata = Base.metadata

DATABASE_URL = "postgresql+psycopg2://admin:84000@localhost/intilaq_db"


# =========================
# Offline Migrations
# =========================
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,                
        version_table="alembic_version",
        version_table_schema="alembic",       
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================
# Online Migrations
# =========================
def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,             
            version_table="alembic_version",
            version_table_schema="alembic",  
        )

        with context.begin_transaction():
            context.run_migrations()


# =========================
# Entrypoint
# =========================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()