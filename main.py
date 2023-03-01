import os
from numpy import extract
import requests as rq
import constants
from prettytable import PrettyTable
import tweepy as tw
import warnings
import sys
from colorama import init, Fore, Back, Style
import re

from datetime import datetime, tzinfo
from dateutil import tz
import pytz

from dash import Dash, html, dcc
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import keyboard

# auto-reset colorama styles
init(autoreset=True)

warnings.filterwarnings("ignore", category=FutureWarning)

query = 'from:AltcoinFGI -is:reply -is:retweet'

BASE = constants.base_url

# Pretty Table Config/Style
table = PrettyTable()
table.field_names = [Fore.BLUE + "TICKER" + Fore.RESET, 
                     Fore.BLUE + "FGI" + Fore.RESET, 
                     Fore.BLUE + "SENTIMENT" + Fore.RESET, 
                     Fore.BLUE + "TA" + Fore.RESET, 
                     Fore.BLUE + "TIME" + Fore.RESET]

table.vertical_char = "|"
table.horizontal_char = "="
table.junction_char = "O"
table.align[table.field_names[0]] = "l"
table.align[table.field_names[1]] = "l"
table.align[table.field_names[2]] = "l"
table.padding_width = 2
table.sortby = table.field_names[0]

print_color = Fore.RESET

# Print out styled status code with code-dependent color
def print_status_with_color(status_code):
    status_color = Fore.BLUE
    if status_code == 200 or status_code == 201:
        status_color = Fore.GREEN
    elif status_code == 404:
        status_color = Fore.RED
    elif status_code == 500 or status_code == 501 or status_code == 429:
        status_color = Fore.YELLOW
    else:
        status_color = Fore.BLUE
    print(Fore.BLUE + "STATUS CODE: " + status_color + str(status_code) + Fore.RESET + "\n")

# Print prettyTable with items recieved from API GET request
def print_coin_table():
    response = rq.get(BASE + 'coins')
    table.clear_rows()
    for i in response.json(): # Reset
        if i['fgi'] < 50:
            print_color = Fore.RED
        elif i['fgi'] == 50:
            print_color = Fore.YELLOW
        else:
            print_color = Fore.GREEN
        table.add_row([print_color + i['ticker'].split("$")[1] + Fore.RESET, 
                       print_color + str(i['fgi']) + Fore.RESET, 
                       print_color + i['sentiment'] + Fore.RESET, 
                       i['ta'], 
                       i['time']])
    print(table)    
    print_status_with_color(response.status_code)

def print_coin(tickers):
    table.clear_rows()
    if ', ' in tickers:
        tickers = tickers.split(', ')
    elif ',' in tickers and not ', ' in tickers:
        tickers = tickers.split(',')
    else:
        tickers = [tickers]
    for i in tickers:
        response = rq.get(BASE + 'coins/' + i)
        print("---> GET $" + i.upper())
        print_status_with_color(response.status_code)
        if response.status_code != 200:
            continue
        elif response.json()['fgi'] < 50:
            print_color = Fore.RED
        elif response.json()['fgi'] == 50:
            print_color = Fore.YELLOW
        else:
            print_color = Fore.GREEN
        table.add_row([print_color + response.json()['ticker'].split("$")[1] + Fore.RESET, 
                        print_color + str(response.json()['fgi']) + Fore.RESET, 
                        print_color + response.json()['sentiment'] + Fore.RESET, 
                        response.json()['ta'],
                        response.json()['time']])    
    print(table)
# Extract relevant info from tweet and send PUT with info to API
def extract_details(tweet):
    tweet_contents = tweet.text
    # get ticker from tweet
    coin = "$" + tweet_contents.split('$')[-1].split(' ')[0]
    # get FGI index value from tweet
    fgi_index_value = int(tweet_contents.split('Index is currently ')[-1].split(' ')[0])
    # get coin Sentiment text from tweet
    fgi_sen = tweet_contents.split('- ')[1].split('\n')[0]
    # get TA index value from tweet
    ta_value = tweet_contents.split('analysis index: ')[-1].split(' ')[0]
    # Create datetime object in local timezone
    tweet_timestamp_utc = tweet.created_at
    # Get local timezone
    local_zone = tz.tzlocal()
    # Convert timezone of datetime from UTC to local
    tweet_time_local = tweet_timestamp_utc.astimezone(local_zone)
    # decide time format for local_time_str
    time_format = "%m/%d/%Y %I:%M %p"
    # format local time to readable text
    local_time_str = tweet_time_local.strftime(time_format)
    # form data object out of tweet contents
    data = {"ticker": coin, "fgi": fgi_index_value, "sentiment": fgi_sen, "ta": ta_value, "time": local_time_str}
    print(Fore.BLUE + "Sending PUT with latest FGI on " + Fore.CYAN + data['ticker'] + "..." + Fore.RESET)
    # send tweet info in PUT request
    response = rq.put(BASE + "coins/" + data['ticker'].split('$')[1], data)
    # print response code
    print_status_with_color(response.status_code)

    print(Fore.CYAN + "Listening for Tweets from @AltcoinFGI...\n")

class FGIPrinter(tw.StreamingClient):

    def on_tweet(self, tweet):
        # string to check if tweet is of correct type (FGI coin update)
        validation_string = "Fear and Greed Index is currently"

        if validation_string in tweet.text:
            extract_details(tweet)
        else:
            print(Fore.RED + "Tweet did not meet validation criteria.")
            print(Fore.RED + "Better luck next time, nerd.")
            print(Fore.CYAN + "Listening for Tweets from @AltcoinFGI...\n")

    def on_errors(errors):
        for error in errors:
            print_status_with_color(error)


    def on_disconnect(self):
        print_coin_table()

if __name__ == "__main__":
    # printer.filter(tweet_fields=['author_id', 'created_at'])
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.GREEN + "Press Enter to start.")
    print(Fore.GREEN + "Type 'table' to print coin table.")
    print(Fore.GREEN + "Type ticker name without $ to print coin info (ex: 'ADA').")

    command = input()
    if command == '':
        os.system('cls' if os.name == 'nt' else 'clear')
        client = tw.Client(bearer_token=constants.bearer_token)
        response = rq.get(BASE + 'coins')
        # -- if database is empty, get recent 10 tweets --
        if len(response.json()) < 1:
            tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations', 'created_at'], max_results=10)
            for tweet in tweets.data:
                extract_details(tweet)

        print_coin_table()
        print(Fore.CYAN + "Listening for Tweets from @AltcoinFGI...\n")
        printer = FGIPrinter(constants.bearer_token, wait_on_rate_limit=True)
        if len(printer.get_rules()) < 1:
            printer.add_rules(tw.StreamRule(query))
        printer.filter(tweet_fields=['author_id', 'created_at'])
    elif command == "table":
        print_coin_table()
    else:
        print_coin(command)
    
    sys.stdout.flush()

# app = Dash(__name__)

# # assume you have a "long-form" data frame
# # see https://plotly.com/python/px-arguments/ for more options

# output = []

# df = df.reset_index()  # make sure indexes pair with number of rows

# for index, row in df.iterrows():

#     color = ""

#     if row['FGI Sentiment'] == "EXTREME FEAR":
#         color = "darkred"
#     elif row['FGI Sentiment'] == "STRONG FEAR":
#         color = "red"
#     elif row['FGI Sentiment'] == "FEAR":
#         color = "indianred"
#     elif row['FGI Sentiment'] == "MILD FEAR":
#         color = "orange"
#     elif row['FGI Sentiment'] == "NEUTRAL":
#         color = "yellow"
#     elif row['FGI Sentiment'] == "MILD GREED":
#         color = "mediumaquamarine"
#     elif row['FGI Sentiment'] == "GREED":
#         color = "green"
#     elif row['FGI Sentiment'] == "STRONG GREED":
#         color = "mediumseagreen"
#     elif row['FGI Sentiment'] == "EXTREME GREED":
#         color = "darkgreen"
#     elif row['FGI Sentiment'] == "INSANITY":
#         color = "darkgreen"



#     fig = go.Figure(go.Indicator(
#         domain = {'x': [0, 1], 'y': [0, 1]},
#         value = row['FGI Index'],
#         mode = "gauge+number",
#         title = {
#                     'text': '<b>' + row['Coin'] + '</b>',
#                     'font': {
#                         'size': 30
#                     }
#                 },
#         gauge = {'axis': {'range': [None, 100]},
#                 'bar': {'color': color}}))

#     fig.add_annotation(
#         text=row['FGI Sentiment'],
#         showarrow=False,
#         font=dict(
#             size=25
#         )
#     )

#     output.append(
#         dcc.Graph(
#             id=str(index),
#             figure=fig,
#             className="graph",
#             style = {
#                 "max-width": "100%",
#                 "height": "auto"
#             }
#         )
#     )

# app.layout = html.Div(
#     children=output,
#     className="outer-container"
# )

# if __name__ == '__main__':
#     app.run_server(debug=True)