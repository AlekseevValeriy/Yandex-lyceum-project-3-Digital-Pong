from icecream import ic
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.textfield import MDTextField

class SearchRoomField(MDTextField):
    api = StringProperty('')
    room_id_length = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(SearchRoomField, self).__init__(*args, **kwargs)
        self.bind(on_text=self.text_formatting)

    def template(self) -> MDTextField:
        return SearchRoomField()

    def text_formatting(self, id_string: str) -> None:
        def cropping(text: str, length: int) -> str:
            return text[:length]

        def clipping(text: str) -> str:
            if text and not text[-1].isdigit():
                return text[:-1]
            return text

        self.root.ids.room_field.text = cropping(clipping(id_string), self.room_id_length)

        if self.api:
            # self.root.ids.room_field.error = True if not self.server.id_confirm(id_text) else False
            ...
