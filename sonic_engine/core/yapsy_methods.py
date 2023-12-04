from yapsy.MultiprocessPluginManager import MultiprocessPluginManager
from yapsy.IMultiprocessPlugin import IMultiprocessPlugin
from sonic_engine.util.dataclass import dataclass
from typing import Union
from sonic_engine.model.extension import FeatureConfig, InferenceConfig, ReportingConfig
from sonic_engine.model.app_config import AppConfigExtension
from sonic_engine.util.functions import EngineUtil
import os

engine_util = EngineUtil()


@dataclass
class YapsyHandler:
    def __init__(
        self,
        extensions_folder,
        global_instances_configs_list: list[
            Union[AppConfigExtension, FeatureConfig, InferenceConfig, ReportingConfig]
        ],
    ):
        self.extensions_folder = extensions_folder
        self.configs_list = global_instances_configs_list

    def _plugin_category(self, plugin: IMultiprocessPlugin):
        return plugin.path.split("/")[-3]

    def _getPluginsLocation(self):
        return [self.extensions_folder]

    def _getPluginConfig(
        self, plugin_path: str
    ) -> Union[AppConfigExtension, FeatureConfig, InferenceConfig, ReportingConfig]:
        # format the plugin path to have the same structure as the isntance configs
        path_components = plugin_path.split(os.path.sep)
        extensions_folder_index = path_components.index(self.extensions_folder)
        formatted_path = os.path.sep.join(
            path_components[extensions_folder_index : extensions_folder_index + 3]
        )

        for config in self.configs_list:
            if config.path == formatted_path:
                return config

    def _plugin_name(self, plugin: IMultiprocessPlugin):
        """
        Get the name of an extension based on its path.

        Args:
            plugin (IMultiprocessPlugin): The plugin object.

        Returns:
            str: The name of the plugin.
        """

        return plugin.path.split("/")[-2]

    def _createManager(self) -> MultiprocessPluginManager:
        """
        Create a Yapsy manager if it doesn't already exist.

        Returns:
            MultiprocessPluginManager: The Yapsy manager.
        """

        if not hasattr(self, "manager"):
            self.manager = MultiprocessPluginManager(
                directories_list=self._getPluginsLocation()
            )
            return self.manager

    def _send_configs(self, plugin, config):
        plugin.plugin_object.child_pipe.send(
            {"config": config, "message": f"Loaded {plugin.name}"}
        )

    def _activatePlugins(self):
        for plugin in self.manager.getAllPlugins():
            if not plugin.plugin_object.is_activated:
                # set plugin name and category
                instance_config = self._getPluginConfig(plugin.path)
                plugin.name = instance_config.id
                plugin.category = instance_config.category

                # activate plugin
                plugin.plugin_object.activate()

                # send instance configs to plugin
                self._send_configs(plugin, instance_config)

    def runAll(self):
        self._createManager()
        self.manager.collectPlugins()
        self._activatePlugins()

    def countAlive(self):
        return len(
            [
                plugin
                for plugin in self.manager.getAllPlugins()
                if plugin.plugin_object.is_activated
            ]
        )

    def killAll(self):
        for plugin in self.manager.getAllPlugins():
            if plugin.plugin_object.is_activated:
                plugin.plugin_object.deactivate()
