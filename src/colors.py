class Colors:
    def __init__(self, theme='dark'):
        self.theme = theme
        self.set_theme(theme)

    def set_theme(self, theme):
        self.theme = theme
        if theme == 'dark':
            self.BRIGHT_BLUE = "#0080FF"
            self.BRIGHT_WHITE = "#FFFFFF"
            self.GREEN = "#00FF00"
            self.YELLOW = "#FFFF00"
            self.CYAN = "#00FFFF"
            self.MAGENTA = "#FF00FF"
            self.RED = "#FF0000"
            self.BLACK = "#000000"
        else:
            self.BRIGHT_BLUE = "#0000FF"
            self.BRIGHT_WHITE = "#000000"
            self.GREEN = "#008000"
            self.YELLOW = "#C8C800"
            self.CYAN = "#008080"
            self.MAGENTA = "#800080"
            self.RED = "#FF0000"
            self.BLACK = "#FFFFFF"