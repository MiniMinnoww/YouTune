# import os
# import socks
# import argparse
# import googleapiclient
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# import pytube
# import mp4Convert
# from mutagen.mp3 import MP3
# from time import sleep
# from shutil import copy
# import sys

import csv
import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.colorchooser as color
import tkinter.messagebox as box
import urllib.request
import urllib.error
from io import BytesIO
from threading import Thread
import random
import pytube
from PIL import Image, ImageTk
from pygame import mixer as mx
import downloads
from prints import *

# TODO: Add favourites playlist
# TODO: Add a way to play all songs


def create_file(path):
    with open(path, "w") as f:
        f.close()


def multiply_image_size(img: Image, multiply: float):
    return img.resize((int(img.size[0] * multiply), int(img.size[1] * multiply)), 0)


def do_popup(event):
    p = event.widget
    m = tk.Menu(p, tearoff=0)
    m.add_command(label="Random Song", command=a.randomSong)
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()


def sort_listbox(box: tk.Listbox):
    items = sorted(box.get(0, tk.END))
    box.delete(0, tk.END)
    for item in items:
        box.insert(tk.END, item)


class MainWindow:
    def __init__(self):
        mx.init()
        self.root = tk.Tk()
        self.device = "computer"
        self.root.update()

        self._init_vars()  # Variables to use
        self._init_root()  # Root window (includes images to avoid 'To early to create image' error)

        # Create download folder and info.csv if they don't exist
        if not os.path.exists(os.getcwd() + "\\downloads"): os.mkdir(os.getcwd() + "\\downloads")
        if not os.path.exists(os.getcwd() + "\\downloads\\info.csv"): create_file(os.getcwd() + "\\downloads\\info.csv")
        for item in os.listdir(os.getcwd() + "\\downloads"):
            if os.path.splitext(item)[1] == ".mp4":
                os.remove(os.getcwd() + "\\downloads\\" + item)

        self._init_title()  # Title bar
        self._init_soundbar()  # Sound bar
        self._init_song_area()  # Song list display

        # Update music and debug 'Initialised'
        self.reloadCurrentMusic()
        printc("Initialised", PrintColors.GREEN)

    def _init_root(self):
        # Define root and other variables
        self.logo = tk.PhotoImage(file="Logo.png")
        self.play_image = tk.PhotoImage(file="play.png")
        self.pause_image = tk.PhotoImage(file="pause.png")
        self.skip_image = tk.PhotoImage(file="skip.png")
        self.back_image = tk.PhotoImage(file="back.png")

        # Configure root to fit needs
        self.root.state("zoomed")
        self.root.title("YouTune")
        self.root.configure(background=self.BG)
        self.root.bind("<F11>", self.toggle_fullscreen)
        ICON = tk.PhotoImage(file="SmallLogo.png")
        self.root.wm_iconphoto(False, ICON)

    def _init_vars(self):
        self.BG = '#212121'  # X11 color: 'gray85'
        self.FG = '#FFFFFF'  # X11 color: 'black'
        self.currentSongs = {}
        self.currentSong = ""
        self.songChange = False
        self.playing = False
        self.my_songs = {}
        self.skipSong = False
        self.scrollBarUpdate = True
        self.collapsed = False
        self.songsInfo = []
        self.results = []
        self.resultImages = []

    def _init_title(self):
        self.title_bar = tk.Frame(self.root)
        self.title_bar.place(relx=0.15, rely=0.01, relheight=0.157, relwidth=0.998)
        title = tk.Label(self.title_bar, image=self.logo, bg=self.BG)
        self.title_bar.configure(relief='groove')
        self.title_bar.configure(borderwidth=0)
        self.title_bar.configure(highlightthickness=0)
        self.title_bar.configure(relief="groove")
        self.title_bar.configure(bg=self.BG)
        title.pack()
        title.photo = self.logo

    def _init_soundbar(self):
        # Create soundbar frame
        self.soundbarFrame = tk.Frame(self.root)
        self.soundbarFrame.place(relx=0.31, rely=0.94, relheight=0.06, relwidth=0.69)
        self.soundbarFrame.configure(relief='groove')
        self.soundbarFrame.configure(relief="groove")
        self.soundbarFrame.configure(borderwidth=0)
        self.soundbarFrame.configure(highlightthickness=0)
        self.soundbarFrame.configure(background=self.BG)

        # Play pause button for soundbar frame
        self.play_pause_button = tk.Button(self.soundbarFrame, image=self.play_image, command=self.play_pause,
                                           bg=self.BG, relief=tk.FLAT)
        self.play_pause_button.photo = self.play_image
        self.play_pause_button.bind("<Button-3>", do_popup)

        self.skip_button = tk.Button(self.soundbarFrame, image=self.skip_image, command=None, bg=self.BG,
                                     relief=tk.FLAT)

        self.back_button = tk.Button(self.soundbarFrame, image=self.back_image, command=self.resetSong, bg=self.BG,
                                     relief=tk.FLAT)

        self.songImageDisplay = tk.Label(self.root, bg=self.BG, text="", relief=tk.FLAT)
        self.currentSongLabel = tk.Label(self.root, image=None, bg=self.BG, fg=self.FG, font="Veranda 15")

        self.soundbarFrame.place(relx=0.31, rely=0.94, relheight=0.06, relwidth=0.69)
        self.currentSongLabel.place(x=1010, y=783)
        self.play_pause_button.place(relx=0.5, rely=0.1)
        self.songImageDisplay.place(relx=0.45, rely=0.3)
        self.skip_button.place(relx=0.7, rely=0.15)
        self.back_button.place(relx=0.3, rely=0.15)

    def _init_song_area(self):
        # Create frame which displays songs
        self.songsFrame = tk.Frame(self.root)

        self.songsFrame.configure(relief="groove")
        self.songsFrame.configure(borderwidth=0)
        self.songsFrame.configure(highlightthickness=0)
        self.songsFrame.configure(background=self.BG)

        self.songsTitle = tk.Label(self.songsFrame)

        self.songsTitle.configure(text="Songs")
        self.songsTitle.configure(font="Verdana 15 underline")
        self.songsTitle.configure(bg=self.BG)
        self.songsTitle.configure(fg=self.FG)

        self.collapseSongsButton = tk.Button(self.songsFrame, text="|", command=self.collapseSongArea, bg=self.BG,
                                             fg=self.FG, relief=tk.FLAT)

        # Listbox for downloaded songs
        self.song_listbox = tk.Listbox(self.songsFrame, width=65, height=45)

        self.song_listbox.configure(bg=self.BG)
        self.song_listbox.configure(fg=self.FG)
        self.song_listbox.configure(activestyle="dotbox")
        self.song_listbox.configure(borderwidth=0)
        self.song_listbox.configure(highlightthickness=0)
        self.song_listbox.bind("<<ListboxSelect>>", self.updateSongInfo)

        self.browse_button = tk.Button(self.songsFrame, command=self.openDownloadWindow, text="Browse Songs",
                                       bg=self.BG, fg=self.FG)

        self.delete_button = tk.Button(self.songsFrame, command=self.deleteSelectedSong, text="Delete Song", bg=self.BG,
                                       fg=self.FG)

        separator = ttk.Separator(self.songsFrame, orient=tk.VERTICAL)
        self.search_bar = tk.Entry(self.songsFrame, text="Search", fg=self.FG, bg=self.BG)
        self.search_bar.bind("<Key>", self.search_for_songs)

        self.songsFrame.place(relx=0.0, rely=0.0, relheight=1, relwidth=0.27)
        self.songsTitle.pack()
        self.song_listbox.pack()
        self.delete_button.place(relx=0.5, rely=0.97, relwidth=0.49)
        self.search_bar.place(relx=0, rely=0.940, relwidth=0.99, height=25)
        self.collapseSongsButton.place(relx=0.97, rely=0, relheight=1)

        self.browse_button.place(relx=0, rely=0.97, relwidth=0.5)
        # noinspection PyUnboundLocalVariable
        separator.place(relx=0.997, rely=0.0, relheight=1)

    def getSongs(self, song=None):
        if song is None:
            dow = downloads.youtubeSearch()
            res = dow.search(self.downloadSearchBar.get())
            self.results = []
            for result in res:
                print("http://www.youtube.com/watch?v=" + result)
                vid = pytube.YouTube("http://www.youtube.com/watch?v=" + result)
                print(vid)
                self.results.append(vid.title)
                self.currentSongs[vid.title] = result
                self.resultImages.append(vid.thumbnail_url)
            self.selectSongToDownload()
        else:
            dow = downloads.youtubeSearch()
            res = dow.search(song)
            result = res[0]
            return result

    def download(self, song=None):
        to_download = song
        self.downloadButton.destroy()
        downloadingLabel = tk.Label(self.downloadWindow2, text="Downloading...", fg=self.FG, bg=self.BG)
        downloadingLabel.pack()
        self.downloadWindow2.update()

        downloads.download(self.currentSongs[to_download])
        printc("Downloaded", PrintColors.GREEN)
        self.reloadCurrentMusic()
        self.downloadWindow2.destroy()

    def deleteSelectedSong(self):
        song = os.getcwd() + "\\downloads\\" + self.song_listbox.selection_get() + ".mp3"
        a = box.askyesno("Are you sure?",
                         f"Are you sure you want to delete the \nsong: '{self.song_listbox.selection_get()}'?",
                         parent=self.root)
        if a:
            try:
                os.remove(song)
            except PermissionError:
                mx.stop()
                mx.music.unload()
                os.remove(song)
        self.reloadCurrentMusic()

    def reloadCurrentMusic(self, _=None):
        self.song_listbox.delete(0, tk.END)
        self.my_songs = {}
        for song in os.listdir(os.getcwd() + "\\downloads"):
            if song != "info.csv":
                self.song_listbox.insert(tk.END, os.path.splitext(song)[0])
                self.my_songs[os.path.splitext(song)[0]] = os.getcwd() + "\\downloads\\" + song
        sort_listbox(self.song_listbox)

        self.songsInfo = list(csv.reader(open(os.getcwd() + "\\downloads\\info.csv")))

    def play_pause(self, _=None, playFrom=0, overrideSong=False):
        if len(self.song_listbox.curselection()) != 0:
            try:
                if overrideSong: self.currentSong = ""
                if self.song_listbox.selection_get() == self.currentSong:
                    self.playing = not self.playing
                    if self.playing:
                        mx.music.unpause()
                        printc("Unpaused", PrintColors.ORANGE)
                        self.play_pause_button.configure(image=self.pause_image)
                        self.play_pause_button.photo = self.pause_image
                    else:
                        mx.music.pause()
                        printc("Paused", PrintColors.RED)
                        self.play_pause_button.configure(image=self.play_image)
                        self.play_pause_button.photo = self.play_image
                else:  # If song is switched
                    self.songChange = True
                    mx.music.load(self.my_songs[self.song_listbox.selection_get()])
                    self.currentSong = self.song_listbox.selection_get()
                    mx.music.play(start=playFrom)
                    self.playing = True
                    printc("Playing", PrintColors.GREEN)
                    self.play_pause_button.configure(image=self.pause_image)
                    self.play_pause_button.photo = self.pause_image
                    self.songChange = False
            except:
                self.songChange = True
                mx.music.load(self.my_songs[self.song_listbox.selection_get()])
                self.currentSong = self.song_listbox.selection_get()
                mx.music.play(start=playFrom)
                self.playing = True
                printc("Playing", PrintColors.GREEN)
                self.play_pause_button.configure(image=self.pause_image)
                self.play_pause_button.photo = self.pause_image
                self.songChange = False

    def randomSong(self):
        songs = [self.song_listbox.get(0, tk.END)]
        print(songs)
        choice = random.choice(songs[0])
        index = self.song_listbox.get(0, "end").index(choice)
        self.song_listbox.select_set(index)
        self.updateSongInfo()
        self.play_pause()

    def toggle_fullscreen(self, _):
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
        else:
            self.root.attributes('-fullscreen', True)

    def openDownloadWindow(self):
        # Create TopLevel from which the user can download songs
        self.downloadWindow = tk.Toplevel(self.root)
        self.downloadWindow.title("Download Song")
        self.downloadWindow.resizable(0, 0)
        self.downloadWindow.geometry("330x550")
        self.downloadWindow.configure(relief='groove')
        self.downloadWindow.configure(borderwidth="2")
        self.downloadWindow.configure(relief="groove")
        self.downloadWindow.configure(background=self.BG)
        ICON = tk.PhotoImage(file="SmallLogo.png")
        self.downloadWindow.wm_iconphoto(False, ICON)

        # Search Box
        self.downloadSearchBar = tk.Entry(self.downloadWindow)
        self.downloadSearchBar.pack(fill=tk.X)
        self.downloadSearchBar.configure(background="white")
        self.downloadSearchBar.configure(disabledforeground="#a3a3a3")
        self.downloadSearchBar.configure(foreground="#000000")
        self.downloadSearchBar.configure(insertbackground="black")

        # Button to search for song to downloads
        self.searchButton = tk.Button(self.downloadWindow)
        self.searchButton.pack(fill=tk.X)
        self.searchButton.configure(activebackground="#ececec")
        self.searchButton.configure(activeforeground="#000000")
        self.searchButton.configure(background=self.BG)
        self.searchButton.configure(disabledforeground="#a3a3a3")
        self.searchButton.configure(foreground=self.FG)
        self.searchButton.configure(highlightbackground=self.BG)
        self.searchButton.configure(highlightcolor="black")
        self.searchButton.configure(pady="0")
        self.searchButton.configure(text="Search")
        self.searchButton.configure(command=self.getSongs)
        
    def selectSongToDownload(self):
        self.downloadWindow.destroy()
        self.downloadWindow2 = tk.Toplevel(self.root)
        self.downloadWindow2.title("Download Song")
        self.downloadWindow2.resizable(0, 0)
        self.downloadWindow2.configure(relief='groove')
        self.downloadWindow2.configure(borderwidth="2")
        self.downloadWindow2.configure(relief="groove")
        self.downloadWindow2.configure(background=self.BG)
        ICON = tk.PhotoImage(file="SmallLogo.png")
        self.downloadWindow2.wm_iconphoto(False, ICON)
        self.downloadWindow2.bind("<Destroy>", self.reloadCurrentMusic)
        
        imageDisplay = tk.Label(self.downloadWindow2, text="IMAGE")
        imageDisplay.pack()
        
        songName = tk.Label(self.downloadWindow2, text=self.results[0], fg=self.FG, bg=self.BG)
        songName.pack()
        
        self.downloadButton = tk.Button(self.downloadWindow2, text="Download", command=lambda: self.download(songName["text"]), fg=self.FG, bg=self.BG)
        self.downloadButton.pack(fill=tk.X)

        try:
            u = urllib.request.urlopen(self.resultImages[0])
            raw_data = u.read()
            u.close()
            image = Image.open(BytesIO(raw_data))
            image = image.resize((640, 360))

            image = ImageTk.PhotoImage(image)

            imageDisplay.configure(image=image)
            imageDisplay.photo = image
        except urllib.error.HTTPError:
            imageDisplay.configure(text="Unable to fetch image")

    def deleteSong(self, path, _):
        os.remove(path)

    def updateSongInfo(self, _=None, overrideSong=None):
        if overrideSong is None:
            updateThread = Thread(target=self._updateSongInfo)
            updateThread.start()
        else:
            updateThread = Thread(target=self._updateSongInfo, args=(overrideSong,))
            updateThread.start()

    def _updateSongInfo(self, overrideSong=None):
        if overrideSong is None:
            selection = self.song_listbox.selection_get()
        else:
            selection = str(overrideSong)
            selection = os.path.splitext(selection)[0]

        if len(self.song_listbox.curselection()) != 0 or overrideSong is not None:
            self.currentSongLabel.configure(text=selection)
            self.currentSongLabel.place_forget()
            self.currentSongLabel.place(x=1010 - (4.5 * len(selection)), y=784)

            URL = None
            for list_ in self.songsInfo:
                if list_[0] == selection + ".mp4":
                    URL = list_[1]
                    break
            try:
                u = urllib.request.urlopen(URL)
                raw_data = u.read()
                u.close()
                image = Image.open(BytesIO(raw_data))
                image = image.resize((640, 360))

                image = ImageTk.PhotoImage(image)

                self.songImageDisplay.configure(image=image)
                self.songImageDisplay.photo = image
            except urllib.error.HTTPError:
                self.songImageDisplay.configure(text="Unable to fetch image")

    def resetSong(self):
        self.currentSong = ""
        self.play_pause()

    def openSettingsMenu(self):
        # Create frame from which the user can download songs
        self.settingsWindow = tk.Toplevel(self.root)
        self.settingsWindow.title("Settings")
        self.settingsWindow.resizable(0, 0)
        self.settingsWindow.geometry("330x550")
        self.settingsWindow.configure(background=self.BG)
        ICON = tk.PhotoImage(file="SmallLogo.png")
        self.settingsWindow.wm_iconphoto(False, ICON)
        self.settingsWindow.bind("<Destroy>", self.reloadCurrentMusic)

        self.bgColourButton = tk.Button(self.settingsWindow, bg=self.BG, fg=self.FG, relief=tk.FLAT,
                                        text="Change background colour", command=self.changeBG)
        self.bgColourButton.pack()

        self.fgColourButton = tk.Button(self.settingsWindow, bg=self.BG, fg=self.FG, relief=tk.FLAT,
                                        text="Change foreground colour", command=self.changeFG)
        self.fgColourButton.pack()

    def changeBG(self):
        c = color.askcolor()[1].upper()
        self.BG = c
        self.root.configure(bg=self.BG)
        for frame in self.root.winfo_children():
            frame.configure(bg=self.BG)
            for widget in frame.winfo_children():
                widget.configure(bg=self.BG)

    def changeFG(self):
        c = color.askcolor()[1].upper()
        self.FG = c
        for frame in self.root.winfo_children():
            for widget in frame.winfo_children():
                widget.configure(fg=self.FG)

    def search_for_songs(self, _=None):
        self.reloadCurrentMusic()
        search_term = self.search_bar.get().upper()
        if search_term == "":
            self.reloadCurrentMusic()

        else:
            items = self.song_listbox.get(0, tk.END)
            print(items)
            new_items = []
            for item in items:
                if search_term in item.upper():
                    new_items.append(item)
            self.song_listbox.delete(0, tk.END)
            print(new_items)
            for item in new_items:
                self.song_listbox.insert(tk.END, item)
            sort_listbox(self.song_listbox)

    def collapseSongArea(self):
        if self.collapsed:
            self.collapseSongsButton.place_forget()
            self.soundbarFrame.place_forget()
            self.songsFrame.place(relx=0.0, rely=0.0, relheight=1, relwidth=0.27)
            self.songsTitle.pack()
            self.song_listbox.pack()
            self.delete_button.place(relx=0.5, rely=0.97, relwidth=0.49)
            self.search_bar.place(relx=0, rely=0.940, relwidth=0.99, height=25)
            self.collapseSongsButton.place(relx=0.97, rely=0, relheight=1)
            self.browse_button.place(relx=0, rely=0.97, relwidth=0.5)
            self.title_bar.place(relx=0.15, rely=0.01, relheight=0.157, relwidth=0.998)

            self.soundbarFrame.place(relx=0.31, rely=0.94, relheight=0.06, relwidth=0.69)

            try:
                selection = self.currentSongLabel["text"]
            except:
                selection = ""
            self.currentSongLabel.place(x=1010 - (4.5 * len(selection)), y=784)
            self.songImageDisplay.place(relx=0.45, rely=0.3)

            self.collapsed = False
        else:
            self.songsFrame.place(relx=0.0, rely=0.0, relheight=1, relwidth=0.1)
            self.songsTitle.pack_forget()
            self.currentSongLabel.place_forget()
            self.songImageDisplay.place_forget()
            self.song_listbox.pack_forget()
            self.delete_button.place_forget()
            self.search_bar.place_forget()
            self.browse_button.place_forget()
            self.collapseSongsButton.place_forget()
            self.collapseSongsButton.configure(command=self.collapseSongArea)
            self.collapseSongsButton.place(relx=0.02, rely=0, relheight=1, relwidth=0.1)
            self.collapsed = True

            self.title_bar.place_forget()
            self.soundbarFrame.place_forget()
            self.title_bar.place(relx=0.157)
            self.delete_button.configure(command=self.deleteSelectedSong)
            self.browse_button.configure(command=self.openDownloadWindow)
            self.play_pause_button.configure(command=self.play_pause)
            self.skip_button.configure(command=None)
            self.back_button.configure(command=self.resetSong)
            self.soundbarFrame.place(relx=0.116, rely=0.94, relheight=0.06, relwidth=0.69)

            try:
                selection = self.currentSongLabel["text"]
            except:
                selection = ""
            self.currentSongLabel.place(x=745 - (4.5 * len(selection)), y=784)

            self.songImageDisplay.place(relx=0.26, rely=0.3)


if __name__ == '__main__':
    a = MainWindow()
    a.root.mainloop()
