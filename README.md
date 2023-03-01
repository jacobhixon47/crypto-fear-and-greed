### *Altcoin FGI discontinued their service and Twitter, so this project no longer works.*

*Still, it's not a bad boilerplate for scraping Twitter info into a table/API.*

This tool listens for Crypto Fear and Greed values from the @AltcoinFGI twitter account and saves them to an API/table for later use. It will update existing coins' FGI values, or add the coins to the table if they do not already exist within.

Steps to use this tool:

1. Create a hosted/accessible empty API at pythonanywhere.com
2. Add your python API URL and your secrets/API keys/etc for Twitter API to `constants_copy.py`
3. Rename `constants_copy.py` to `constants.py`.
4. Navigate to the main project folder in your terminal and run the standard `python main.py` command

Enjoy!