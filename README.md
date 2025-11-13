**Telegram Channel Listener**

# Overview
This project listens to Telegram channels using a user account and the Telethon library. It enables you to monitor messages from public and private channels you join, providing a flexible and powerful way to aggregate channel content.

## Ways to Listen to Telegram Channels
There are several ways to programmatically listen to Telegram channels:

- **Bot Account:** Limited to channels where the bot is an admin.
- **User Account (Client API):** Log in as a user and access any channel you join (most flexible).
- **Proxy/Forwarder:** Use a bot or user to forward messages from channels.
- **Telegram API (TDLib):** Advanced, official client library for full user features.

This project uses the User Account (Client API) method with Telethon, which provides the most flexibility for listening to public and private channels.

# Setup

## Set Up MongoDB (Ubuntu)

To use MongoDB for caching dialog data, you need to install and start MongoDB on your Ubuntu system:

1. **Install MongoDB:**
	```bash
	sudo apt update
	sudo apt install -y mongodb
	```

2. **Start MongoDB service:**
	```bash
	sudo systemctl start mongodb
	sudo systemctl enable mongodb
	```

3. **Verify MongoDB is running:**
	```bash
	sudo systemctl status mongodb
	```

4. **Default connection string:**
	Use `mongodb://localhost:27017` as your `MONGO_URI` in your `.env` file.

For advanced configuration or remote access, refer to the [official MongoDB documentation](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/).

## Set Up Python Virtual Environment


It is recommended to use a Python virtual environment to manage dependencies for this project.

1. Create a new virtual environment:
	```bash
	python3 -m venv .venv
	```
2. Activate the virtual environment:
	```bash
	source .venv/bin/activate
	```
3. Upgrade pip (optional but recommended):
	```bash
	pip install --upgrade pip
	```
4. Install all necessary packages:
	```bash
	pip install -r requirements.txt
	```


## Set Up Telegram App and Obtain `.session` File

To use this project, you need to create a Telegram application and generate a `.session` file for authentication.

### 1. Create a Telegram Application

1. Visit [my.telegram.org](https://my.telegram.org).
2. Log in with your Telegram account.
3. Navigate to “API development tools”.
4. Create a new application to obtain your `api_id` and `api_hash`.
5. Create your own `.env` file from the provided `.env.example` and set your API credentials and configuration in `.env`.
6. Set your phone number (`PHONE`) and session name (`SESSION_NAME`) in `.env` as well.

### 2. Generate Your `.session` File

Run the provided script to generate your `.session` file:

```bash
python -m tools.generate_session.py
```

You will be prompted to enter your API ID, API Hash, and phone number. Then, enter the code sent to your Telegram app. After successful login, a `.session` file will be created in your working directory.


# Tools

## List Dialogs Tool

This tool lists all dialogs (private chats, groups, channels) your Telegram account can access, and caches them in MongoDB.

### Usage

1. **Configure MongoDB connection string in `.env`:**
	Add the following line to your `.env` file (use your own connection string if needed):
	```
	MONGO_URI=mongodb://localhost:27017
	```

2. **Run the tool:**
	```bash
	python -m tools.list_dialogs
	```

3. **Force update from Telegram (ignore cache):**
	```bash
	python -m tools.list_dialogs --update
	```

If you do not use the `--update` flag, the tool will load dialogs from the MongoDB cache if available. If the cache is empty or you use `--update`, it will fetch dialogs from Telegram and update the cache.


# Telethon Entities Overview

This section provides an overview of key entities in Telethon.

## Dialog

In Telethon, a **Dialog** represents a conversation or chat thread. It can be:
	- A private chat with a user
	- A group chat
	- A channel