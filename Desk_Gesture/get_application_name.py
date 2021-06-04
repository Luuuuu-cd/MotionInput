# https://stackoverflow.com/questions/14394513/win32gui-get-the-current-active-application-name

import wmi
import win32gui

c = wmi.WMI()

def get_application_name():
    windows_tile = ""; 
    while ( True ) :
        if win32gui.GetForegroundWindow() == 327778:
            return 'Desktop'
        else:
            new_window_tile = win32gui.GetWindowText(win32gui.GetForegroundWindow()); 
            if(new_window_tile != windows_tile):
                windows_tile = new_window_tile
                return windows_tile
