**Telegram Channel Listener**

- [Overview](#overview)
	- [Ways to Listen to Telegram Channels](#ways-to-listen-to-telegram-channels)
	- [Infrastructure](#infrastructure)
- [Setup](#setup)
	- [Set Up MongoDB](#set-up-mongodb)
		- [Set Up MongoDB in Extension Storage](#set-up-mongodb-in-extension-storage)
	- [Set Up Python Virtual Environment](#set-up-python-virtual-environment)
	- [Set Up Telegram App and Obtain `.session` File](#set-up-telegram-app-and-obtain-session-file)
		- [1. Create a Telegram Application](#1-create-a-telegram-application)
		- [2. Generate Your `.session` File](#2-generate-your-session-file)
- [Tools](#tools)
	- [List Dialogs Tool](#list-dialogs-tool)
		- [Usage](#usage)
- [Telethon](#telethon)
	- [Dialogs](#dialogs)


# Overview
This project listens to Telegram using a user account and the Telethon library. It enables you to monitor messages from groups and channels you join, providing a flexible and powerful way to aggregate channel content.


## Ways to Listen to Telegram Channels
There are several ways to programmatically listen to Telegram channels:

- **Bot Account:** Limited to channels where the bot is an admin.
- **User Account (Client API):** Log in as a user and access any channel you join (most flexible).
- **Proxy/Forwarder:** Use a bot or user to forward messages from channels.
- **Telegram API (TDLib):** Advanced, official client library for full user features.

This project uses the User Account (Client API) method with Telethon, which provides the most flexibility for listening to public and private channels.


## Infrastructure

The project is designed to run on a dedicated server with the following setup:

1. Ubuntu Desktop: This is where the project deployed. **the login user is presumed to be `saguette`**.
2. Storage: A SeaGate HDD is connected as extension storage to the Ubuntu Desktop, mounted at `/media/saguette/Expansion`.
3. Project Location: The project files are located at `/media/saguette/Expansion/cunhua/telegram`.
4. Environments: Two environments are set up for development and production: `dev` and `prod`.
5. Network Topology: The server (Ubuntu Desktop) is connected to a Wi-Fi router, sharing the local network with a MacBook (macOS). The MacBook can SSH into the Ubuntu desktop using the local IP address (**The server's IP address on this network is presumed to be `192.168.2.1`**). This setup will be referenced in subsequent instructions for remote access and integration.
6. Database Authentication: **The password for MongoDB users is set to `1234567890` in this documentation**.

```
└── /media/saguette/Expansion/cunhua/telegram/
    ├── dev/
    │   ├── mongodb/
    │   |   ├── data/
    │   |   ├── mongod.conf
    │   |   └── mongod.log
	|	|
	|	└── telegram_downloads/
    │       ├── <channel_1>
    │       ├── <channel_2>
	│       ├── <group_1>
    │       └── others
	|   
    └── prod
```
- The `prod` environment mirrors the structure of `dev`, ensuring consistency across both setups.


# Setup

## Set Up MongoDB

To set up MongoDB on Ubuntu, follow the [official MongoDB installation guide](https://www.mongodb.com/docs/manual/administration/install-community/?operating-system=linux&linux-distribution=ubuntu&linux-package=default&search-linux=with-search-linux) and [official MongoDB Compass installation guide](https://www.mongodb.com/docs/compass/install/?operating-system=linux&package-type=.deb)

After installation, ensure MongoDB is running and accessible. Use `mongodb://localhost:27017` as your default connection string in the `.env` file.

### Set Up MongoDB in Extension Storage

This project will access Telegram channels and groups to download media files. Given the large volume of pictures and videos expected, it's advisable to store all data on the external SeaGate HDD for adequate storage capacity.

**Note**: Steps 1-8 set up a standalone MongoDB instance with authentication and remote access. Steps 9-12 are optional and only needed if you want to configure MongoDB as a replica set for high availability and data redundancy.

After completing the setup, update your MongoDB connection string in the `.env` file.

**1. Create the Configuration File**

Create a file named `mongod.conf` in the following path: `/media/saguette/Expansion/cunhua/telegram/dev/mongodb/mongod.conf`.

```yaml
# mongod.conf

# Where and how to store data.
storage:
  dbPath: /media/saguette/Expansion/cunhua/telegram/dev/mongodb/data
#  engine:
#  wiredTiger:

# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /media/saguette/Expansion/cunhua/telegram/dev/mongodb/mongodb.log

# network interfaces
net:
  port: 27001
  bindIp: 127.0.0.1,192.168.2.1


# how the process runs
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
```


**Note:**
`192.168.2.1` is the Ubuntu laptop's IP for remote access; `127.0.0.1` is for local requests. Set both in `bindIp` so MongoDB listens internally and externally. This config controls which network interfaces MongoDB accepts connections from—not which clients are allowed (that’s managed by firewalls or ACLs).
   
**Network Request Flow (MacBook → Ubuntu Desktop):**
1. MongoDB Compass on your MacBook connects to `192.168.2.1:27001`.
2. The request travels through your local network (Wi-Fi/Ethernet).
3. The Ubuntu machine receives the request on its network interface.
4. `mongod` accepts and processes the connection on `192.168.2.1:27001`.


**2. Create the Storage Directory**

```shell
mkdir -p /media/saguette/Expansion/cunhua/telegram/dev/mongodb/data
```


**3. Start MongoDB**

Run MongoDB with the custom configuration file:

```shell
mongod --config /media/saguette/Expansion/cunhua/telegram/dev/mongodb/mongod.conf --fork
```

To debug:

```shell
mongod --config /media/saguette/Expansion/cunhua/telegram/dev/mongodb/mongod.conf
```

or

```shell
tail -n 50 /media/saguette/Expansion/cunhua/telegram/dev/mongodb/mongod.log
```


**4. Verify Running Instance**


Check MongoDB's status:

```shell
sudo lsof -iTCP -sTCP:LISTEN -P | grep mongod
```

Example output:

```shell 
mongod  235771  saguette  15u  IPv4  2249267  0t0  TCP  localhost:27001 (LISTEN)
mongod  235771  saguette  16u  IPv4  2249268  0t0  TCP  saguette:27001 (LISTEN)
```
**Note**: The output shows that the MongoDB process is run by the user because you started the mongod command from your terminal.


**5. Test Remote Connectivity (Optional)**

From your MacBook, verify connectivity:

```shell
telnet 192.168.2.1 27001
```

**6. Create Authenticated Users**

Create secure users for your MongoDB instance:
1. Access the MongoDB shell:
	```shell
	mongosh --port 27001
	```
2. Add Users with appropriate roles:
	```shell
	test> use admin
	switched to db admin
	admin> db.createUser({user: "admin", pwd: "1234567890", roles: [ { role: "root", db: "admin" } ]})
	{ ok: 1 }
	admin> db.createUser({ user: "cunhua", pwd: "1234567890", roles: [ { role: "userAdminAnyDatabase", db: "admin" }, { role: "readAnyDatabase", db: "admin" }, { role: "readWrite", db: "telegram" }, { role: "readWrite", db: "telegram_backup" } ]})
	{ ok: 1 }
	```
3. Log in using the new credentials:
	```shell
	mongosh --port 27001 -u cunhua -p 1234567890 --authenticationDatabase admin
	```
4. Update User:
	```shell
	test> use admin

	admin> db.updateUser("cunhua", {
	roles: [
		{ role: "userAdminAnyDatabase", db: "admin" },
		{ role: "readAnyDatabase", db: "admin" },
		{ role: "readWrite", db: "telegram" },
		{ role: "readWrite", db: "telegram_backup" },
		{ role: "readWrite", db: "telegram_archive" }
	]
	})
	```
	or
	```shell
	test> use admin

	admin> db.grantRolesToUser("cunhua", [
	{ role: "readWrite", db: "telegram_archive" }
	])
	```


**7. Connect via MongoDB Compass**

Use the following URI to connect from your MacBook:

```shell
mongodb://cunhua:1234567890@192.168.2.1:27001/?authSource=admin
```

**8. Stop MongoDB Before Setting up the Replica Set**

Terminate MongoDB using its PID:

```shell
sudo kill <PID>
```

**9. (Replica Set Only) Create a Keyfile for the Replica Set**

1. Generate a keyfile:
   	```bash
   	openssl rand -base64 756 > keyfile-mongodb-cunhua-telegram-dev
   	```
   	**Note**: Creating the keyfile on an external portable disk may cause issues. To avoid this, place the file in a directory under your root file system (e.g., `/home/saguette/keyfile-mongodb-cunhua-telegram-dev`).

2. Set appropriate permissions and ownership:
   	```bash
   	sudo chmod 600 keyfile-mongodb-cunhua-telegram-dev
   	sudo chown cunhua:cunhua keyfile-mongodb-cunhua-telegram-dev
   	```
   	**Note**: Ensure the ownership of the keyfile matches the user running the `mongod` process. In this case, `cunhua` should be the process owner.


**10. (Replica Set Only) Update the Configuration File**


Update your `mongod.conf` with the following settings:

```yaml
# security
security:
  authorization: enabled
  keyFile: /home/saguette/keyfile-mongodb-cunhua-telegram-dev

replication:
  replSetName: "rs0"
```

Restart MongoDB to apply changes and debug using:

```bash
tail -n 50 /media/saguette/Expansion/cunhua/cunhua_mongodb.log
```

**11. (Replica Set Only) Start Replica Set**

1. Log in as the admin user:
   	```shell
   	mongosh --port 27001 -u admin -p 1234567890 --authenticationDatabase admin
   	```
2. Initialize the replica set:
   	```shell
   	rs.initiate()
   	rs.status()
   	```
   
**12. (Replica Set Only) Restart Replica Set**

The replica set needs to be restarted if there is a network connection interruption due to an IP address change (for example, the IP address changes from `192.168.2.1` to `192.168.2.60`).

**Note**: When we first initiated the replica set, the laptop was assigned the IP address `192.168.2.1`. MongoDB stores the replica set configuration, including the host's IP address, in its internal metadata located within the data directory (`/media/saguette/Expansion/cunhua/telegram/dev/mongodb/data`). However, when the IP address changes, the replica set continues to use the old IP address (`192.168.2.1`) because the replica set configuration stored within MongoDB's internal metadata still references that original address. Simply updating the `mongod.conf` file changes how MongoDB binds to network interfaces, but it does **not** automatically update the replica set's member information. The replica set configuration must be explicitly updated within MongoDB to reflect the new IP address for the changes to take effect.

1. Update the `mongod.conf` File for `bindIp`.
2. Restart the `mongod` Service.
3. Log in as the `admin` User via `mongosh`.
4. Attempt to Re-initialize the Replica Set.
   1. At this point, running `rs.initiate()` will likely result in an error because the replica set has already been initialized with the old IP address.
   ```shell
   rs.initiate()
   ```
   Error Message:
   ```text
   MongoServerError[AlreadyInitialized]: already initialized
   ```
   Additionally, running `rs.status()` will display:
   ```text
   MongoServerError[InvalidReplicaSetConfig]: Our replica set config is invalid or we are not a member of it
   ```
5. Check the Current Replica Set Configuration:
   Run `rs.conf()` to view the current configuration and identify discrepancies between the Ubuntu laptop's current IP address and the replica set configuration.
6. Execute the following commands in `mongosh` to update the `host` field and apply the new configuration.
	```shell
	var config = rs.conf();
	printjson(config);
	
	config.members[0].host = '192.168.2.60:27000';
	
	config.version += 1;
	
	rs.reconfig(config, { force: true });
	
	rs.status();
	```



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

1. **Activate your Python virtual environment and install all packages:**
	```bash
	source .venv/bin/activate
	pip install -r requirements.txt
	```

2. **Configure MongoDB connection string in `.env`:**
	Add the following line to your `.env` file (use your own connection string if needed):
	```
	MONGO_URI=mongodb://localhost:27017
	```

3. **Run the tool:**
	```bash
	python -m tools.list_dialogs
	```

4. **Force update from Telegram (ignore cache):**
	```bash
	python -m tools.list_dialogs --update
	```

If you do not use the `--update` flag, the tool will load dialogs from the MongoDB cache if available. If the cache is empty or you use `--update`, it will fetch dialogs from Telegram and update the cache.


# Telethon

This section provides an overview of key entities in Telethon.

## Dialogs

In Telethon, a Dialog represents a conversation or chat thread. It can be:
- **Private Chat**: One-to-one conversation with a single user.
- **Chat**: Old-style “basic group” (up to 200 members) where all members can send messages.
- **Channel with `entity.megagroup == True`**: A supergroup, i.e. a large group chat where all members can send messages.
- **Channel with `entity.megagroup == False`**: A broadcast channel, where only admins/owners can post messages and other users are subscribers.

My code in `tgtypes/dialog.py` classifies them slightly differently:

| Telethon types        | My code classifies as | Reason                                                                                  |
|-----------------------|-----------------------|-----------------------------------------------------------------------------------------|
| Private Chat          | Private Chat          | One-to-one dialog with a single user.                                                  |
| Chat                  | Group                 | Legacy/basic group where multiple members can talk.    |
| megagroup Channel     | Group                 | Supergroups where multiple members can talk.  |
| non-megagroup Channel | Channel               | These are true broadcast channels, so they stay in their own “Channel” category.       |