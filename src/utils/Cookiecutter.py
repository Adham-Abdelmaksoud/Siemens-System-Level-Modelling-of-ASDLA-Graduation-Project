from utils.Singleton import Singleton
import os
import pathlib
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QProcess
from PySide6.QtUiTools import QUiLoader
import cookiecutter.main
import cookiecutter.prompt
from jinja2 import Environment, FileSystemLoader
from paths.SystemPaths import SystemPaths
import json
from cookiecutter.main import cookiecutter
basedir = os.path.dirname(__file__)
loader = QUiLoader()


class Cookiecutter(metaclass=Singleton):
    def __init__(self, jinja_templates, debug) -> None:
        self.SysPath = SystemPaths()
        self.debug = debug
        self.SysPath.jinja_templates_path = jinja_templates
        self.jinja_template_filename = "cookiecutter.json.jinja"

    def render_cookiecutter_template(self, src_cookie_json_path, output_cookie_json_path, template_dir):
        path_arch_json, _ = QFileDialog.getOpenFileName(
            None, "Load Architecture JSON file",  self.SysPath.jsondir, "JSON Files (*.json)"
        )
        path_output = None
        if path_arch_json:
            data = None
            with open(path_arch_json, "r") as json_file:
                data = json.load(json_file)

            if 'list' in data['layers']:
                data['residual'] = {'layers': {'list': []}}
                for layer in data['layers']['list']:
                    if layer['type'] == 'Residual_Block':
                        path_residual_json, _ = QFileDialog.getOpenFileName(
                            None, "Load Residual Block JSON file", self.SysPath.jsondir, "JSON Files (*.json)"
                        )
                        with open(path_residual_json, "r") as json_file:
                            data['residual'] = json.load(json_file)
                        break

            path_output = QFileDialog.getExistingDirectory(
                None, "Pick a folder to save the output", self.SysPath.jsondir
            )
            self.SysPath.jsondir = path_output
            self.cookicutterpreproccess(
                data, src_cookie_json_path, output_cookie_json_path
            )
            self.generate_project(
                template_dir, path_output
            )
        return path_output

    def generate_project(self, template_path, output_path):
        cookiecutter(template_path, output_dir=output_path,
                     no_input=True,  overwrite_if_exists=True)

    def cookicutterpreproccess(self, data, src_cookie_json_path, output_cookie_json_path):
        env = Environment(loader=FileSystemLoader(src_cookie_json_path))
        if self.debug:
            print(src_cookie_json_path, output_cookie_json_path,
                  self.SysPath.jinja_templates_path)
        template = env.get_template(self.jinja_template_filename)

        data = self.remove_empty_arrays(data)
        result_file = template.render(
            my_dict=json.dumps(data, indent=4)
        )
        with open(output_cookie_json_path, "w") as json_file:
            json_file.write(str(result_file))

    def remove_empty_arrays(self, d):
        return {k: v for k, v in d.items() if v != []}
