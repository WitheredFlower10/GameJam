import arcade

MENU_OPTIONS = [
    "Connecter a l'ecran",
    "Chat du futur ($20 chaque fois)",
    "Achat des infos",
    "Discuter avec le Hero",
    "Met le Pari"
]

class MainTerminal:
    def __init__(self, window, on_select_callback=None, on_exit_callback=None, screen_connected=False):
        self.window = window
        self.selected_index = 0
        self.on_select_callback = on_select_callback
        self.on_exit_callback = on_exit_callback
        self.font_terminal = "ByteBounce"
        self.screen_connected = screen_connected

    @property
    def menu_options(self):
        if self.screen_connected:
            return ["Ecran deja connecte"] + MENU_OPTIONS[1:]
        else:
            return MENU_OPTIONS



    def on_draw(self):
        # 小终端参数
        w, h = 450, 300
        screen_width, screen_height = self.window.width, self.window.height
        x = screen_width - w - 30
        y = screen_height - h - 30
        term_green = (0, 255, 0)
        font_terminal = self.font_terminal

        # 背景 + 边框
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)

        # 标题
        arcade.draw_text("Terminal", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)

        # 菜单选项
        option_gap = 32
        for i, option in enumerate(self.menu_options):
            oy = y + h - 70 - i * option_gap
            if i == self.selected_index and not (self.screen_connected and i == 0):
                arcade.draw_lrbt_rectangle_outline(x+18, x+w-18, oy-6, oy+24, term_green, 2)
                bold = True
            else:
                bold = False
            arcade.draw_text(option, x+32, oy, term_green, 20, font_name=font_terminal, bold=bold)

    def on_key_press(self, key, modifiers):
        max_index = len(self.menu_options) - 1
        if key == arcade.key.UP:
            prev = self.selected_index
            while True:
                self.selected_index = (self.selected_index - 1) % (max_index + 1)
                if not (self.screen_connected and self.selected_index == 0):
                    break
                if self.selected_index == prev:
                    break
        elif key == arcade.key.DOWN:
            prev = self.selected_index
            while True:
                self.selected_index = (self.selected_index + 1) % (max_index + 1)
                if not (self.screen_connected and self.selected_index == 0):
                    break
                if self.selected_index == prev:
                    break
        elif key in (arcade.key.ENTER, arcade.key.RETURN):
            if not (self.screen_connected and self.selected_index == 0):
                if self.on_select_callback:
                    self.on_select_callback(self.selected_index)
        elif key == arcade.key.ESCAPE:
            if self.on_exit_callback:
                self.on_exit_callback()
