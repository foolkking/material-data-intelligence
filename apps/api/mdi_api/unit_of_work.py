from __future__ import annotations

from types import TracebackType
from contextvars import Token

from sqlalchemy.engine import Connection, Engine, Transaction

from mdi_api.agent2_repositories import Agent2RepositoryBundle
from mdi_api.application.research.ports import ResearchProjectAccessPort
from mdi_api.application.research.transactions import (
    enter_transaction,
    exit_transaction,
    transaction_active,
)
from mdi_api.infrastructure.project_access import SQLALCHEMY_PROJECT_ACCESS
from mdi_api.repositories import SqlAlchemyRepositoryBundle


class RepositorySession:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._connection: Connection | None = None
        self._transaction: Transaction | None = None
        self._repositories: SqlAlchemyRepositoryBundle | None = None
        self._agent2_repositories: Agent2RepositoryBundle | None = None
        self._transaction_token: Token[int] | None = None

    @property
    def repositories(self) -> SqlAlchemyRepositoryBundle:
        if self._repositories is None:
            raise RuntimeError("RepositorySession.begin() must be called before accessing repositories")
        return self._repositories

    @property
    def agent2(self) -> Agent2RepositoryBundle:
        if self._agent2_repositories is None:
            raise RuntimeError("RepositorySession.begin() must be called before accessing Agent 2.0 repositories")
        return self._agent2_repositories

    @property
    def connection(self) -> Connection:
        if self._connection is None:
            raise RuntimeError("RepositorySession.begin() must be called before accessing the connection")
        return self._connection

    def begin(self) -> "RepositorySession":
        if self._connection is not None:
            raise RuntimeError("RepositorySession is already active")
        self._connection = self._engine.connect()
        self._transaction = self._connection.begin()
        self._transaction_token = enter_transaction()
        self._repositories = SqlAlchemyRepositoryBundle.create(self._connection)
        self._agent2_repositories = Agent2RepositoryBundle.create(self._connection)
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
        self._agent2_repositories = None
        if self._transaction_token is not None:
            exit_transaction(self._transaction_token)
            self._transaction_token = None

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
    def __init__(
        self,
        engine: Engine,
        *,
        project_access: ResearchProjectAccessPort = SQLALCHEMY_PROJECT_ACCESS,
    ) -> None:
        self.engine = engine
        self.project_access = project_access

    def create_repositories(self) -> SqlAlchemyRepositoryBundle:
        return SqlAlchemyRepositoryBundle.create(self.engine)

    def session(self) -> RepositorySession:
        return RepositorySession(self.engine)

    def unit_of_work(self) -> UnitOfWork:
        return UnitOfWork(self.engine)
