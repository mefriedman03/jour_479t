# importing the libraries we need to run this script
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# this is pulling that secret we added earlier
slack_token = os.environ.get('SLACK_API_TOKEN')

# telling slack we want to interact with it using our key
client = WebClient(token=slack_token)

# message we want to send
# swap out the brackets for your name, or change the message entirely
msg = "this is [add your name here], testing my bot!"

# this basically says, 'whenever this script runs, i want you to try to send the message above in the channel called jour479t'
try:
    response = client.chat_postMessage(
        channel="jour479t", # this is the channel the message will send to
        text=msg,
        unfurl_links=True, 
        unfurl_media=True
    )
    # if the message is sent, then print the word success!
    print("success!")
# if something wrong happens, then tell us what the error was by printing it.    
except SlackApiError as e:
    assert e.response["ok"] is False
    assert e.response["error"]
    print(f"Got an error: {e.response['error']}")

# right now, this script only happens when you run "python3 week10/slackbot.py" in your terminal.
# that's not the MOST useful when we want a message to be sent when certain conditions are met
# in your slackbot, you can have it send messages at a certain time, when a certain trigger occurs, etc. 
# play around with the different scopes you have access to in slack as well!!!
# as always, ask your llm friends for help (or ask me!) have fun :-)