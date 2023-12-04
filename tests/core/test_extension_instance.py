import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import shutil
from sonic_engine.model.app_config import ExtensionGlobalConfig
from sonic_engine.core.extension_instance import ExtensionInstanceHandler

EXTENSION_CONFIG = ExtensionGlobalConfig(
            name="SampleExtension",
            description="Sample extension description",
            version="1.0.0",
            authors=["Author1", "Author2"],
            license="MIT",
            requirements="requirements.txt",
            channels=None,
            log=None,
            models=None,
            id="sample_id",
            category="Sample Category",
            source="https://github.com/sample_extension",
            branch=None,
            token=None,
            path="/extension_folder"
        )
        


class TestExtensionInstanceHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.handler = ExtensionInstanceHandler(EXTENSION_CONFIG)

        self._remove_ext_path()
        if not os.path.exists(self.handler.config.path):
            self._create_ext_path()
    
    def tearDown(self) -> None:
        self._remove_ext_path()

    def _create_ext_path(self, specific_path=None):
        if specific_path is not None:
            os.makedirs(specific_path)
        else:
            os.makedirs(self.handler.config.path)
    
    def _get_new_handler(self):
        handler = ExtensionInstanceHandler(EXTENSION_CONFIG)
        return handler
    
    def _remove_ext_path(self, specific_path=None):
        if specific_path is not None:
            try:
                shutil.rmtree(specific_path)
            except OSError as e:
                print("Error: %s : %s" % (specific_path, e.strerror))
        else:
            try:
                shutil.rmtree(self.handler.config.path)
            except OSError as e:
                print("Error: %s : %s" % (self.handler.config.path, e.strerror))

    @patch('os.path.exists', return_value=False)
    def test_non_existing_folder(self, mock_path_exists):
        result = self.handler._check_instance_location()

        mock_path_exists.assert_called_once_with(self.handler.config.path)
        assert result == False
    
    @patch('builtins.input', side_effect=['n'])
    @patch('os.path.exists', return_value=True)
    def test_skip_existing_folder(self, mock_path_exists, mock_input):
        result = self.handler._check_instance_location()

        mock_path_exists.assert_called_once_with(self.handler.config.path)
        mock_input.assert_called_once()
        assert result == True

    
    @patch('builtins.input', side_effect=['y'])
    @patch('os.path.exists', return_value=True)
    @patch('sonic_engine.core.extension_instance.engine_util.remove_folder')
    def test_overwrite_existing_folder(self, mock_input, mock_path_exists, mock_remove_folder):
        result = self.handler._check_instance_location()

        mock_input.assert_called_once()
        mock_path_exists.assert_called_once_with(self.handler.config.path)
        mock_remove_folder.assert_called_once_with()
        assert result == False
    
    @patch('sonic_engine.core.extension_instance.engine_util.load_config')
    def test_load_local_configs_success(self, mock_load_config):
        mock_new_config = self.handler.config
        mock_new_config.category = "New Category"
        mock_new_config.id = "new_id"
        mock_new_config.path = "/new_path"
        self._create_ext_path(mock_new_config.path)

        mock_load_config.return_value = mock_new_config
        self.handler._load_local_configs()

        mock_load_config.assert_called_once_with(ExtensionGlobalConfig,
                                                 os.path.join(self.handler.config.path, 'config.yaml'),
                                                 mock_new_config)
        self.assertEqual(self.handler.config, mock_new_config)
        self.assertEqual(self.handler.config.path, mock_new_config.path)
        self._remove_ext_path(mock_new_config.path)
    
    @patch('subprocess.run')
    def test_clone_success(self, mock_subprocess_run):
        mock_subprocess_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_subprocess_completed

        result = self.handler._clone()

        mock_subprocess_run.assert_called_once_with(['git', 'clone', self.handler.config.source, self.handler.config.path], check=True)
        self.assertEqual(result, mock_subprocess_completed)
    
    @patch('subprocess.run')
    def test_clone_success_with_branch(self, mock_subprocess_run):
        mock_subprocess_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_subprocess_completed

        self.handler.config.branch = "new_branch"
        result = self.handler._clone()

        mock_subprocess_run.assert_called_once_with(['git', 'clone', '-b', self.handler.config.branch, self.handler.config.source, self.handler.config.path], check=True)
        self.assertEqual(result, mock_subprocess_completed)

        self.handler.config.branch = None

    @patch('subprocess.run')
    def test_clone_success_with_token(self, mock_subprocess_run):

        self.handler.config.token = "new_token"

        mock_subprocess_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_subprocess_completed
        current_source = self.handler.config.source
        source_with_token = self.handler.config.source.replace(
                "https://", f"https://{self.handler.config.token}:x-oauth-basic@"
            )
        
        result = self.handler._clone()

        mock_subprocess_run.assert_called_once_with(['git', 'clone', source_with_token, self.handler.config.path], check=True)
        self.assertEqual(result, mock_subprocess_completed)

        self.handler.config.token = None
        self.handler.config.source = current_source

    @patch('subprocess.run')
    def test_clone_fail(self, mock_subprocess_run):
        mock_subprocess_completed = MagicMock(returnCode = 1)
        mock_subprocess_run.return_value = mock_subprocess_completed

        result = self.handler._clone()

        mock_subprocess_run.assert_called_once_with(['git', 'clone', self.handler.config.source, self.handler.config.path], check=True)
        self.assertEqual(result, mock_subprocess_completed)

    @patch('os.makedirs')
    @patch('subprocess.run')
    def test_copy_success(self, mock_subprocess_run, mock_os_makedirs):
        mock_os_makedirs.return_value = None
        mock_process_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_process_completed

        result = self.handler._copy()

        mock_os_makedirs.assert_called_once_with(self.handler.config.path)
        mock_subprocess_run.assert_called_once_with(['cp', '-r', self.handler.config.source + "/.", self.handler.config.path], check=True)
        self.assertEqual(result, mock_process_completed)
    
    @patch('platform.system', return_value='Windows')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.join')
    @patch('subprocess.run')
    def test_create_venv_windowns_success(self, mock_subprocess_run, mock_os_path_join, mock_os_path_exists, mock_platform_system):
        mock_venv_path = "/venv_path"
        mock_os_path_join.return_value = mock_venv_path

        mock_process_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_process_completed
        self.handler.system_platform = "Windows"

        result = self.handler._create_venv()

        mock_os_path_exists.assert_called_once_with(mock_venv_path)
        mock_os_path_join.assert_has_calls([
            unittest.mock.call(self.handler.config.path, ".venv"),  # First os.path.join call for creating the venv_path
            unittest.mock.call(mock_venv_path, "Scripts", "python.exe"),  # Second os.path.join call for constructing python_bin
        ])
        mock_subprocess_run.assert_called_once_with(['python', '-m', 'virtualenv', mock_venv_path], check=True)
        expected_python_bin = os.path.join(mock_venv_path, "Scripts", "python.exe")
        self.assertEqual(result, expected_python_bin)

    @patch('os.path.exists', return_value=False)
    @patch('os.path.join')
    @patch('subprocess.run')
    def test_create_venv_linux_success(self, mock_subprocess_run, mock_os_path_join, mock_os_path_exists):
        mock_venv_path = "/venv_path"
        mock_os_path_join.return_value = mock_venv_path

        mock_process_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_process_completed
        self.handler.system_platform = "Linux"

        result = self.handler._create_venv()

        mock_os_path_exists.assert_called_once_with(mock_venv_path)
        mock_os_path_join.assert_has_calls([
            unittest.mock.call(self.handler.config.path, ".venv"),  # First os.path.join call for creating the venv_path
            unittest.mock.call(mock_venv_path, "bin", "python"),  # Second os.path.join call for constructing python_bin
        ])
        mock_subprocess_run.assert_called_once_with(['python', '-m', 'virtualenv', mock_venv_path], check=True)
        expected_python_bin = os.path.join(mock_venv_path, "bin", "python")
        self.assertEqual(result, expected_python_bin)
    
    @patch('sonic_engine.core.extension_instance.engine_util.stop_engine')
    @patch('sonic_engine.core.extension_instance.engine_util.logger')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.join')
    @patch('subprocess.run')
    def test_create_venv_unsupported_platform(self, mock_subprocess_run, mock_os_path_join, mock_os_path_exists, mock_logger, mock_stop_engine):
        mock_venv_path = "/venv_path"
        mock_os_path_join.return_value = mock_venv_path

        mock_process_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_process_completed
        self.handler.system_platform = "UnsupportedPlatform"

        result = self.handler._create_venv()

        mock_os_path_join.assert_called_once_with(self.handler.config.path, ".venv")
        mock_subprocess_run.assert_called_once_with(['python', '-m', 'virtualenv', mock_venv_path], check=True)
        mock_os_path_exists.assert_called_once_with(mock_venv_path)
        mock_stop_engine.assert_called_once_with(1)
        mock_logger.error.assert_called_once_with("Unsupported platform: UnsupportedPlatform for venv")
        self.assertEqual(result, None)
    
    @patch('os.path.exists', return_value=True)
    @patch('os.path.join')
    @patch('subprocess.run')
    def test_install_requirements_success(self, mock_subprocess_run, mock_os_path_join, mock_os_path_exists):
        mock_python_bin = "/python_bin"
        mock_requirements_file = "/extension_folder/requirements.txt"
        mock_os_path_join.return_value = mock_requirements_file

        mock_process_completed = MagicMock(returnCode = 0)
        mock_subprocess_run.return_value = mock_process_completed

        result = self.handler._install_requirements(mock_python_bin)

        mock_os_path_exists.assert_called_once_with(mock_requirements_file)
        mock_os_path_join.assert_called_once_with(self.handler.config.path, self.handler.config.requirements)
        mock_subprocess_run.assert_called_once_with([mock_python_bin, '-m', 'pip', 'install', '-r', mock_requirements_file], check=True)

    @patch('os.path.exists', return_value=False)
    @patch('os.path.join')
    @patch('sonic_engine.core.extension_instance.engine_util.logger')
    @patch('sonic_engine.core.extension_instance.engine_util.stop_engine')
    def test_install_requirements_no_requirements_file(self, mock_stop_engine, mock_logger, mock_os_path_join, mock_os_path_exists):
        mock_python_bin = "/python_bin"
        mock_requirements_file = "/extension_folder/requirements.txt"
        mock_os_path_join.return_value = mock_requirements_file

        self.handler._install_requirements(mock_python_bin)

        mock_os_path_exists.assert_called_once_with(mock_requirements_file)
        mock_os_path_join.assert_called_once_with(self.handler.config.path, self.handler.config.requirements)
        mock_logger.error.assert_called_once_with(f"Requirements file not found for {self.handler.config.id}: {mock_requirements_file}")
        mock_stop_engine.assert_called_once_with(1)


    @patch('os.path.join')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_init_file_windows_success(self, mock_open, mock_os_join_path):
        self.handler.system_platform = "Windows"
        site_packages_for_windows = f"custom_site_packages_path = engine_util.relative(__file__, '.venv/Lib/site-packages')"
        site_packages_64 = f"custom_site_packages_64_path = engine_util.relative(__file__, '.venv/Lib/site-packages')"

        self.handler._write_init_file()

        expected_content = f"""
import sys
from sonic_engine.util.functions import EngineUtil

engine_util = EngineUtil()

{site_packages_for_windows}

{site_packages_64}

sys.path.insert(0, custom_site_packages_path)
sys.path.insert(0, custom_site_packages_64_path)

# fmt: off
from .main import *
    """

        mock_os_join_path.assert_called_once_with(self.handler.config.path, "__init__.py")
        mock_open.assert_called_once_with(mock_os_join_path.return_value, 'w')
        mock_open().write.assert_called_once_with(expected_content)
        
    @patch('sys.version_info', new_callable=lambda: (3, 9, 0))
    @patch('os.path.join')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_init_file_linux_success(self, mock_open, mock_os_join_path, mock_sys_version_info):
        self.handler.system_platform = "Linux"
        site_packages_for_linux = f"custom_site_packages_path = engine_util.relative(__file__, '.venv/lib/python {mock_sys_version_info[0]}.{mock_sys_version_info[1]}/site-packages')"
        site_packages_64_for_linux = f"custom_site_packages_64_path = engine_util.relative(__file__, '.venv/lib64/python{mock_sys_version_info[0]}.{mock_sys_version_info[1]}/site-packages')"

        self.handler._write_init_file()

        expected_content = f"""
import sys
from sonic_engine.util.functions import EngineUtil

engine_util = EngineUtil()

{site_packages_for_linux}

{site_packages_64_for_linux}

sys.path.insert(0, custom_site_packages_path)
sys.path.insert(0, custom_site_packages_64_path)

# fmt: off
from .main import *
    """

        mock_os_join_path.assert_called_once_with(self.handler.config.path, "__init__.py")
        mock_open.assert_called_once_with(mock_os_join_path.return_value, 'w')
        mock_open().write.assert_called_once_with(expected_content)
     
    @patch('os.path.join')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_yapsy_plugin_file_success(self, mock_open, mock_os_join_path):
        self.handler._write_yapsy_plugin_file()

        expected_content = f"""
[Core]
Name = {self.handler.config.name}
Module = .

[Documentation]
Author = {self.handler.config.authors}
Description = {self.handler.config.description}
Version = {self.handler.config.version}
    """
        
        mock_os_join_path.assert_called_once_with(self.handler.config.path, "main.yapsy-plugin")
        mock_open.assert_called_once_with(mock_os_join_path.return_value, 'w')
        mock_open().write.assert_called_once_with(expected_content)

    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._check_instance_location', return_value=True)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._load_local_configs')
    def test_install_skip_isntance_true(self, mock_load_local_configs, mock_check_instance_location):

        result = self.handler.install()

        mock_check_instance_location.assert_called_once()
        mock_load_local_configs.assert_called_once()
        self.assertEqual(result, self.handler.config)
        
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._check_instance_location', return_value=False)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._load_local_configs')
    @patch('os.path.exists', return_value=False)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._clone', return_value=MagicMock(returncode=0))
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._copy', return_value=MagicMock(returncode=0))
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._create_venv', return_value="/python_bin")
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._install_requirements')
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._write_init_file')
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._write_yapsy_plugin_file')
    def test_install_clone_success(self, mock_write_yapsy_plugin_file, mock_write_init_file, mock_install_requirements, mock_create_venv, mock_copy, mock_clone, mock_os_path_exists, mock_load_local_configs, mock_check_instance_location):
        
        result = self.handler.install()

        mock_check_instance_location.assert_called_once()
        mock_clone.assert_called_once()
        mock_copy.assert_not_called()
        mock_load_local_configs.assert_called_once()
        mock_create_venv.assert_called_once()
        mock_install_requirements.assert_called_once_with("/python_bin")
        mock_write_init_file.assert_called_once()
        mock_write_yapsy_plugin_file.assert_called_once()
        mock_os_path_exists.assert_called_once_with(self.handler.config.source)
        self.assertEqual(result, self.handler.config)
    
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._check_instance_location', return_value=False)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._load_local_configs')
    @patch('os.path.exists', return_value=True)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._clone', return_value=MagicMock(returncode=0))
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._copy', return_value=MagicMock(returncode=0))
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._create_venv', return_value="/python_bin")
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._install_requirements')
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._write_init_file')
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._write_yapsy_plugin_file')
    def test_install_copy_success(self, mock_write_yapsy_plugin_file, mock_write_init_file, mock_install_requirements, mock_create_venv, mock_copy, mock_clone, mock_os_path_exists, mock_load_local_configs, mock_check_instance_location):
        
        result = self.handler.install()

        mock_check_instance_location.assert_called_once()
        mock_clone.assert_not_called()
        mock_copy.assert_called_once()
        mock_load_local_configs.assert_called_once()
        mock_create_venv.assert_called_once()
        mock_install_requirements.assert_called_once_with("/python_bin")
        mock_write_init_file.assert_called_once()
        mock_write_yapsy_plugin_file.assert_called_once()
        mock_os_path_exists.assert_called_once_with(self.handler.config.source)
        self.assertEqual(result, self.handler.config)
    
    @patch('sonic_engine.core.extension_instance.engine_util.logger')
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._check_instance_location', return_value=False)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._load_local_configs')
    @patch('os.path.exists', return_value=False)
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._clone', return_value=MagicMock(returncode=1))
    @patch('sonic_engine.core.extension_instance.ExtensionInstanceHandler._copy', return_value=MagicMock(returncode=1))
    def test_install_failure(self, mock_copy, mock_clone, mock_os_path_exists, mock_load_local_configs, mock_check_instance_location, mock_logger):
        
        self.handler.install()

        mock_check_instance_location.assert_called_once()
        mock_os_path_exists.assert_called_once_with(self.handler.config.source)
        mock_load_local_configs.assert_not_called()
        mock_clone.assert_called_once()
        mock_copy.assert_not_called()
        mock_logger.error.assert_called_once_with(f"Error cloning / copying extension: {self.handler.config.id}")

if __name__ == '__main__':
    unittest.main()