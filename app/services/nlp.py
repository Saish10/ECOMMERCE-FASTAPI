from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException


class NLPQueryService:
    """Service for executing SQL queries on the database."""

    @staticmethod
    def execute_query(db: Session, query: str) -> list[dict]:
        """Executes an SQL query and returns results."""
        try:
            result = db.execute(text(query)).fetchall()
            return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @staticmethod
    def get_database_schema(db: Session) -> str:
        """Fetches database schema dynamically from PostgreSQL"""
        result: list[tuple[str, str]] = db.execute(
            text(
                """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
            """
            )
        ).fetchall()

        schema: dict[str, list[str]] = {}
        for table, column in result:
            schema.setdefault(table, []).append(column)

        schema_str = "\n".join(
            [
                f"{table} ({', '.join(columns)})"
                for table, columns in schema.items()
            ]
        )
        return schema_str
