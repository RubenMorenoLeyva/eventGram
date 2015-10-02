__author__ = 'Malaga-talentum'

import telebot
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import csv
#path watchdog (csv file)
path=''

#put your token api bot
bot = telebot.TeleBot(token="")
list_tags = ['concert','theatre','football','basketball','science','exposition','conference','fair','circus']

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        #path watchdog (csv file)
        if event.src_path == '':
            list_news = send_event()
            conn = sqlite3.connect("eventgram.db")
            cursor = conn.cursor()

            changes = cursor.execute("SELECT user_id FROM tags WHERE name=? and location=?",(list_news[0],list_news[1]))
            for id in changes:
                message = "There is a new event: "+ list_news[2]+ ".The event match your tag: " + list_news[0]+", "+list_news[1] +"."
                bot.send_message(int(id[0]), message)
            conn.close()


event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path=path, recursive=False)
observer.start()


def send_event():
    #path where is csv file that contains events
    with open("") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            last_line = (row['tag'], row['location'],row['title'])
    csvfile.close()
    return last_line

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    mess = "Welcome to EventGram!\nThe commands for user are:\n/subscribe tag location\n/unsubscribe tag location\nThe command for group is:\n/addfriends tag location link"
    bot.reply_to(message, mess)


@bot.message_handler(commands=['subscribe'])
def subscribe_tag(message):
    chat_id = message.chat.id
    if chat_id > 0:
        list = message.text.split()
        if len(list) == 3:
            tag = list[1]
            location = list[2]
            if list_tags.__contains__(tag):
                conn = sqlite3.connect("eventgram.db")
                c = conn.cursor()
                c.execute("INSERT INTO tags (user_id, name, location) values (?,?,?)", (chat_id, tag,location))
                conn.commit()
                bot.reply_to(message,"Tag added")
                conn.close()
            else:
                bot.reply_to(message, "Introduce a valid tag. Here are the valid tags: %s"%list_tags)
        else:
            bot.reply_to(message, "Invalid command. Example: /subscribe theatre madrid")
    else:
        bot.reply_to(message, "Groups cannot subscribe to events")

@bot.message_handler(commands=['addfriends'])
def addfriends_group(message):
    chat_id = message.chat.id
    if chat_id < 0:
        list = message.text.split()
        if len(list) == 4:
            tag = list[1]
            location = list[2]
            link = list[3]

            if list_tags.__contains__(tag):
                conn = sqlite3.connect("eventgram.db")
                cursor = conn.cursor()
                result = cursor.execute("SELECT user_id FROM tags WHERE name=? and location=?",(tag,location))
                for r in result:
                    mess = "You have been invited to the group " + message.chat.title + ". The tags are " + tag + ", " + location + ". Enjoy your new group!\n" + link
                    bot.send_message(int(r[0]),mess)
                conn.close()
            else:
                bot.reply_to(message, "Introduce tag correcto: %s"%list_tags)
        else:
            bot.reply_to(message, "Invalid command. Example: /addfriends theatre madrid link")
    else:
        bot.reply_to(message, "Users cannot add friends. Create a group to add other people.")

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_tag(message):
    chat_id = message.chat.id
    if chat_id > 0:
        list = message.text.split()
        if len(list) == 3:
            tag = list[1]
            location = list[2]
            if list_tags.__contains__(tag):
                conn = sqlite3.connect("eventgram.db")
                c = conn.cursor()
                c.execute("DELETE FROM tags where user_id=? and name=? and location=?", (chat_id, tag, location,))
                conn.commit()
                bot.reply_to(message,"Tag removed")
                conn.close()
            else:
                bot.reply_to(message, "Introduce a valid tag. Here are the valid tags: %s"%list_tags)
        else:
            bot.reply_to(message, "Invalid command. Example: /unsubscribe theatre madrid")
    else:
        bot.reply_to(message, "Groups cannot unsubscribe to events")

bot.polling()

