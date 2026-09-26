from __future__ import annotations

from typing import NoReturn, Protocol


class Logger(Protocol):
    def debug(self, message: str) -> None: ...
    def die(self, message: str) -> NoReturn: ...


logger: Logger | None = None


def die(msg: str) -> NoReturn:
    assert logger is not None
    logger.die(msg)


def debug(msg: str) -> None:
    assert logger is not None
    logger.debug(msg)
