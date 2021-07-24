import shutil
import tkinter.messagebox as box
from googleapiclient.errors import HttpError
import argparse
from googleapiclient.discovery import build
import pytube
import os

import mp4Convert


class youtubeSearch(object):
    global DEVELOPER_KEY, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION
    DEVELOPER_KEY = 'UR_NOT_SEEING_THIS!'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    def __init__(self):
        self.url = ""
        self.videos = []
        self.parser = argparse.ArgumentParser()
        self.args = None

    def youtube_search(self, options):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey=DEVELOPER_KEY)
        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(  # LAG
            q=options.q,
            part='id,snippet',
            maxResults=options.max_results
        ).execute()
        self.videos = []
        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                self.videos.append('%s' % (search_result['id']['videoId']))
        return self.videos

    def search(self, query):
        print("1")
        self.parser.add_argument('--q', help='none', default=query)
        self.parser.add_argument('--max-results', help='Max results', default=1)
        self.args = self.parser.parse_args()
        print("2")

        v = self.youtube_search(self.args)
        print("Return")
        return v


def download(end):
    try:
        vid = pytube.YouTube("http://www.youtube.com/watch?v=" + end)
        video = vid.streams.first()
        print(video)
        filename = video.default_filename
        out_file = video.download(output_path=os.getcwd() + "\\downloads")
        base, ext = os.path.splitext(out_file)
        print(out_file)
        mp4Convert.mp4tomp3(out_file)
        os.remove(out_file)
        with open(os.getcwd() + "\\downloads\\info.csv", "a") as f:
            f.write(str(filename) + "," + str(vid.thumbnail_url) + "\n")
        return os.getcwd() + "\\downloads\\" + filename, filename
    except:
        print("Try failed")
        try:
            os.remove(os.getcwd() + "\\downloads\\" + filename)
        except:
            pass
        download(end)
