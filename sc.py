# Source Code Extractor
# Author: CYBER ALPHA
# Extracts HTML, CSS, JS, saves to Downloads directory, copies all code to clipboard,
# creates a ZIP, and logs results to a domain-based file

import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pyperclip
import zipfile
from io import BytesIO
from tqdm import tqdm
from datetime import datetime
import webbrowser
import getpass

# === Redirect to WhatsApp Channel First ===
channel_url = "https://whatsapp.com/channel/0029Vb6Fvn4IHphRFHAdtD1S"
webbrowser.open(channel_url)
print("\033[1;33mPlease follow the WhatsApp channel in your browser.\033[0m")
input("\033[1;37m> Press Enter after following to continue...\033[0m")

def clear_screen():
    """Clear the terminal for a clean display."""
    os.system('clear' if os.name == 'posix' else 'cls')

def loading_animation():
    """Display a startup progress bar."""
    print("\033[1;32mInitializing TAM TECH SOURCE EXTRACTOR...\033[0m")
    time.sleep(0.5)
    for i in range(21):
        bar = "█" * i + '-' * (20 - i)
        print(f"\rProgress: [{bar}] {i * 5}%", end='', flush=True)
        time.sleep(0.05)
    print("\n\033[1;32mInitialized.\033[0m\n")

def display_header():
    """Display the tool's header with CYBER ALPHA credit."""
    clear_screen()
    print("\033[1;34m" + "=" * 40)
    print("      TAM TECH SOURCE EXTRACTOR")
    print("=" * 40 + "\033[0m")
    print("\033[0;91mCreated by CYBER ALPHA\033[0m\n")

def main_menu():
    """Show the main menu and get user input."""
    print("\033[1;36m[1] Extract Website (HTML + CSS + JS)")
    print("[2] Copy All Code to Clipboard")
    print("[3] Save Last Extract as ZIP")
    print("[4] Exit\033[0m")
    return input("\n\033[1;37m> Select option (1-4): \033[0m").strip()

def check_storage_permission():
    """Always save to the normal user's Downloads folder, even if running as root."""
    try:
        user_home = os.path.expanduser(f"~{getpass.getuser()}")
        folder_path = os.path.join(user_home, "Downloads")

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        return folder_path
    except Exception as e:
        print(f"\033[0;91mError accessing Downloads folder: {e}\033[0m")
        return os.getcwd()

def sanitize_filename(filename):
    """Sanitize file names to avoid invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:100]

def save_results(url, save_path, fetched_files, success=True, error=None):
    """Save extraction results to a domain-based file."""
    domain = urlparse(url).netloc.replace('.', '_')
    results_file = os.path.join(save_path, f"{domain}_results.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(results_file, "w", encoding="utf-8") as f:
            f.write(f"TAM TECH SOURCE EXTRACTOR - Results\n")
            f.write(f"Created by CYBER ALPHA\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Status: {'Success' if success else 'Failed'}\n")
            if not success:
                f.write(f"Error: {error}\n")
            f.write("\nFiles Saved:\n")
            if fetched_files['html']:
                f.write(f"- HTML: {os.path.join(save_path, 'index.html')}\n")
            for css_file in fetched_files['css']:
                f.write(f"- CSS: {os.path.join(save_path, css_file['filename'])}\n")
            for js_file in fetched_files['js']:
                f.write(f"- JS: {os.path.join(save_path, js_file['filename'])}\n")
        print(f"\033[1;32mResults saved: {results_file}\033[0m")
    except Exception as e:
        print(f"\033[0;91mFailed to save results: {e}\033[0m")

def extract_website():
    """Extract HTML, CSS, and JS files from a website."""
    clear_screen()
    folder_path = check_storage_permission()
    if not folder_path:
        input("\033[1;37m> Press Enter to continue...\033[0m")
        return False, None, None

    url = input("\033[1;37m> Enter website URL (e.g., https://example.com): \033[0m").strip()
    if not url:
        print("\033[0;91m> Enter a valid URL.\033[0m")
        input("\033[1;37m> Press Enter to continue...\033[0m")
        return False, None, None
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    save_path = folder_path
    fetched_files = {'html': '', 'css': [], 'js': []}

    try:
        print("\n\033[1;37mFetching website...\033[0m")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        fetched_files['html'] = response.text

        # Save HTML
        html_path = os.path.join(save_path, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"\033[1;32mHTML saved: {html_path}\033[0m")

        # Gather CSS and JS links
        css_links = [urljoin(url, link.get("href")) for link in soup.find_all("link", rel="stylesheet") if link.get("href")]
        js_links = [urljoin(url, script.get("src")) for script in soup.find_all("script") if script.get("src")]

        all_links = css_links + js_links
        total = len(all_links)
        if total == 0:
            print("\033[0;93mNo CSS or JS files found.\033[0m")
        else:
            print(f"\033[1;37mDownloading {total} files (CSS: {len(css_links)}, JS: {len(js_links)})...\033[0m")
            file_counts = {}
            for i, file_url in enumerate(tqdm(all_links, desc="Progress", ncols=70)):
                try:
                    file_res = requests.get(file_url, timeout=10)
                    file_res.raise_for_status()
                    ext = ".css" if file_url.endswith(".css") else ".js"
                    base_name = urlparse(file_url).path.split('/')[-1] or f"file_{i}"
                    base_name = sanitize_filename(base_name)
                    file_name = base_name + ext
                    if file_name in file_counts:
                        file_counts[file_name] += 1
                        file_name = f"{base_name}_{file_counts[file_name]}{ext}"
                    else:
                        file_counts[file_name] = 0
                    file_path = os.path.join(save_path, file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(file_res.text)
                    if ext == ".css":
                        fetched_files['css'].append({'url': file_url, 'content': file_res.text, 'filename': file_name})
                    else:
                        fetched_files['js'].append({'url': file_url, 'content': file_res.text, 'filename': file_name})
                    print(f"\033[1;32mSaved: {file_name}\033[0m")
                except Exception as e:
                    print(f"\033[0;91mSkipped {file_url}: {e}\033[0m")
                    continue

        save_results(url, save_path, fetched_files)
        print(f"\033[1;32mAll files saved in: {save_path}\033[0m")
        input("\033[1;37m> Press Enter to continue...\033[0m")
        return True, fetched_files, save_path

    except requests.exceptions.RequestException as e:
        print(f"\033[0;91mFailed to fetch {url}: {e}\033[0m")
        save_results(url, save_path, fetched_files, success=False, error=str(e))
        input("\033[1;37m> Press Enter to continue...\033[0m")
        return False, None, None
    except Exception as e:
        print(f"\033[0;91mUnexpected error: {e}\033[0m")
        save_results(url, save_path, fetched_files, success=False, error=str(e))
        input("\033[1;37m> Press Enter to continue...\033[0m")
        return False, None, None

def copy_all_code(fetched_files):
    """Copy all extracted code (HTML, CSS, JS) to clipboard."""
    clear_screen()
    if not fetched_files['html']:
        print("\033[0;91m> Nothing to copy. Extract a URL first.\033[0m")
    else:
        try:
            all_code = fetched_files['html'] + "\n\n/* CSS Files */\n"
            for css_file in fetched_files['css']:
                all_code += f"/* {css_file['filename']} */\n{css_file['content']}\n"
            all_code += "\n/* JS Files */\n"
            for js_file in fetched_files['js']:
                all_code += f"/* {js_file['filename']} */\n{js_file['content']}\n"
            pyperclip.copy(all_code)
            print("\033[1;32m> All code (HTML, CSS, JS) copied to clipboard.\033[0m")
        except Exception as e:
            print(f"\033[0;91m> Failed to copy: {e}\033[0m")
    input("\033[1;37m> Press Enter to continue...\033[0m")

def save_as_zip(fetched_files, save_path):
    """Save all files as a ZIP."""
    clear_screen()
    if not fetched_files['html']:
        print("\033[0;91m> Nothing to zip. Extract a URL first.\033[0m")
    else:
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr('index.html', fetched_files['html'])
                for css_file in fetched_files['css']:
                    zip_file.writestr(f"css/{css_file['filename']}", css_file['content'])
                for js_file in fetched_files['js']:
                    zip_file.writestr(f"js/{js_file['filename']}", js_file['content'])
            zip_path = os.path.join(save_path, 'website_source.zip')
            with open(zip_path, 'wb') as f:
                f.write(zip_buffer.getvalue())
            print(f"\033[1;32m> ZIP saved: {zip_path}\033[0m")
        except Exception as e:
            print(f"\033[0;91m> Failed to create ZIP: {e}\033[0m")
    input("\033[1;37m> Press Enter to continue...\033[0m")

# === Main Execution with KeyboardInterrupt handling ===
try:
    clear_screen()
    loading_animation()
    fetched_files = {'html': '', 'css': [], 'js': []}
    save_path = None

    while True:
        display_header()
        choice = main_menu()
        if choice == "1":
            success, new_files, new_path = extract_website()
            if success:
                fetched_files = new_files
                save_path = new_path
        elif choice == "2":
            copy_all_code(fetched_files)
        elif choice == "3":
            if save_path:
                save_as_zip(fetched_files, save_path)
            else:
                clear_screen()
                print("\033[0;91m> Nothing to zip. Extract a URL first.\033[0m")
                input("\033[1;37m> Press Enter to continue...\033[0m")
        elif choice == "4":
            clear_screen()
            print("\033[1;32mExiting TAM TECH SOURCE EXTRACTOR. Stay sharp!\033[0m")
            break
        else:
            clear_screen()
            print("\033[0;91mInvalid choice. Try again.\033[0m")
            input("\033[1;37m> Press Enter to continue...\033[0m")

except KeyboardInterrupt:
    clear_screen()
    print("\n\033[1;32m[!] Program stopped by user (Ctrl+C).\033[0m")
