import os
import certifi
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel

os.environ['SSL_CERT_FILE'] = certifi.where()
import requests
import webbrowser
import json
from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup

class BBCData:
    def __init__(self):
        self.titles = []
        self.ids = []
        self.thumbnails = []

bbc_data = BBCData()

def get_time(duration):
    minutes, seconds = '', ''
    for x in duration:
        if x != 'M' and x != 'S':
            seconds += x
        elif x == 'S':
            if minutes == '':
                minutes = 0
        else:
            minutes = seconds
            seconds = ''
    if 0 < int(minutes) < 3:
        return True
    else:
        return False


def get_short_title(title):
    title = title.split()[:3]
    new_title = ''
    for i in title:
        new_title += f'{i} '
    return new_title


def get_videos():
    api_key = 'AIzaSyAST2MxD3uE4JryFq0t5UgNu9EcGMkz1lw'
    channel_id = 'UCndmr6gTAxUk8rxA8yF8Rwg'
    try:
        web = requests.get(f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&maxResults=30')
        json_data = json.loads(web.text)
        video_id = json_data.get('items')
    except requests.exceptions.ConnectionError:
        ErrorPopup().open()
        video_id = []
    i = 0
    for x in video_id:
        title = x.get('snippet').get('title')
        if 'BBC' in title:
            id = x.get('id').get('videoId')
            web = requests.get(f'https://www.googleapis.com/youtube/v3/videos?id={id}&part=contentDetails&key={api_key}')
            json_data = json.loads(web.text)
            duration = json_data.get('items')[0].get('contentDetails').get('duration')
            duration = duration[2:6]
            if get_time(duration):
                if i > 2:
                    break
                else:
                    title = get_short_title(title)
                    bbc_data.titles.append(title)
                    bbc_data.ids.append(id)
                    thumbnail = x.get('snippet').get('thumbnails').get('high').get('url')
                    bbc_data.thumbnails.append(thumbnail)
                    i += 1


class ErrorPopup(Popup):
    def exit_app(self, *args):
        self.parent.close()

    def retry(self, *args):
        self.dismiss()
        get_videos()


class AutoBox(ButtonBehavior, BoxLayout):
    pass


class AutoLabel(MDLabel):
    pass

class ExitButton(MDRaisedButton):
    pass

class BBCBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        get_videos()
        for i in range(len(bbc_data.titles)):
            box = AutoBox(on_press=self.touch)
            lab = AutoLabel(text=bbc_data.titles[i])
            self.icon = AsyncImage(source=bbc_data.thumbnails[i])
            box.add_widget(lab)
            box.add_widget(self.icon)
            self.add_widget(box)
        self.add_widget(ExitButton())

    def touch(self, *args):
        id = bbc_data.ids[bbc_data.titles.index(args[0].children[1].text)]
        webbrowser.open(f'http://www.youtube.com/watch?v={id}')

    def quit_app(self, *args):
        self.parent.close()


class BBCApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return BBCBox()

bbc = BBCApp()
bbc.run()