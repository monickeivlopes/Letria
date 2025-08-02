import os

# 拷贝文件到运行目录
package_dir = os.path.dirname(__file__)
# 获取包的上一级目录
parent_dir = os.path.dirname(package_dir)
root_dir = './api'
init_file_path = os.path.join(root_dir, '__init__.py')
# 根据api目录下 自动生成导入文件
py_files = [f for f in os.listdir(root_dir) if f.endswith('.py') and '__' not in f]
# 获取__init__.py的最新修改时间
if os.path.exists(init_file_path):
    init_file_creation_time = os.path.getmtime(init_file_path)
else:
    init_file_creation_time = 0


def get_latest_file_creation_time(directory):
    files = [file for file in os.listdir(directory) if file.endswith('.py') and '__' not in file]
    latest_creation_time = 0

    for file in files:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            file_creation_time = os.path.getctime(file_path)
            latest_creation_time = max(latest_creation_time, file_creation_time)

    return latest_creation_time


init_file_path = os.path.join(root_dir, '__init__.py')


def get_init_file_line_count(init_file_path):
    with open(init_file_path, 'r') as _init_file_:
        lines = _init_file_.readlines()
        line_count = len(lines)
    return line_count


divide = get_init_file_line_count(init_file_path) != len(py_files)

if get_latest_file_creation_time(root_dir) > init_file_creation_time or divide:
    with open(init_file_path, 'w') as init_file:
        for py_file in py_files:
            file_name = os.path.splitext(py_file)[0]
            module_name = os.path.splitext(py_file)[0]
            module_name = module_name[0].upper() + module_name[1:]
            import_statement = f'from .{file_name} import {module_name}\n'
            init_file.write(import_statement)
