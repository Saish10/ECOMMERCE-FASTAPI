import importlib
import os
import pkgutil
import sys
from logging.config import fileConfig
from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from app.database import Base

# Load environment variables
load_dotenv(dotenv_path=".env")

# Ensure `app/` is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure models are loaded
MODELS_PACKAGE = "app.models"
models_path = os.path.join(os.path.dirname(__file__), "..", "models")

if os.path.exists(models_path):  # Ensure the path exists
    for _, module_name, _ in pkgutil.iter_modules([models_path]):
        importlib.import_module(f"{MODELS_PACKAGE}.{module_name}")

# Load DATABASE_URL from `.env`
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

# Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Setup logging
if config.config_file_name:
    fileConfig(config.config_file_name)

# Set target metadata from Base
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
