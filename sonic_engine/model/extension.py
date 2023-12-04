from typing import List, Literal, Union
from sonic_engine.util.dataclass import nested_dataclass

# from sonic_engine.model.app_config import AppConfigExtension


@nested_dataclass
class LogConfig:
    "Extension logs configuration"

    level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "DEBUG"
    "Log level"

    dir: str = "./logs"
    "Path to the logs folder"


@nested_dataclass
class Input:
    "Feature extensions sources identifiers"

    files: List[str] = None
    "List of files paths"

    interfaces: List[str] = None
    "List of network interfaces names"


# CHANNELS


@nested_dataclass
class ChannelsPipeline:
    "Abstract pipeline channels identifiers"

    input: Input = None

    subscribe: List[str] = None

    publish: List[str] = None


@nested_dataclass
class FeatureChannel(ChannelsPipeline):
    "Feature extension channel identifiers"

    input: Input
    "Input channel identifiers"

    publish: List[str]
    "Publish channel identifiers"


@nested_dataclass
class InferenceChannel(ChannelsPipeline):
    "Inference extension channel identifiers"

    subscribe: List[str]
    "Redis channels to subscribe to"

    publish: List[str]
    "Redis channels to publish into"


@nested_dataclass
class ReportingChannel(ChannelsPipeline):
    "Reporting extension channel identifiers"

    subscribe: List[str]
    "Redis channels to subscribe to"


# TODO: check


@nested_dataclass
class ModelsPipeline:
    "Abstract pipeline model identifiers"


# Extension configuration


@nested_dataclass
class ExtensionConfig:
    "The base class for every extension local configuration"

    id: str
    "An identifier for the extension"

    name: str

    description: str
    "Description for the extension"

    version: str
    "Version of the extension"

    authors: Union[List[str], str]
    "Author(s) of the extension"

    license: str
    "License of the extension project"

    requirements: Union[List[str], str]
    "a requirement.txt file path"

    channels: ChannelsPipeline
    "Map of channels to communicate with other extensions"

    log: LogConfig

    category: str = None

    path: str = None

    models: List[ModelsPipeline] = None

    def __post_init__(self):
        """
        Initializes the `log` field with a default value if it is not provided during object creation.
        """

        if self.log is None:
            self.log = LogConfig()


@nested_dataclass
class FeatureConfig(ExtensionConfig):
    channels: FeatureChannel


@nested_dataclass
class InferenceConfig(ExtensionConfig):
    "Inference extension configuration class"

    channels: InferenceChannel


@nested_dataclass
class ReportingConfig(ExtensionConfig):
    "Reporting extension configuration class"

    channels: ReportingChannel
