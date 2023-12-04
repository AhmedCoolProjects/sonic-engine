from sonic_engine.util.dataclass import nested_dataclass
from sonic_engine.model.extension import (
    ExtensionConfig,
    ModelsPipeline,
    ChannelsPipeline,
    LogConfig,
)
from typing import List, Dict, Union


@nested_dataclass
class AppConfigMetadata:
    "Metadata for the configuration"

    extensions_folder: str
    "Extensions folder name"


@nested_dataclass
class AppConfigCategory:
    "Category class"

    name: str
    "Name of the category"

    description: str
    "Description of the category"


@nested_dataclass
class ExtensionGlobalConfig(ExtensionConfig):
    "Override class for an extension global configs"

    name: str = None

    # ExtensionConfig
    description: str = None
    "Description for the extension"

    version: str = None
    "Version of the extension"

    authors: Union[List[str], str] = None
    "Author(s) of the extension"

    license: str = None
    "License of the extension project"

    requirements: Union[List[str], str] = None
    "a requirement.txt file path"

    channels: ChannelsPipeline = None
    "Map of channels to communicate with other extensions"

    log: LogConfig = None

    models: List[ModelsPipeline] = None

    # AppConfigExtension

    id: str = None
    "Id of the extension"

    category: str = None
    "Category of the extension"

    source: str = None
    "Git url of the extension"

    branch: str = None
    "Branch of the git repository"

    token: str = None
    "Token for the git repository"

    path: str = None
    "Path of the extension"


@nested_dataclass
class AppConfigExtension:
    "Extension class"

    id: str
    "Id of the extension"

    category: str
    "Category of the extension"

    source: str
    "Git url of the extension"

    branch: str = None
    "Branch of the git repository"

    token: str = None
    "Token for the git repository"

    path: str = None
    "Path of the extension"

    override: Dict[str, ExtensionGlobalConfig] = None


@nested_dataclass
class AppConfig:
    "Application configuration"
    
    metadata: AppConfigMetadata
    "Metadata for the configuration"

    categories: List[AppConfigCategory]
    "List of categories"

    extensions: List[AppConfigExtension]
    "List of extensions"