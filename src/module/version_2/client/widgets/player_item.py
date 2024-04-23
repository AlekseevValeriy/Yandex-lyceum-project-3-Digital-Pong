from random import random
from typing import Any

from icecream import ic
from kivy.properties import NumericProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText, MDListItemSupportingText

from src.module.version_2.client.data import PlayerItem


class PlayerListItem(MDListItem):
    status = NumericProperty(0)


    def md_chip_template(self, data: str) -> MDChip:
        def waiting(widget_class: Any) -> None:
            match widget_class.__class__.__name__:
                case 'MDChip':
                    if widget_class.theme_bg_color == 'Primary':
                        widget_class.theme_bg_color = 'Custom'
                    widget_class.md_bg_color = (random(), random(), random(), 1)

        return MDChip(
            MDChipText(text=data),
            pos_hint={'center_y': .5},
            theme_bg_color='Primary',
            on_release=waiting)

    def remove_player(self, player_button: MDIconButton, *args) -> None:
        player_button.parent.parent.remove_widget(player_button.parent)

    def template(self, player_item_data: PlayerItem) -> MDListItem:
        # TODO при множественном нажатии на создать игрока, он перестаёт удаляться
        return PlayerListItem(
            MDListItemLeadingIcon(icon=player_item_data.icon),
            MDListItemHeadlineText(text=player_item_data.nickname),
            MDListItemSupportingText(text=player_item_data.location),
            *tuple(self.md_chip_template(data) for data in player_item_data.chips),
            MDIconButton(
                icon="skull-crossbones-outline",
                style="filled",
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                on_release=self.remove_player
            ),
            status=player_item_data.status
        )
