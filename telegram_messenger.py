# We used the telepot library to send messages via Telegram bot
import datetime
import telepot

bot = telepot.Bot('5781518019:AAFo3Q4haFUGHiGGHkl-uL0M85EVWY86Gss')


# Function to send images
def send_image(image):
    bot.sendPhoto(-4236701413, photo=open(image, 'rb'), caption=datetime.datetime.now().strftime("%H:%M:%S"))
# Function to send message
def send_message(msg):
    bot.sendMessage(-4236701413, msg)

# Function to send message with some text
def send_attendance(person_name):
    msg = 'An unknown person.'
    if (person_name != 'Unknown'):
        msg = person_name + "'s attendance taken ."
    send_message(msg)