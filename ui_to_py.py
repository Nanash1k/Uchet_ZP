import os
import re


def ui_to_py(path: str):
    files = os.listdir(path)
    ui_list = []
    pattern = re.compile(r'.*\.ui')
    for it in files:
        if pattern.match(it):
            ui_list.append(it)

    for it in ui_list:
        file_path = os.path.join(path, it)
        file_name_without_extension = file_path.split(os.sep)[-1].removesuffix('.ui')
        cmd = f'pyside6-uic {file_path} > {path}{os.sep}{file_name_without_extension}.py'
        os.popen(cmd)


if __name__ == '__main__':
    ui_to_py(os.path.dirname((os.path.abspath(__file__))))