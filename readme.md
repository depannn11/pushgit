```md
# 🤖 GitHub Upload Bot

A powerful Telegram bot for automatic file uploads to GitHub repositories with multi-user support, ZIP auto-extraction, and real-time file management.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-Bot-green.svg" alt="Telegram">
  <img src="https://img.shields.io/badge/GitHub-API-lightgrey.svg" alt="GitHub">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

## ✨ Features

- 📤 **One-Click Upload** - Upload any file directly to GitHub
- 📦 **Smart ZIP Extraction** - Auto-extract ZIP files with subfolder preservation
- 👥 **Multi-User System** - Manage multiple users with admin controls
- 🎯 **Real-Time Push** - Instant GitHub repository updates
- 🔐 **Secure Access** - User authentication and permissions
- 🎨 **Colorful Interface** - Beautiful terminal output with animations
- ⚡ **Fast & Efficient** - Quick uploads with progress tracking

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/depannn11/pushgit.git
cd pushgit
pip install -r requirements.txt
```

2. Run the Bot

```bash
python3 script.py
```

3. First-Time Setup

1. Enter your Telegram Bot Token
2. Enter your Telegram ID as admin
3. Configure GitHub via /setconfig command

🔧 Configuration

Environment Setup

```bash
# Create config file automatically on first run
# Or manually edit config.json
```

Bot Commands

```
/start       - Start the bot
/setconfig   - Setup GitHub credentials (Admin only)
/list        - List repository files
/users       - Manage allowed users (Admin only)
/adduser     - Add new user (Admin only)
/removeuser  - Remove user (Admin only)
/help        - Show help message
```

📦 Usage Examples

Upload Single File

```
User: [Sends any file]
Bot: ✓ File uploaded to GitHub!
```

Upload ZIP Archive

```
User: [Sends ZIP file]
Bot: ⚡ Extracting 15 files...
Bot: 📤 Uploading to GitHub...
Bot: ✅ All files uploaded successfully!
```

Manage Repository

```
User: /list
Bot: 📁 Repository Contents:
     📄 index.js (25.4 KB)
     📁 src/
     📄 README.md (2.1 KB)
```

🎯 Advanced Features

Auto Folder Creation

Bot automatically creates folders based on ZIP structure.

File Conflict Resolution

Existing files are updated instead of duplicated.

Progress Tracking

Real-time upload progress with file counters.

Error Handling

Comprehensive error messages with recovery suggestions.

⚙️ Technical Details

Dependencies

```txt
requests==2.31.0
pyTelegramBotAPI==4.21.1
colorama==0.4.6
```

Project Structure

```
pushgit/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── config.json        # Configuration file
├── README.md         # This file
└── assets/           # Additional resources
```

🔐 Security

· User authentication via Telegram ID
· Admin-only configuration commands
· Encrypted GitHub token storage
· Permission-based file access

🐛 Troubleshooting

Common Issues

```bash
# Bot not starting
python3 -c "import requests; print('Checking internet...')"

# Upload failures
- Verify GitHub token has 'repo' scope
- Check repository exists and is accessible
- Ensure file size is within limits

# ZIP extraction problems
- Confirm ZIP file is not corrupted
- Check available disk space
```

Debug Mode

```python
# Add debug=True to see detailed logs
bot.run_polling(debug=True)
```

📊 Performance

· Supports files up to 50MB (Telegram limit)
· Concurrent upload processing
· Memory-efficient ZIP handling
· Automatic retry on failures

🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

Code Style

· Follow PEP 8 guidelines
· Add comments for complex logic
· Include error handling
· Test before submitting

📄 License

MIT License - See LICENSE for details.

🌟 Show Your Support

Give a ⭐️ if this project helped you!

👥 Community

· Author: [https://t.me/depstore11](depann)
· Repository: depannn11/pushgit
· Issues: Report Bugs
· Discussions: Share Ideas

🚨 Disclaimer

This bot is for educational purposes. Users are responsible for complying with:

· Telegram's Terms of Service
· GitHub's API usage policies
· Copyright and licensing laws

---

<p align="center">
  <b>Made with ❤️ by depannn11</b><br>
  <i>Simplifying GitHub uploads through Telegram</i>
</p>

<div align="center">

```ascii
  ╔══════════════════════════════════════╗
  ║       GITHUB UPLOAD BOT v2.0                ║
  ║                                             ║
  ╚══════════════════════════════════════╝
```

https://user-images.githubusercontent.com/placeholder/anim.gif

</div>
```

🎬 Terminal Animation Preview

When running the bot, you'll see:

```
╔══════════════════════════════════════╗
║       GITHUB UPLOAD BOT v2.0         ║
║                                      ║
╚══════════════════════════════════════╝

🎯 Loading modules...        [✓]
🔗 Testing connections...    [✓]
🤖 Bot initializing...      [✓]
⚡ Ready to upload!          [✓]

📤 Uploading: script.py      ████████████████████ 100%
📁 Creating folder: assets   ████████████ 75%
🔄 Processing files...       ████████████████████ 100%

✅ Operation completed successfully!
```

This README includes:

1. Complete English documentation
2. Owner info: [https://t.me/depstore11](Telegram), [https://github.com/depannn11](GitHub)
3. Repository: pushgit
4. ASCII art animations
5. Badges and visual elements
6. Terminal animation preview
7. All features clearly explained
