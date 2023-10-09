# Prometheuzdy-bot
Khun thong oppenheimmer style 🕶️
This is a simple Discord bot template written in Python using the Discord.py 2.0 library. 


## Prerequisites

Before you can run this bot, make sure you have the following installed:

- Python 3.6 or higher
- pip (Python package manager)

## Getting Started

1. Clone or download this repository to your local machine.

2. Create a new Discord application and bot account on the [Discord Developer Portal](https://discord.com/developers/applications).

3. After creating the bot, navigate to the "Bot" section of your application and click on the "Copy" button under the "Token" section to copy your bot's token.

4. Create a file named `.env` in the project root directory.

5. In the `.env` file, define the following environment variables:
   - `TOKEN`: Your API token or secret key.
   - `CLIENT_ID` : Your discord client id.
   - `DB_HOST`: The hostname or IP address of your database server.
   - `DB_PORT` : The port of your database server. 
   - `DB_USER`: The username for connecting to the database.
   - `DB_PASS`: The password for the database user.
   - `DB_NAME`: The name of your database.

   The `.env` file should look like this:

   ```plaintext
   TOKEN=your_api_token_here
   CLIENT_ID=your_bot_client_id_here
   DB_HOST=your_database_host_here
   DB_PORT=your_database_port_here
   DB_USER=your_database_user_here
   DB_PASS=your_database_password_here
   DB_NAME=your_database_name_here
   ```

   Replace `YOUR_BOT_TOKEN_HERE` with the actual token you copied in step 3.

6. Install the required Python packages using pip. Open your terminal/command prompt and run:

   ```
   pip install -r requirements.txt
   ```

7. Once the dependencies are installed, you can run the bot by executing:

   ```
   python main.py
   ```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

