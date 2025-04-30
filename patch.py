import shutil
import importlib.util
import os

# Имя библиотеки
LIB_NAME = "manimlib"

# Файлы, которые нужно заменить (относительно папки библиотеки)
PATCH_FILES = {
    "tex_templates.yml": "patches/tex_templates.yml",
    "utils/tex_file_writing.py": "patches/tex_file_writing.py",
    "utils/directories.py": "patches/directories.py",
}


def find_library_path(lib_name):
    spec = importlib.util.find_spec(lib_name)
    if spec and spec.origin:
        return os.path.dirname(spec.origin)
    raise ImportError(f"Не удалось найти библиотеку '{lib_name}'")


def apply_patches():
    lib_path = find_library_path(LIB_NAME)
    print(f"[INFO] Библиотека найдена в: {lib_path}")

    for relative_path, patch_path in PATCH_FILES.items():
        target_path = os.path.join(lib_path, relative_path)
        print(f"[PATCH] {patch_path} → {target_path}")
        shutil.copy2(patch_path, target_path)

    print("[DONE] Патчи применены!")


if __name__ == "__main__":
    apply_patches()
