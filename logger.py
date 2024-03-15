import datetime
import json
import logging
import os
import sys

import git
import shortuuid


class ExcludeAsyncioTestCaseFilter(logging.Filter):
    def filter(self, record):
        return "IsolatedAsyncioTestCase._asyncioLoopRunner()" not in record.getMessage()


class Logger:
    """Logger class."""

    def __init__(self, name="campanha_parser"):
        self.logger = logging.getLogger(name)
        log_format = "%(asctime)s [%(levelno)s] %(appname)s [%(branch)s] %(uuid)s %(message)s"  # Updated log format
        log_level = os.environ.get("LOG_LEVEL", "20")
        log_level = int(log_level) if log_level.isdigit() else logging.INFO

        if not self.logger.handlers:
            hdlr = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(log_format)
            hdlr.setFormatter(formatter)
            self.logger.addHandler(hdlr)
            self.logger.setLevel(log_level)

        self.new_uuid()
        self.name = name
        self.logger.addFilter(ExcludeAsyncioTestCaseFilter())
        self.info(f"Logger Iniciado. Level: {log_level}")

    def new_uuid(self):
        self.uuid = str(shortuuid.uuid())
        return self.uuid

    @staticmethod
    def format_date(item):
        if isinstance(item, (datetime.date, datetime.datetime)):
            return item.isoformat()
        return item

    def get_git_branch(self):
        try:
            repo = git.Repo(search_parent_directories=True)
            branch = repo.active_branch.name
            return branch
        except git.InvalidGitRepositoryError:
            return None

    def log(self, level, message, **kwargs):
        message_json = json.dumps(message, ensure_ascii=False, sort_keys=True, default=self.format_date)
        log_kwargs = kwargs.copy()
        branch_name = self.get_git_branch() or os.environ.get("GIT_BRANCH_NAME", "Unknown Branch")
        log_kwargs["extra"] = {
            "uuid": self.uuid,
            "appname": self.name,
            "branch": branch_name,
        }  # Add appname and UUID to the log record
        getattr(self.logger, level)(message_json, **log_kwargs)

    def info(self, message, **kwargs):
        self.log("info", message, **kwargs)

    def warning(self, message, **kwargs):
        self.log("warning", message, **kwargs)

    def success(self, message, **kwargs):
        self.log("info", message, **kwargs)

    def error(self, message, **kwargs):
        self.log("error", message, **kwargs)

    def critical(self, message, **kwargs):
        self.log("critical", message, **kwargs)

    def debug(self, message, **kwargs):
        self.log("debug", message, **kwargs)

    def warning(self, message, **kwargs):
        self.log("warning", message, **kwargs)
