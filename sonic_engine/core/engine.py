import os
from shutil import which
from time import sleep
from sonic_engine.core.extension import ExtensionHandler
from sonic_engine.core.yapsy_methods import YapsyHandler
from sqlite3 import NotSupportedError
import redis
from sonic_engine.model.app_config import AppConfig, AppConfigExtension
from sonic_engine.util.functions import EngineUtil

engine_util = EngineUtil()


class Engine:
    """
    This class manages the execution of a program. It checks if Redis database is running, installs and runs extensions, and handles program termination.

    Example Usage:
    ```python
    # Create an instance of the Engine class
    engine = Engine(("path/to/config", "config_file_name"))

    # Start the program
    engine.start()
    ```
    """

    def __init__(self, config_file: tuple) -> None:
        """
        Initializes the Engine object by loading the configuration file.

        Args:
        - config_file (tuple): A tuple containing the path to the configuration file and the name of the file.

        Returns:
        - None
        """
        config_file_path = engine_util.relative(config_file[0], config_file[1])
        self.config: AppConfig = engine_util.load_config(
            cls=AppConfig, config_file_path=config_file_path
        )

    def _check_redis(self):
        """
        Checks if Redis database is running and starts it if necessary.

        Returns:
        - None
        """
        try:
            import sonic_engine.core.database

            engine_util.logger.info("Redis is running!")

        except redis.exceptions.ConnectionError:
            if which("redis-server") is None:
                raise NotSupportedError("redis-server must be installed!")
            msg = 'Looks like Redis database is not running, run "redis-server --daemonize yes"? (y/n) '
            response = input(msg)
            while response not in ["y", "n"]:
                response = input(msg)
            if response == "y":
                os.system("redis-server --daemonize yes")
                sleep(5)
                engine_util.logger.info("Redis started running!")
            else:
                engine_util.logger.error("Redis is NOT running!")
                raise ConnectionError("Redis database is not running!")

    def start(self) -> None:
        """
        Starts the program by installing and running extensions, and handling program termination.

        Returns:
        - None
        """
        # check if redis is running
        self._check_redis()

        instances_configs_list: list = []
        "a list of installed extensions instances global configurations"

        # loop through extensions and install them
        for config_extension in self.config.extensions:
            extension = ExtensionHandler(
                self.config.metadata.extensions_folder,
                AppConfigExtension(**config_extension),
            )
            extension_instances_configs: list = extension.install()
            instances_configs_list.extend(extension_instances_configs)

        # create the yapsy handler and run all
        yapsy_handler = YapsyHandler(
            self.config.metadata.extensions_folder, instances_configs_list
        )
        yapsy_handler.runAll()

        try:
            while yapsy_handler.countAlive():
                try:
                    sleep(1)
                except KeyboardInterrupt:
                    # You can perform any cleanup or additional actions here if needed
                    engine_util.logger.info("Exiting the program.")
                    yapsy_handler.killAll()
                    break  # Break out of the while loop
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle the exception as needed
        finally:
            # Perform cleanup actions here, if any
            print("Exiting the program.")
