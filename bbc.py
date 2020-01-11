import requests
import webbrowser
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup


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
    global titles
    global ids
    global thumbnails
    api_key = 'AIzaSyBp12_b1xWX6Vpb7RgOl5hJmexoochn4qg'
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
                    titles.append(title)
                    ids.append(id)
                    thumbnail = x.get('snippet').get('thumbnails').get('high').get('url')
                    thumbnails.append(thumbnail)
                    i += 1


titles, ids, thumbnails = [], [], []


class ErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Błąd!'
        self.title_align = 'center'
        self.size_hint = [None, None]
        self.width = 800
        self.height = 400
        self.auto_dismiss=False
        box_main = BoxLayout(orientation='vertical')
        box_main.add_widget(Label(text='Nie można połączyć się z siecią!'))
        box_button = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=10)
        box_button.add_widget(Button(text='Wyjdź', on_press=self.exit_app))
        box_button.add_widget(Button(text='Spróbuj ponownie', on_press=self.retry))
        box_main.add_widget(box_button)
        self.add_widget(box_main)

    def exit_app(self, *args):
        self.parent.close()

    def retry(self, *args):
        self.dismiss()
        get_videos()


class BBCBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 100
        get_videos()
        for i in range(len(titles)):
            box = BoxLayout(orientation='vertical', on_touch_down=self.touch)
            lab = Label(text=titles[i], size_hint_y=None, height=20)
            self.icon = AsyncImage(source=thumbnails[i])
            box.add_widget(lab)
            box.add_widget(self.icon)
            self.add_widget(box)
        self.add_widget(Button(text='Wyjdź', on_press=self.quit_app, size_hint_y=None, height=100))

    def touch(self, *args):
        if args[0].collide_point(args[1].x, args[1].y):
            id = ids[titles.index(args[0].children[1].text)]
            webbrowser.open(f'http://www.youtube.com/watch?v={id}')

    def quit_app(self, *args):
        self.parent.close()


class BBC(App):
    def build(self):
        return BBCBox()


bbc = BBC()