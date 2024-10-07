
# BG Server Freez

This code was in Python to attack DDos on BGMI server to freeze it.

## Codespace Setup
Create Codespace with 4-core else it will not work.


## Installation

Before installation of install.sh change this line in install.sh to your own repositories

```bash
postStartCommand": "python3 /workspaces/<YourRepo>/BGS.py",
```
You have to change only `<YourRepo>` to own repo.

Then Install install.sh and rebuild your codespase

```bash
chmod +x *
./install.sh
```
After rebuild run this commands

```bash
pip install pymongo aiohttp
pip install telebot
pip install flask
pip install aiogram
pip install python-telegram-bot
chmod +x *
```

## Authors

- [@ayush0662](https://www.github.com/ayush0662)


## Support

For support, email ayush.ranjan0662@gmail.com or join our Telegram channel.

[![telegram](https://img.shields.io/badge/telegram-1DA1F2?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.com/)

