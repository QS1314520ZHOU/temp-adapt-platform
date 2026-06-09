import logging
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class SqlExtractor:
    """Execute SQL queries against a relational database and return results.

    Uses SQLAlchemy internally so that Oracle, MySQL, PostgreSQL, SQL Server
    and other backends are supported through the appropriate driver.

    Args:
        connection_string: A SQLAlchemy connection string, e.g.
            - ``postgresql+psycopg2://user:pass@host/db``
            - ``mysql+pymysql://user:pass@host/db``
            - ``oracle+cx_oracle://user:pass@host:1521/?service_name=svc``
            - ``mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+17``
        db_type: A human-readable label (``oracle``, ``mysql``,
            ``postgresql``, ``sqlserver``). Currently informational only but
            can be used for future branching logic.
    """

    def __init__(self, connection_string: str, db_type: str) -> None:
        self.connection_string: str = connection_string
        self.db_type: str = db_type
        self._engine: Optional[Engine] = None

    # ------------------------------------------------------------------
    # Engine lifecycle
    # ------------------------------------------------------------------

    def _get_engine(self) -> Engine:
        """Lazily create and cache the SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(self.connection_string, pool_pre_ping=True)
        return self._engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_query(self, sql: str) -> list[dict]:
        """Execute a SQL statement and return rows as a list of dicts.

        Args:
            sql: The SQL query to execute.

        Returns:
            A list where each element is a dict keyed by column name.

        Raises:
            SQLAlchemyError: If the query fails.
        """
        engine = self._get_engine()
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                logger.info("Query returned %d rows", len(rows))
                return rows
        except SQLAlchemyError:
            logger.exception("SQL query execution failed")
            raise

    def test_connection(self) -> bool:
        """Test whether a connection to the database can be established.

        Returns:
            True if the connection succeeds, False otherwise.
        """
        try:
            engine = self._get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test succeeded (%s)", self.db_type)
            return True
        except Exception:
            logger.exception("Database connection test failed (%s)", self.db_type)
            return False

    def close(self) -> None:
        """Dispose of the underlying SQLAlchemy engine and release resources."""
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            logger.info("Database engine disposed")
