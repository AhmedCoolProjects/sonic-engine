from sonic_engine.model.app_config import AppConfigExtension, ExtensionGlobalConfig
from sonic_engine.core.extension_instance import ExtensionInstanceHandler
from sonic_engine.util.functions import EngineUtil
import os

engine_util = EngineUtil()


class ExtensionHandler:
    """
    A class that handles the installation of an extension.
    """

    def __init__(self, extensions_folder: str, config: AppConfigExtension):
        """
        Initialize the ExtensionHandler class with a configuration object.

        :param config: The configuration object for the extension.
        :type config: AppConfigExtension
        """
        self.extensions_folder = extensions_folder
        self.config = config

    def install(self):
        """
        Install all instances of the extension.

        Loop through the list of instance configurations and then call the `install` method on each instance.
        """
        instances_configs_list = self._create_instances_list()

        instances_global_configs_list: list = []

        for instance in instances_configs_list:
            instanceHandler = ExtensionInstanceHandler(instance)
            instance_configs = instanceHandler.install()
            instances_global_configs_list.append(instance_configs)

        return instances_global_configs_list

    def _create_instances_list(self) -> list[ExtensionGlobalConfig]:
        """
        Create a list of instance configurations based on the default configuration and any overrides specified in the `config` attribute.

        :return: A list of instance configurations, including the default configuration and any overrides specified in the `config` attribute.
        :rtype: list[AppConfigExtension]
        """

        default_config_dict = self.config.__dict__.copy()
        default_config_dict.pop("override")
        default_config = ExtensionGlobalConfig(**default_config_dict)

        instances_list: list[ExtensionGlobalConfig] = [default_config]
        "fill the instances list with their configs"

        if self.config.override is not None:
            for instance_id in self.config.override.keys():
                # if we gonna override the default instance
                if instance_id == self.config.id:
                    instances_list[0] = engine_util.override_config(
                        default_config, self.config.override[instance_id]
                    )
                    engine_util.logger.info(
                        f"Overriding default instance for {instance_id}"
                    )
                # if we gonna create a duplicate instance
                else:
                    self.config.override[instance_id]["id"] = instance_id
                    instances_list.append(
                        engine_util.override_config(
                            default_config, self.config.override[instance_id]
                        )
                    )
        # updating the instance path
        for instance in instances_list:
            instance.path = os.path.join(
                self.extensions_folder, instance.category, instance.id
            )
        engine_util.logger.info(
            f"extension {self.config.id} configs loaded with {len(instances_list)} instances"
        )
        return instances_list
