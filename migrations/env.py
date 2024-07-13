import os
import sys

# Append the root directory of your project to Python's path
# Adjust the path as per your project structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Adjust target_metadata if needed
target_metadata = None

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app import db
from app.models import User, Income, Expense

# This is the Alembic Config object, which provides access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name:
    fileConfig(config.config_file_name)

# Add your model's MetaData objects here for 'autogenerate' supportgit
target_metadata = db.metadata  # Adjust based on your actual metadata setup

# Other values from the config, defined by the needs of env.py, can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
