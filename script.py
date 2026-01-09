#!/data/data/com.termux/files/usr/bin/python3
import os
import sys
import time
import json
import base64
import zipfile
import tempfile
import shutil
import sqlite3
from pathlib import Path
import traceback
import re

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def setup_imports():
    try:
        import requests
        print(f"{Colors.GREEN}✅ requests siap{Colors.END}")
        return True
    except ImportError:
        print(f"{Colors.RED}❌ requests tidak ditemukan{Colors.END}")
        print(f"{Colors.YELLOW}Menginstal requests...{Colors.END}")
        os.system("pip install requests -q")
        try:
            import requests
            return True
        except:
            return False

if not setup_imports():
    print(f"{Colors.RED}❌ Gagal menginstal requests. Install manual:{Colors.END}")
    print("pip install requests")
    sys.exit(1)

import requests

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "BOT_TOKEN": "",
            "GITHUB_TOKEN": "",
            "GITHUB_USER": "",
            "REPO_NAME": "",
            "ALLOWED_USERS": [],
            "ADMIN_IDS": []
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                for key in self.default_config:
                    if key not in config:
                        config[key] = self.default_config[key]
                self.config = config
                print(f"{Colors.GREEN}✅ Config loaded{Colors.END}")
            except:
                self.config = self.default_config.copy()
                self.save_config()
        else:
            self.config = self.default_config.copy()
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key):
        return self.config.get(key, "")

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def add_allowed_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.config["ALLOWED_USERS"]:
            self.config["ALLOWED_USERS"].append(user_id)
            self.save_config()

    def remove_allowed_user(self, user_id):
        user_id = str(user_id)
        if user_id in self.config["ALLOWED_USERS"]:
            self.config["ALLOWED_USERS"].remove(user_id)
            self.save_config()

    def is_allowed(self, user_id):
        user_id = str(user_id)
        return user_id in self.config["ALLOWED_USERS"] or self.is_admin(user_id)

    def is_admin(self, user_id):
        user_id = str(user_id)
        return user_id in self.config["ADMIN_IDS"]

class GitHubUploader:
    def __init__(self, config):
        self.config = config
        self.headers = {}
        self.update_headers()
        self.uploaded_count = 0
        self.failed_count = 0

    def update_headers(self):
        token = self.config.get("GITHUB_TOKEN")
        if token:
            self.headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GitHub-Bot-Uploader"
            }
        else:
            self.headers = {}

    def get_base_url(self):
        user = self.config.get("GITHUB_USER")
        repo = self.config.get("REPO_NAME")
        if user and repo:
            return f"https://api.github.com/repos/{user}/{repo}"
        return None

    def create_repo(self, repo_name, is_private=False):
        try:
            url = "https://api.github.com/user/repos"
            data = {
                "name": repo_name,
                "private": is_private,
                "auto_init": True
            }
            response = requests.post(url, json=data, headers=self.headers)
            if response.status_code == 201:
                return True, f"✅ Repo '{repo_name}' created"
            else:
                return False, f"❌ Error: {response.json().get('message', 'Unknown')}"
        except Exception as e:
            return False, f"❌ Exception: {str(e)}"

    def upload_file(self, file_path, github_path=""):
        try:
            base_url = self.get_base_url()
            if not base_url:
                return False, "❌ GitHub config not set"

            with open(file_path, 'rb') as f:
                content = f.read()
           
            encoded_content = base64.b64encode(content).decode('utf-8')
            filename = os.path.basename(file_path)
            
            if github_path:
                github_path = github_path.strip('/')
                github_filepath = f"{github_path}/{filename}"
            else:
                github_filepath = filename
            
            github_filepath = github_filepath.replace('//', '/')
            
            print(f"{Colors.CYAN}📤 Uploading: {github_filepath}{Colors.END}")
            
            url = f"{base_url}/contents/{github_filepath}"
            check_response = requests.get(url, headers=self.headers, timeout=10)
            
            data = {
                "message": f"Upload: {github_filepath}",
                "content": encoded_content,
                "branch": "main"
            }
            
            if check_response.status_code == 200:
                existing_data = check_response.json()
                data["sha"] = existing_data["sha"]
                response = requests.put(url, json=data, headers=self.headers, timeout=10)
                action = "updated"
            else:
                response = requests.put(url, json=data, headers=self.headers, timeout=10)
                action = "uploaded"
            
            if response.status_code in [200, 201]:
                self.uploaded_count += 1
                return True, f"✅ {action}: {github_filepath}"
            else:
                self.failed_count += 1
                error_msg = response.json().get('message', 'Unknown error')
                return False, f"❌ Error {response.status_code}: {error_msg}"
                
        except Exception as e:
            self.failed_count += 1
            return False, f"❌ Exception: {str(e)}"

    def upload_zip_contents(self, zip_path, chat_id, bot):
        try:
            total_files = 0
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for file_info in zf.infolist():
                    if not file_info.is_dir():
                        total_files += 1
            
            bot.send_message(chat_id, f"📦 ZIP contains {total_files} files")
            
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(tmpdir)
                
                all_files = []
                for root, dirs, files in os.walk(tmpdir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, tmpdir)
                        all_files.append((full_path, rel_path))
                
                bot.send_message(chat_id, f"📂 Found {len(all_files)} files")
                
                for idx, (full_path, rel_path) in enumerate(all_files, 1):
                    github_dir = os.path.dirname(rel_path)
                    success, result = self.upload_file(full_path, github_dir)
                    
                    if idx % 10 == 0 or idx == len(all_files):
                        bot.send_message(chat_id, f"📊 Progress: {idx}/{len(all_files)}")
                    
                    if not success:
                        bot.send_message(chat_id, f"⚠️ Failed: {rel_path}")
                
                summary = f"""
🎉 ZIP UPLOAD COMPLETE
├ ✅ Success: {self.uploaded_count} files
└ ❌ Failed: {self.failed_count} files
                """
                bot.send_message(chat_id, summary)
                return True, f"Uploaded {self.uploaded_count} files"
                
        except Exception as e:
            return False, f"❌ ZIP Error: {str(e)}"

    def list_files(self, path=""):
        try:
            base_url = self.get_base_url()
            if not base_url:
                return False, "❌ GitHub config not set"
            
            url = f"{base_url}/contents/{path}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                files = []
                for item in response.json():
                    if item['type'] == 'file':
                        size_kb = item.get('size', 0) / 1024
                        files.append(f"📄 {item['name']} ({size_kb:.1f} KB)")
                    elif item['type'] == 'dir':
                        files.append(f"📁 {item['name']}/")
                
                if files:
                    return True, "\n".join(files[:30])
                else:
                    return True, "📭 Empty"
            else:
                return False, f"❌ Error: {response.status_code}"
        except Exception as e:
            return False, str(e)

class SimpleTelegramBot:
    def __init__(self, config):
        self.config = config
        self.bot_token = config.get("BOT_TOKEN")
        self.github = GitHubUploader(config)
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        self.user_sessions = {}

    def send_message(self, chat_id, text, parse_mode="HTML"):
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"{Colors.RED}Send message error: {e}{Colors.END}")
            return None

    def download_file(self, file_id):
        try:
            url = f"{self.base_url}/getFile"
            params = {"file_id": file_id}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                file_info = response.json()
                if file_info.get("ok"):
                    file_path = file_info["result"]["file_path"]
                    download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
                    file_response = requests.get(download_url, timeout=30)
                    
                    filename = os.path.basename(file_path)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
                    temp_file.write(file_response.content)
                    temp_file.close()
                    
                    return temp_file.name, filename
            return None, None
        except Exception as e:
            print(f"{Colors.RED}Download error: {e}{Colors.END}")
            return None, None

    def handle_message(self, message):
        chat_id = message["chat"]["id"]
        user_id = str(message["from"]["id"])
        
        if not self.config.is_allowed(user_id):
            self.send_message(chat_id, "❌ Access denied!")
            return

        if "text" in message:
            text = message["text"]
            
            if text.startswith("/start"):
                welcome = """
🤖 GitHub Upload Bot

📤 Features:
• Upload any file
• Auto extract ZIP
• Multi-user support
• GitHub push

📝 Commands:
/start - Start bot
/setconfig - Set GitHub config
/list - List files
/users - Manage users (admin)
/help - Show help
                """
                self.send_message(chat_id, welcome)
            
            elif text.startswith("/setconfig"):
                if not self.config.is_admin(user_id):
                    self.send_message(chat_id, "❌ Admin only!")
                    return
                
                self.user_sessions[user_id] = "awaiting_github_token"
                self.send_message(chat_id, "🔑 Send GitHub token:")
            
            elif text.startswith("/list"):
                self.send_message(chat_id, "🔄 Fetching files...")
                success, result = self.github.list_files()
                if success:
                    self.send_message(chat_id, f"📂 Files:\n\n{result}")
                else:
                    self.send_message(chat_id, f"❌ {result}")
            
            elif text.startswith("/users"):
                if not self.config.is_admin(user_id):
                    self.send_message(chat_id, "❌ Admin only!")
                    return
                
                users = self.config.config["ALLOWED_USERS"]
                if users:
                    user_list = "\n".join([f"👤 {uid}" for uid in users])
                    msg = f"👥 Allowed Users:\n{user_list}"
                else:
                    msg = "📭 No allowed users"
                self.send_message(chat_id, msg)
            
            elif text.startswith("/adduser"):
                if not self.config.is_admin(user_id):
                    self.send_message(chat_id, "❌ Admin only!")
                    return
                
                parts = text.split()
                if len(parts) > 1:
                    new_user = parts[1]
                    self.config.add_allowed_user(new_user)
                    self.send_message(chat_id, f"✅ User {new_user} added")
            
            elif text.startswith("/removeuser"):
                if not self.config.is_admin(user_id):
                    self.send_message(chat_id, "❌ Admin only!")
                    return
                
                parts = text.split()
                if len(parts) > 1:
                    remove_user = parts[1]
                    self.config.remove_allowed_user(remove_user)
                    self.send_message(chat_id, f"🗑️ User {remove_user} removed")
            
            elif text.startswith("/help"):
                help_text = """
❓ Help:

For Admins:
/setconfig - Set GitHub config
/users - List allowed users
/adduser <id> - Add user
/removeuser <id> - Remove user

For Users:
Just send any file or ZIP!
/list - View repository files
                """
                self.send_message(chat_id, help_text)
            
            else:
                if user_id in self.user_sessions:
                    session = self.user_sessions[user_id]
                    
                    if session == "awaiting_github_token":
                        self.config.set("GITHUB_TOKEN", text)
                        self.user_sessions[user_id] = "awaiting_github_user"
                        self.send_message(chat_id, "✅ Token saved!")
                        self.send_message(chat_id, "👤 Send GitHub username:")
                    
                    elif session == "awaiting_github_user":
                        self.config.set("GITHUB_USER", text)
                        self.user_sessions[user_id] = "awaiting_repo_name"
                        self.send_message(chat_id, "✅ Username saved!")
                        self.send_message(chat_id, "📁 Send repository name:")
                    
                    elif session == "awaiting_repo_name":
                        self.config.set("REPO_NAME", text)
                        self.github.update_headers()
                        del self.user_sessions[user_id]
                        
                        test_url = self.github.get_base_url()
                        try:
                            response = requests.get(test_url, headers=self.github.headers, timeout=10)
                            if response.status_code == 200:
                                self.send_message(chat_id, "✅ Config saved! Repository accessible.")
                            elif response.status_code == 404:
                                self.send_message(chat_id, "⚠️ Repo not found. Create it? (yes/no)")
                                self.user_sessions[user_id] = "confirm_create_repo"
                            else:
                                self.send_message(chat_id, "✅ Config saved!")
                        except Exception as e:
                            print(f"{Colors.YELLOW}Test repo error: {e}{Colors.END}")
                            self.send_message(chat_id, "✅ Config saved!")
                    
                    elif session == "confirm_create_repo":
                        if text.lower() == "yes":
                            self.send_message(chat_id, "Creating repository...")
                            success, result = self.github.create_repo(self.config.get("REPO_NAME"))
                            self.send_message(chat_id, result)
                        else:
                            self.send_message(chat_id, "⚠️ Repository not created")
                        del self.user_sessions[user_id]
        
        elif "document" in message:
            document = message["document"]
            filename = document["file_name"]
            file_id = document["file_id"]
            
            self.send_message(chat_id, f"📥 Downloading: {filename}")
            
            temp_path, downloaded_name = self.download_file(file_id)
            
            if temp_path:
                if filename.lower().endswith('.zip'):
                    self.send_message(chat_id, "📦 ZIP Detected!")
                    self.github.uploaded_count = 0
                    self.github.failed_count = 0
                    
                    success, result = self.github.upload_zip_contents(temp_path, chat_id, self)
                    if not success:
                        self.send_message(chat_id, f"❌ {result}")
                else:
                    self.send_message(chat_id, f"📤 Uploading: {filename}")
                    success, result = self.github.upload_file(temp_path)
                    if success:
                        self.send_message(chat_id, f"✅ {result}")
                    else:
                        self.send_message(chat_id, f"❌ {result}")
                
                try:
                    os.unlink(temp_path)
                except:
                    pass
            else:
                self.send_message(chat_id, "❌ Download failed")

    def run_polling(self):
        print(f"{Colors.GREEN}🤖 Bot starting...{Colors.END}")
        
        while True:
            try:
                url = f"{self.base_url}/getUpdates"
                params = {
                    "offset": self.last_update_id + 1,
                    "timeout": 30,
                    "allowed_updates": ["message"]
                }
                
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok") and data.get("result"):
                        for update in data["result"]:
                            self.last_update_id = update["update_id"]
                            if "message" in update:
                                self.handle_message(update["message"])
                else:
                    print(f"{Colors.YELLOW}⚠️ API error: {response.status_code}{Colors.END}")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}🛑 Bot stopped{Colors.END}")
                break
            except requests.exceptions.Timeout:
                continue
            except Exception as e:
                print(f"{Colors.RED}❌ Polling error: {e}{Colors.END}")
                time.sleep(5)

def main():
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}🤖 GITHUB UPLOAD BOT{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    config = ConfigManager()
    
    if not config.get("BOT_TOKEN"):
        print(f"{Colors.YELLOW}⚠️ Bot token not set!{Colors.END}")
        bot_token = input(f"{Colors.CYAN}Enter bot token: {Colors.END}")
        config.set("BOT_TOKEN", bot_token.strip())
    
    if not config.get("ADMIN_IDS"):
        print(f"{Colors.YELLOW}⚠️ No admin set!{Colors.END}")
        admin_id = input(f"{Colors.CYAN}Enter your Telegram ID: {Colors.END}")
        config.set("ADMIN_IDS", [admin_id.strip()])
    
    print(f"{Colors.GREEN}✅ Bot ready!{Colors.END}")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.END}")
    
    bot = SimpleTelegramBot(config)
    bot.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 Bye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal: {e}{Colors.END}")
        traceback.print_exc()
