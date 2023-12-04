import os
from time import time
import logging
from typing import Dict, TypeVar, Any, Union, Type
import yaml
import sys
from dataclasses import replace
import subprocess

T = TypeVar("T")


def timestamp():
    return round(time() * 1e3)


def _update_nested_dict(
    original_dict: Dict[str, Any], overrides: Dict[str, Any]
) -> Dict[str, Any]:
    "Update a dict with another regarding nested items in a way that replace the original values with the new ones if they are not None"

    updated_dict = original_dict.copy()

    for key, value in overrides.items():
        if (
            isinstance(value, dict)
            and key in updated_dict
            and isinstance(updated_dict[key], dict)
        ):
            updated_dict[key] = _update_nested_dict(updated_dict[key], value)
        else:
            if value is not None:
                updated_dict[key] = value

    return updated_dict


class EngineUtil:
    logger = None

    def __init__(self) -> None:
        if not EngineUtil.logger:
            self.sef_logger()

    @staticmethod
    def override_config(config: T, override: dict) -> Type[T]:
        updated_config = replace(config, **override)
        return updated_config

    def load_config(self, cls: T, config_file_path, override: T = None) -> Type[T]:
        with open(config_file_path) as f:
            try:
                config = yaml.safe_load(f.read())

                config = cls(**config)
                if override is not None:
                    config = self.override_nested_config(config, override)
                return config
            except yaml.YAMLError as e:
                self.logger.error(f"{e} for {cls.__name__} in {config_file_path}")
                self.stop_engine(1)
            except TypeError as e:
                self.logger.error(f"{e} for {cls.__name__} in {config_file_path}")
                self.stop_engine(1)

    @staticmethod
    def relative(file, *args):
        return os.path.join(os.path.dirname(file), *args)

    # TODO: 1 fix this one and make sure it's working as expected
    @staticmethod
    def override_nested_config(config: T, override: T) -> Type[T]:
        updated_config = replace(
            config, **_update_nested_dict(config.__dict__, override.__dict__)
        )
        return updated_config

    def remove_folder(self, path):
        "Remove a folder and its contents"

        try:
            process = subprocess.run(["rd", "/s", "/q", path], check=True, shell=True)
            if process.returncode == 0:
                self.logger.info(f"Folder {path} removed")
        except Exception as e:
            self.logger.error(f"Error: {path} : {e}")
            self.stop_engine(1)

    @staticmethod
    def stop_engine(exit_code: int = 0):
        "Stop the engine"

        sys.exit(exit_code)

    def sef_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("\n%(asctime)s - [%(levelname)s] - %(message)s\n")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        self.logger = logger
        EngineUtil.logger = logger
