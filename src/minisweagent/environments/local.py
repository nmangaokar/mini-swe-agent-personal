import os
import subprocess
from dataclasses import dataclass, field
from typing import Any
import sys


@dataclass
class LocalEnvironmentConfig:
    cwd: str = ""
    env: dict[str, str] = field(default_factory=dict)
    timeout: int = 30


class LocalEnvironment:
    def __init__(self, *, config_class: type = LocalEnvironmentConfig, **kwargs):
        """This class executes bash commands directly on the local machine."""
        self.config = config_class(**kwargs)

    # def execute(self, command: str, cwd: str = ""):
    #     """Execute a command in the local environment and return the result as a dict."""
    #     cwd = cwd or self.config.cwd or os.getcwd()
    #     result = subprocess.run(
    #         command,
    #         shell=True,
    #         text=True,
    #         cwd=cwd,
    #         env=os.environ | self.config.env,
    #         timeout=self.config.timeout,
    #         encoding="utf-8",
    #         errors="replace",
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT,
    #     )
    #     return {"output": result.stdout, "returncode": result.returncode}

    def execute(self, command: str, cwd: str = ""):
        """Execute a command locally, stream live to stdout, and return the result as a dict."""
        cwd = cwd or self.config.cwd or os.getcwd()

        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            cwd=cwd,
            env=os.environ | self.config.env,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        output_lines = []
        for line in process.stdout:
            sys.stdout.write(line)    # stream live to terminal
            sys.stdout.flush()
            output_lines.append(line) # capture for return

        process.wait(timeout=self.config.timeout)

        return {"output": "".join(output_lines), "returncode": process.returncode}
