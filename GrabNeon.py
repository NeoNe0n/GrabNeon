import os
import sys
import shutil
import subprocess
import importlib
import importlib.util
import pathlib

required_modules = ["yt_dlp", "colorama"]
missing_modules = [m for m in required_modules if importlib.util.find_spec(m) is None]

if missing_modules:
    print(f"Missing libraries detected: {', '.join(missing_modules)}")
    choice = input("Do you want to install missing libraries now? (y/n): ").strip().lower()
    if choice == 'y':
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_modules)
            importlib.invalidate_caches()
        except subprocess.CalledProcessError:
            print("Install failed. Try manually: pip install " + " ".join(missing_modules))
            sys.exit(1)
    else:
        print("Cannot run without required libraries. Exiting...")
        sys.exit(1)

yt_dlp = importlib.import_module("yt_dlp")
colorama = importlib.import_module("colorama")

init = colorama.init
Fore = colorama.Fore
Style = colorama.Style

import time
import getpass

init(autoreset=True)

if os.name == 'nt':
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding="utf-8")

USER_NAME = getpass.getuser()
DEFAULT_DOWNLOAD_PATH = str(pathlib.Path.home() / "Downloads")
current_color = Fore.GREEN


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def set_title():
    if os.name == 'nt':
        os.system("title GrabNeon")


def draw_ui(status_text="", extra_menu=None):
    clear_screen()
    set_title()
    print(current_color + r"""
 ▄█████ ▄████▄   ███   █████▄ ▄█▄  █▄ ▄█████ ▄████▄ ▄█▄  █▄
 ██ ▄▄▄ ██  ██  ██ ██  ██ ▄█▀ ██▀█ ██ ██▄▄   ██  ██ ██▀█ ██
 ██ ▀ █ █████▀ ██▀▀▀██ ██ ▀█▄ ██ █▄██ ██▀▀   ██  ██ ██ █▄██
 ▀█████ ██ ▀█▄  ██ ██  █████▀ ▀█  ██▀ ▀█████ ▀████▀ ▀█  ██▀
  
                        By: NeoNe0n
""")

    if extra_menu:
        for item in extra_menu:
            print(f"    {item}")
        print()

    if status_text:
        print(f"    {Fore.YELLOW}Status: {status_text}\n")

    print(f"    {Fore.LIGHTBLACK_EX}[Folder: {DEFAULT_DOWNLOAD_PATH}]")
    print(f"    {Fore.LIGHTBLACK_EX}[User: {USER_NAME}]\n")


def change_folder():
    global DEFAULT_DOWNLOAD_PATH
    draw_ui("SETTINGS - FOLDER", [
        f"Current Path: {DEFAULT_DOWNLOAD_PATH}"
    ])
    new_path = input(f"    {current_color}Enter new path: {Style.RESET_ALL}").strip()
    # Drag & drop adds quotes, and "~" should expand to the home folder
    new_path = os.path.expanduser(new_path.strip('"\''))
    if new_path:
        DEFAULT_DOWNLOAD_PATH = new_path
        draw_ui("Folder path updated successfully!")
        time.sleep(1.5)


def change_color():
    global current_color
    while True:
        draw_ui("SETTINGS - COLOR", [
            "1 - Cyan",
            "2 - Green",
            "3 - Red",
            "4 - Yellow",
            "5 - Back"
        ])
        c_choice = input(f"    {current_color}> {Style.RESET_ALL}").strip()
        if c_choice == '1':
            current_color = Fore.CYAN
        elif c_choice == '2':
            current_color = Fore.GREEN
        elif c_choice == '3':
            current_color = Fore.RED
        elif c_choice == '4':
            current_color = Fore.YELLOW
        elif c_choice == '5':
            break


def download_media(url):
    try:
        os.makedirs(DEFAULT_DOWNLOAD_PATH, exist_ok=True)
    except OSError as e:
        draw_ui(f"Cannot use folder: {e}")
        input("    Press Enter to continue...")
        return

    # mp3 conversion and mp4 merging both need ffmpeg
    if shutil.which("ffmpeg") is None:
        draw_ui("ffmpeg not found! Install it and add it to PATH first.")
        input("    Press Enter to go back...")
        return

    while True:
        draw_ui("Select Format:", [
            "1 - mp3",
            "2 - mp4"
        ])
        format_choice = input(f"    {current_color}> {Style.RESET_ALL}").strip()
        if format_choice in ('1', '2'):
            break

    ydl_opts = {
        'outtmpl': os.path.join(DEFAULT_DOWNLOAD_PATH, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'windowsfilenames': True,
    }

    if format_choice == '1':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        draw_ui("Downloading media... Please wait.")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        draw_ui("Download completed successfully!")
        time.sleep(2)
    except Exception as e:
        draw_ui(f"Error: {e}")
        input("    Press Enter to continue...")


def main():
    while True:
        draw_ui("Ready", [
            "1 - Folder",
            "2 - Color",
            "3 - Exit",
            "",
            "Or paste a link to download"
        ])

        user_input = input(f"    {current_color}> {Style.RESET_ALL}").strip()

        if user_input == '1':
            change_folder()
        elif user_input == '2':
            change_color()
        elif user_input == '3':
            sys.exit()
        elif user_input.startswith("http://") or user_input.startswith("https://"):
            download_media(user_input)
        else:
            if user_input:
                draw_ui("Invalid input or link!")
                time.sleep(1.5)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nBye!")
        sys.exit(0)