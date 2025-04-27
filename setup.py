import os
import shutil
import subprocess
import requests
from tqdm import tqdm
from zipfile import ZipFile
import argparse


def check_available(args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def is_ffmpeg_available():
    return check_available(["ffmpeg", "-version"])


def is_miktex_available():
    return check_available(["miktex", "--version"])


def download_and_extract(url, target_dir, zip_name):
    zip_path = os.path.join(target_dir, zip_name)

    print(f"[INFO] Скачивание {zip_name}...")

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024

    with open(zip_path, "wb") as f, tqdm(
        total=total_size, unit="iB", unit_scale=True, desc=f"Скачивание {zip_name}"
    ) as bar:
        for data in response.iter_content(block_size):
            f.write(data)
            bar.update(len(data))

    with ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    os.remove(zip_path)
    print(f"[DONE] {zip_name} скачан и распакован!")

    return zip_ref.namelist()[0].split("/")[0]  # Возвращаем имя папки


def install_ffmpeg(target_dir):
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    extracted_folder = download_and_extract(url, target_dir, "ffmpeg.zip")
    extracted_folder_path = os.path.join(target_dir, extracted_folder)

    print("[INFO] Поиск ffmpeg.exe...")

    for root, _, files in os.walk(extracted_folder_path):
        if "ffmpeg.exe" in files:
            src = os.path.join(root, "ffmpeg.exe")
            dst = os.path.join(target_dir, "ffmpeg.exe")
            shutil.move(src, dst)
            print("[DONE] ffmpeg.exe найден и перемещён!")
            break
    else:
        print("[ERROR] ffmpeg.exe не найден!")

    print("[INFO] Очистка временных файлов...")
    shutil.rmtree(extracted_folder_path, ignore_errors=True)
    print("[DONE] Очистка завершена!")


def install_miktex(target_dir):
    url = "https://miktex.org/download/win/miktexsetup-x64.zip"
    extracted_folder = download_and_extract(url, target_dir, "miktex.zip")

    setup_exe = os.path.join(target_dir, "miktexsetup_standalone.exe")

    print("[INFO] Скачивание пакетов MikTeX...")
    os.system(f'"{setup_exe}" --verbose --package-set=basic download')
    print("[DONE] Пакеты MikTeX скачаны!")

    print("[INFO] Установка MikTeX...")
    os.system(f'"{setup_exe}" --verbose --package-set=basic install')
    print("[DONE] MikTeX установлен!")

    print("[INFO] Установка шрифтов...")
    os.system("miktex packages install cm-super")
    print("[DONE] Шрифты установлены!")

    print("[INFO] Очистка временных файлов...")
    if os.path.exists(setup_exe):
        os.remove(setup_exe)
    extracted_folder_path = os.path.join(target_dir, extracted_folder)
    if os.path.exists(extracted_folder_path):
        shutil.rmtree(extracted_folder_path, ignore_errors=True)
    print("[DONE] Очистка завершена!")


def run_example_scene():
    from runner import run
    from manimlib import Scene, Tex, Write, VGroup, DOWN

    class ExampleScene(Scene):
        def construct(self):
            tex1 = Tex("\\text{Если вы получили это сообщение,}")
            tex2 = Tex("\\text{то установка прошла успешно!}")
            tex = VGroup(tex1, tex2).arrange(DOWN)
            self.play(Write(tex))

    run(ExampleScene)


def main():
    parser = argparse.ArgumentParser(description="Установка зависимостей для проекта.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Принудительно переустановить ffmpeg и MikTeX.",
    )
    parser.add_argument(
        "--skip-example", action="store_true", help="Пропустить запуск пример-сцены."
    )
    args = parser.parse_args()

    current_dir = os.getcwd()

    # Установка ffmpeg
    if args.force or not is_ffmpeg_available():
        print("[INFO] Устанавливаем ffmpeg...")
        install_ffmpeg(current_dir)
    else:
        print("[INFO] ffmpeg уже установлен.")

    # Установка MikTeX
    if args.force or not is_miktex_available():
        print("[INFO] Устанавливаем MikTeX...")
        install_miktex(current_dir)
    else:
        print("[INFO] MikTeX уже установлен.")

    # Пример сцены
    if not args.skip_example:
        print("[INFO] Запуск пример-сцены...")
        run_example_scene()


if __name__ == "__main__":
    main()
