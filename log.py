from typing import NoReturn, Optional, Protocol


class Logger(Protocol):
    def debug(self, message: str) -> None: ...
    def die(self, message: str) -> NoReturn: ...


logger: Optional[Logger] = None


def die(msg: str) -> NoReturn:
    assert logger is not None
    logger.die(msg)


def debug(msg: str) -> None:
    assert logger is not None
    logger.debug(msg)
