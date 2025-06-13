import os
import requests
import subprocess
import sys
import time

GAME_STEAM_ID = "3164500"
REMOTE_VERSION_URL = "https://raw.githubusercontent.com/Ssirnichek/shedule1_rus/main/version.txt"
REMOTE_TRANSLATE_URL = "https://raw.githubusercontent.com/Ssirnichek/shedule1_rus/main/Translate.txt"

# Получение пути к Steam игре
def get_game_install_path():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
        game_path = os.path.join(steam_path, "steamapps", "common", "Schedule I")
        return game_path
    except Exception as e:
        print(f"Ошибка получения пути к Steam: {e}")
        return None

# Уведомление через PowerShell
def notify(title, message):
    script = f'''
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textNodes = $template.GetElementsByTagName("text")
    $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
    $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Schedule I Russian")
    $notifier.Show($toast)
    '''
    subprocess.Popen(["powershell", "-Command", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Получить содержимое файла с GitHub
def get_remote_text(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"Ошибка при получении {url}: {response.status_code}")
    except Exception as e:
        print(f"Исключение при загрузке {url}: {e}")
    return None

def save_text_to_file(path, content):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Ошибка записи в файл {path}: {e}")
        return False

def read_file(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Ошибка чтения файла {path}: {e}")
        return None

def run_steam_game():
    try:
        subprocess.Popen(["cmd", "/c", "start", "", f"steam://rungameid/{GAME_STEAM_ID}"], shell=True)
    except Exception as e:
        notify("Schedule I Russian", f"Ошибка запуска игры: {e}")
        sys.exit(1)

def main():
    print("=== Обновление перевода Schedule I ===")
    game_path = get_game_install_path()
    if not game_path:
        notify("Schedule I Russian", "Не удалось найти путь к игре в Steam!")
        run_steam_game()
        return

    version_path = os.path.join(game_path, "version.txt")
    translate_path = os.path.join(game_path, "AutoTranslator", "Translation", "ru", "Text", "Translate.txt")

    local_version = read_file(version_path) or "0"
    remote_version = get_remote_text(REMOTE_VERSION_URL)
    if not remote_version:
        notify("Schedule I Russian", "Ошибка при проверке версии.")
        run_steam_game()
        return

    if remote_version != local_version:
        notify("Schedule I Russian", f"Найдена новая версия: {remote_version}")
        remote_translate = get_remote_text(REMOTE_TRANSLATE_URL)
        if remote_translate:
            current_translate = read_file(translate_path)
            if current_translate != remote_translate:
                if save_text_to_file(translate_path, remote_translate):
                    save_text_to_file(version_path, remote_version)
                    notify("Schedule I Russian", "Перевод обновлён успешно!")
                    time.sleep(4)
                else:
                    notify("Schedule I Russian", "Ошибка при обновлении перевода!")
                    time.sleep(4)
            else:
                print("Содержимое перевода не изменилось.")
        else:
            notify("Schedule I Russian", "Не удалось скачать перевод.")
            time.sleep(4)
    else:
        print("Версия актуальна, перевод не требуется обновлять.")

    run_steam_game()

if __name__ == "__main__":
    main()
