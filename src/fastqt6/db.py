"""Small SQL helpers for PyQt6 apps."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


@dataclass(slots=True)
class DBConfig:
    driver: str = "mysql"
    host: str = "localhost"
    ports: tuple[int, ...] = (3308, 3306)
    user: str = "root"
    password: str = ""
    database: str = ""
    charset: str = "utf8mb4"
    sqlite_path: str | Path = "app.db"


class SQLDatabase:
    """A tiny DAO wrapper that works with MySQL and SQLite."""

    def __init__(self, config: DBConfig | None = None, connection: Any | None = None):
        self.config = config or DBConfig()
        self.connection = connection or self._connect()

    @classmethod
    def mysql(
        cls,
        database: str,
        *,
        host: str = "localhost",
        ports: tuple[int, ...] = (3308, 3306),
        user: str = "root",
        password: str = "",
    ) -> "SQLDatabase":
        return cls(DBConfig(driver="mysql", host=host, ports=ports, user=user, password=password, database=database))

    @classmethod
    def sqlite(cls, path: str | Path = "app.db") -> "SQLDatabase":
        return cls(DBConfig(driver="sqlite", sqlite_path=path))

    def close(self) -> None:
        self.connection.close()

    def execute(self, sql: str, params: Sequence[Any] | Mapping[str, Any] = ()) -> Any:
        with self.cursor() as cursor:
            cursor.execute(self._sql(sql), params)
            return cursor

    def fetch_one(self, sql: str, params: Sequence[Any] | Mapping[str, Any] = ()) -> dict[str, Any] | None:
        with self.cursor() as cursor:
            cursor.execute(self._sql(sql), params)
            row = cursor.fetchone()
        return dict(row) if row is not None else None

    def fetch_all(self, sql: str, params: Sequence[Any] | Mapping[str, Any] = ()) -> list[dict[str, Any]]:
        with self.cursor() as cursor:
            cursor.execute(self._sql(sql), params)
            return [dict(row) for row in cursor.fetchall()]

    def scalar(self, sql: str, params: Sequence[Any] | Mapping[str, Any] = (), default: Any = None) -> Any:
        row = self.fetch_one(sql, params)
        if not row:
            return default
        return next(iter(row.values()))

    def select(
        self,
        table: str,
        *,
        columns: str | Iterable[str] = "*",
        where: str = "",
        params: Sequence[Any] = (),
        order_by: str = "",
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        cols = columns if isinstance(columns, str) else ", ".join(columns)
        sql = f"select {cols} from {table}"
        if where:
            sql += f" where {where}"
        if order_by:
            sql += f" order by {order_by}"
        if limit is not None:
            sql += f" limit {int(limit)}"
        return self.fetch_all(sql, params)

    def insert(self, table: str, data: Mapping[str, Any]) -> int:
        columns = list(data)
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"insert into {table} ({', '.join(columns)}) values ({placeholders})"
        with self.cursor() as cursor:
            cursor.execute(self._sql(sql), tuple(data[column] for column in columns))
            return int(getattr(cursor, "lastrowid", 0) or 0)

    def update(self, table: str, data: Mapping[str, Any], where: str, params: Sequence[Any] = ()) -> None:
        columns = list(data)
        assignments = ", ".join(f"{column}=?" for column in columns)
        sql = f"update {table} set {assignments} where {where}"
        values = tuple(data[column] for column in columns) + tuple(params)
        self.execute(sql, values)

    def delete(self, table: str, where: str, params: Sequence[Any] = ()) -> None:
        self.execute(f"delete from {table} where {where}", params)

    def login(
        self,
        table: str,
        username: str,
        password: str,
        *,
        username_col: str = "username",
        password_col: str = "password",
    ) -> dict[str, Any] | None:
        return self.fetch_one(
            f"select * from {table} where {username_col}=? and {password_col}=?",
            (username, password),
        )

    def run_script(self, sql: str) -> None:
        statements = [part.strip() for part in sql.split(";") if part.strip()]
        with self.cursor() as cursor:
            for statement in statements:
                cursor.execute(self._sql(statement))

    @contextmanager
    def transaction(self) -> Iterator["SQLDatabase"]:
        old_autocommit = None
        if self.config.driver == "mysql":
            old_autocommit = self.connection.get_autocommit()
            self.connection.autocommit(False)
        try:
            yield self
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            if old_autocommit is not None:
                self.connection.autocommit(old_autocommit)

    @contextmanager
    def cursor(self) -> Iterator[Any]:
        cursor = self.connection.cursor()
        try:
            yield cursor
            if self.config.driver == "sqlite":
                self.connection.commit()
        finally:
            cursor.close()

    def _connect(self) -> Any:
        if self.config.driver == "sqlite":
            connection = sqlite3.connect(self.config.sqlite_path)
            connection.row_factory = sqlite3.Row
            return connection

        if self.config.driver != "mysql":
            raise ValueError("driver must be 'mysql' or 'sqlite'")

        try:
            import pymysql
            from pymysql.cursors import DictCursor
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install PyMySQL: pip install PyMySQL") from exc

        last_error: Exception | None = None
        for port in self.config.ports:
            try:
                return pymysql.connect(
                    host=self.config.host,
                    port=port,
                    user=self.config.user,
                    password=self.config.password,
                    database=self.config.database,
                    charset=self.config.charset,
                    cursorclass=DictCursor,
                    autocommit=True,
                )
            except Exception as exc:  # pragma: no cover - depends on local server
                last_error = exc
        raise last_error or RuntimeError("Could not connect to MySQL")

    def _sql(self, sql: str) -> str:
        if self.config.driver == "mysql":
            return sql.replace("?", "%s")
        return sql
