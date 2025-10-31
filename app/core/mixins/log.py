import logging
from functools import lru_cache
from sys import stdout
from time import gmtime


class LogMixin:
    @staticmethod
    @lru_cache
    def __get_logger() -> logging.Logger:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d: [%(process)d:%(thread)d] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
        )
        formatter.converter = gmtime

        console_handler = logging.StreamHandler(stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        return root_logger

    def log(self, msg: str) -> None:
        self.__get_logger().info(f"{self.__class__.__name__} {msg}")


logger = LogMixin().log
