This tool listens for Crypto Fear and Greed values from the @AltcoinFGI twitter account and saves them to an API/table for later use. It will update existing coins' FGI values, or add the coins to the table if they do not already exist within.

Steps to use this tool:

1. Add your secrets/API keys/etc from Twitter API to `constants_copy.py`
2. Rename `constants_copy.py` to `constants.py`.
3. Create a hosted/accessible empty API at pythonanywhere.com
4. Add your pythonanywhere URL to the `BASE` variable on line 30 in `main.py`.
5. Navigate to the main project folder in your terminal and run the standard `python main.py` command

Enjoy!