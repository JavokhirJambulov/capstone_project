# We used the telepot library to send messages via Telegram bot
import datetime
import telepot

bot = telepot.Bot('5781518019:AAFo3Q4haFUGHiGGHkl-uL0M85EVWY86Gss')



# Function to send message
def send_message(msg):
    bot.sendMessage(-4224436966, msg)

# Function to send message with some text
def send_attendance(lp_number):
    msg = "Vehicle: " + lp_number + " has arrived. ("+ datetime.datetime.now().strftime("%H:%M:%S")+ ")"
    send_message(msg)