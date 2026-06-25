from __future__ import annotations

from types import TracebackType

from sqlalchemy.engine import Connection, Engine, Transaction

from mdi_api.repositories import SqlAlchemyRepositoryBundle


class RepositorySession:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._connection: Connection | None = None
        self._transaction: Transaction | None = None
        self._repositories: SqlAlchemyRepositoryBundle | None = None

    @property
    def repositories(self) -> SqlAlchemyRepositoryBundle:
        if self._repositories is None:
            raise RuntimeError("RepositorySession.begin() must be called before accessing repositories")
        return self._repositories

    def begin(self) -> "RepositorySession":
        if self._connection is not None:
            raise RuntimeError("RepositorySession is already active")
        self._connection = self._engine.connect()
        self._transaction = self._connection.begin()
        self._repositories = SqlAlchemyRepositoryBundle.create(self._connection)
        return self

    def commit(self) -> None:
        if self._transaction is None:
            return
        self._transaction.commit()
        self._transaction = None

    def rollback(self) -> None:
        if self._transaction is None:
            return
        self._transaction.rollback()
        self._transaction = None

    def close(self) -> None:
        if self._transaction is not None:
            self.rollback()
        if self._connection is not None:
            self._connection.close()
        self._connection = None
        self._repositories = None

    def __enter__(self) -> "RepositorySession":
        return self.begin()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()
        return False


class UnitOfWork(RepositorySession):
    pass


class RepositoryFactory:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create_repositories(self) -> SqlAlchemyRepositoryBundle:
        return SqlAlchemyRepositoryBundle.create(self.engine)

    def session(self) -> RepositorySession:
        return RepositorySession(self.engine)

    def unit_of_work(self) -> UnitOfWork:
        return UnitOfWork(self.engine)
