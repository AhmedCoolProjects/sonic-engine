import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import shutil
from sonic_engine.model.app_config import ExtensionGlobalConfig, AppConfigExtension
from sonic_engine.core.extension import ExtensionHandler

EXTENSION_FOLDER = "extensions_folder"
APP_CONFIG_EXTENSION = AppConfigExtension(
    id="test_extension_id",
    category="test_category",
    source="https://test_source",
    override={
        "test_extension_id_2": ExtensionGlobalConfig(
            description="test_description_2",
        ),
        "test_extension_id_3": ExtensionGlobalConfig(
            description="test_description_3",
            branch="test_branch_3",
        ),

    }
)

DEFAULT_CONFIG = ExtensionGlobalConfig(
    source="https://test_source",
    category="test_category",
    id="test_extension_id"
)

# class TestExtensionHandler(unittest.TestCase):

#     def setUp(self) -> None:
#         self.handler = ExtensionHandler(EXTENSION_FOLDER, APP_CONFIG_EXTENSION)

#     @patch("sonic_engine.core.extension.engine_util.override_config")
#     @patch("sonic_engine.core.extension.engine_util.logger")
#     @patch('os.path.join')
#     def test_create_instances_list_override_no_default(self, mock_os_path_join, mock_logger, mock_override_config):
        


#         result = self.handler._create_instances_list()

#         mock_override_config.assert_has_calls([
#             unittest.mock.call(
#                 DEFAULT_CONFIG, APP_CONFIG_EXTENSION.override["test_extension_id_2"]
#             ),
#             unittest.mock.call(
#                 DEFAULT_CONFIG, APP_CONFIG_EXTENSION.override["test_extension_id_3"]
#             )
#         ])
#         mock_os_path_join.assert_has_calls([
#             unittest.mock.call(EXTENSION_FOLDER, self.handler.config.category, "test_extension_id"),
#             unittest.mock.call(EXTENSION_FOLDER, self.handler.config.category, "test_extension_id_2"),
#             unittest.mock.call(EXTENSION_FOLDER, self.handler.config.category, "test_extension_id_3")
#         ])
#         mock_logger.info.assert_called_once_with(f"extension {self.handler.config.id} configs loaded with {len(result)} instances")
#         self.assertEqual(len(result), 3)

# if __name__ == '__main__':
#     unittest.main()