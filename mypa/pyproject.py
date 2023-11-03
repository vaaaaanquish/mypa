from platform import python_version

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from tomlkit.toml_file import TOMLFile


class PyProjectToml:

    def __init__(self):
        self.toml = TOMLFile("pyproject.toml").read()

    def get_mypa_dependencies(self):
        dependencies = self.toml["project"]["dependencies"]
        return [Requirement(x) for x in dependencies]

    def get_python_version(self):
        # tool.mypa.env.pythonセクションがある場合
        mypa_env_python = self.toml.get("tool", {}) \
                                .get("mypa", {}) \
                                .get("env", {}) \
                                .get("python", {}) \
                                .get("version")
        if mypa_env_python:
            return mypa_env_python

        # 利用しているPythonがprojectの条件を満たす場合
        project_python = self.toml["project"].get("requires-python")
        system_python = python_version()
        if project_python and system_python in SpecifierSet(project_python):
            return system_python

        raise Exception('Not found requires python version.')
