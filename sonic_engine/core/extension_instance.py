from sonic_engine.model.app_config import ExtensionGlobalConfig
from sonic_engine.model.extension import FeatureConfig, InferenceConfig, ReportingConfig
from sonic_engine.util.functions import EngineUtil
import os
import platform
import sys
import subprocess
from typing import Union

engine_util = EngineUtil()
UnionType = Union[FeatureConfig, InferenceConfig, ReportingConfig]


class ExtensionInstanceHandler:
    """
    Install the extension by performing several steps such as cloning or copying the extension source code, updating the configuration with local configurations, creating a virtual environment, installing the required packages, and writing the necessary files.

    ## Args:
    - config: An instance of AppConfigExtension, FeatureConfig, InferenceConfig, or ReportingConfig that represents the configuration for the extension.

    ## Outputs:
    - None. The method performs the installation steps for the extension.

    ## Example Usage:\n
    config = AppConfigExtension(...)\n
    handler = ExtensionInstanceHandler(config)\n
    handler.install()

    ## Flow:
    1. The method first checks if the instance folder already exists and prompts the user to replace it or skip it.
    2. If the instance folder does not exist, it either clones the Git repository specified in the configuration or copies the contents of the source directory to the destination directory.
    3. The method then loads local configurations for the extension by calling the loadConfig method from the engineUtil object.
    4. It creates a virtual environment for the extension using the python -m virtualenv command if the virtual environment does not already exist.
    5. The method installs the required packages for the extension by running pip install -r requirements.txt using the Python binary within the virtual environment.
    6. It writes the contents of an __init__.py file that includes import statements and adds custom site packages paths to the Python system path.
    7. Finally, the method writes the Yapsy plugin configuration to a file named main.yapsy-plugin.
    """

    def __init__(self, config: ExtensionGlobalConfig) -> None:
        self.config = config
        self.system_platform = platform.system()

    def install(self):
        """
        Install the extension by performing several steps such as cloning or copying the extension source code, updating the configuration with local configurations, creating a virtual environment, installing the required packages, and writing the necessary files.
        """
        # if the instance folder already exists, ask to replace it or skip it
        skip_instance = self._check_instance_location()
        if skip_instance:
            self._load_local_configs()
            return self.config

        # clone / copy
        if not os.path.exists(self.config.source):
            process = self._clone()
        else:
            process = self._copy()
        if process.returncode != 0:
            engine_util.logger.error(
                f"Error cloning / copying extension: {self.config.id}"
            )
            return None

        # update configs with local configs (overrided if needed)
        self._load_local_configs()

        # create virtual environment
        python_bin = self._create_venv()

        # install requirements
        self._install_requirements(python_bin)

        # write __init__ and yapsy_plugin files
        self._write_init_file()
        self._write_yapsy_plugin_file()

        return self.config

    def _check_instance_location(self):
        """
        Check if a specific path exists and prompt the user to replace or skip the existing instance if it does exist.
        """

        if os.path.exists(self.config.path):
            engine_util.logger.warning(
                f"folder {self.config.path} already exists, would you like to replace it? (y/n)"
            )

            replace = input()
            while replace not in ["y", "n"]:
                engine_util.logger.warning(
                    f"folder {self.config.path} already exists, would you like to replace it? (y/n)"
                )
                replace = input()
            if replace == "y":
                engine_util.remove_folder(self.config.path)
                return False
            else:
                engine_util.logger.info(f"skipping directory: {self.config.path}")
                return True
        else:
            return False

    def _clone(self):
        """
        Clones a Git repository to a specified path.

        :return: The result of the Git clone process.
        """
        if self.config.token:
            self.config.source = self.config.source.replace(
                "https://", f"https://{self.config.token}:x-oauth-basic@"
            )
        if self.config.branch:
            git_command = f"git clone -b {self.config.branch} {self.config.source} {self.config.path}"
        else:
            git_command = f"git clone {self.config.source} {self.config.path}"

        process_completed = subprocess.run(git_command.split(" "), check=True)
        if process_completed.returncode == 0:
            engine_util.logger.info(f"Git repository cloned for {self.config.id}")

        return process_completed

    def _copy(self):
        """
        Copy the contents of the source directory to the destination directory.

        :return: The result of the copy process.
        """
        os.makedirs(self.config.path)
        process_completed = subprocess.run(
            ["cp", "-r", self.config.source + "/.", self.config.path], check=True
        )

        return process_completed

    def _load_local_configs(self):
        """
        Load local configurations for an extension and update the `self.config` attribute.

        This method loads local configurations for an extension by calling the `loadConfig` method from the `engineUtil` object.

        Outputs:
        - None. The method updates the `self.config` attribute with the loaded local configurations.
        """
        try:
            instance_path = self.config.path
            # TODO: it is not returning anything about the config data
            new_config: UnionType = engine_util.load_config(
                ExtensionGlobalConfig,
                os.path.join(self.config.path, "config.yaml"),
                self.config,
            )
            self.config = new_config
            self.config.path = instance_path
        except Exception as e:
            engine_util.logger.error(f"Error loading local configs: {e}")

    # -------------------- Working with local configs --------------------

    def _create_venv(self):
        """
        Create a virtual environment for the extension.

        This method creates a virtual environment for the extension. It checks if the virtual environment already exists and if not, it uses the `subprocess.run` function to run the command `python -m virtualenv` to create the virtual environment. It then returns the path to the Python binary within the virtual environment.

        Returns:
            str: The path to the Python binary within the virtual environment.
        """

        venv_path = os.path.join(self.config.path, ".venv")
        if not os.path.exists(venv_path):
            try:
                process_completed = subprocess.run(
                    ["python", "-m", "virtualenv", venv_path], check=True
                )
                if process_completed.returncode == 0:
                    engine_util.logger.info(
                        f"Virtual environment created for {self.config.id}"
                    )
            except Exception as e:
                engine_util.logger.error(f"Error creating virtual environment: {e}")
        else:
            engine_util.logger.warning(
                f"Virtual environment already exists for {self.config.id}"
            )
        # NOTE: depends on the OS
        # check if the OS is windows or linux
        if self.system_platform == "Windows":
            python_bin = os.path.join(venv_path, "Scripts", "python.exe")
        elif self.system_platform == "Linux":
            python_bin = os.path.join(venv_path, "bin", "python")
        else:
            engine_util.logger.error(
                f"Unsupported platform: {self.system_platform} for venv"
            )
            engine_util.stop_engine(1)
            return None

        return python_bin

    def _install_requirements(self, python_bin):
        """
        Install the required packages for an extension.

        Args:
            python_bin (str): The path to the Python binary that will be used to install the requirements.

        Raises:
            FileNotFoundError: If the requirements file doesn't exist for the specified extension.
        """

        requirements_file = os.path.join(self.config.path, self.config.requirements)

        if os.path.exists(requirements_file):
            try:
                completed_process = subprocess.run(
                    [python_bin, "-m", "pip", "install", "-r", requirements_file],
                    check=True,
                )
                if completed_process.returncode == 0:
                    engine_util.logger.info(
                        f"Requirements installed for {self.config.id}"
                    )
            except Exception as e:
                engine_util.logger.error(
                    f"Error installing requirements: {e} in {python_bin} for {self.config.id}"
                )
        else:
            engine_util.logger.error(
                f"Requirements file not found for {self.config.id}: {requirements_file}"
            )
            engine_util.stop_engine(1)

    def _write_init_file(self):
        """
        Write the contents of an __init__.py file in the specified directory.

        This method generates a script that includes import statements and adds custom site packages paths to the Python system path.
        The script is then written to the __init__.py file.

        Outputs:
        - None. The method writes the script to the __init__.py file.
        """
        python_version = sys.version_info[0:2]  # (3, 9)

        site_packages_for_linux = f"custom_site_packages_path = engine_util.relative(__file__, '.venv/lib/python{python_version[0]}.{python_version[1]}/site-packages')"
        site_packages_for_windows = f"custom_site_packages_path = engine_util.relative(__file__, '.venv/Lib/site-packages')"
        site_packages_64_for_linux = f"custom_site_packages_64_path = engine_util.relative(__file__, '.venv/lib64/python{python_version[0]}.{python_version[1]}/site-packages')"
        if self.system_platform == "Windows":
            site_packages = site_packages_for_windows
            site_packages_64 = f"custom_site_packages_64_path = engine_util.relative(__file__, '.venv/Lib/site-packages')"
        elif self.system_platform == "Linux":
            site_packages = site_packages_for_linux
            site_packages_64 = site_packages_64_for_linux
        else:
            engine_util.logger.error(
                f"Unsupported platform: {self.system_platform} for __init__.py"
            )
            engine_util.stop_engine(1)

        with open(os.path.join(self.config.path, "__init__.py"), "w") as f:
            script = f"""
import sys
from sonic_engine.util.functions import EngineUtil

engine_util = EngineUtil()

{site_packages}

{site_packages_64}

sys.path.insert(0, custom_site_packages_path)
sys.path.insert(0, custom_site_packages_64_path)

# fmt: off
from .main import *
    """
            f.write(script)

    def _write_yapsy_plugin_file(self):
        """
        Write the Yapsy plugin configuration to a file.

        This method takes the plugin configuration values from the `self.config` object and writes them to a file named `main.yapsy-plugin` in the specified `self.config.path`.

        Outputs:
        - None. The method writes the plugin configuration to a file.
        """
        script = f"""
[Core]
Name = {self.config.name}
Module = .

[Documentation]
Author = {self.config.authors}
Description = {self.config.description}
Version = {self.config.version}
    """

        with open(os.path.join(self.config.path, "main.yapsy-plugin"), "w") as f:
            f.write(script)
