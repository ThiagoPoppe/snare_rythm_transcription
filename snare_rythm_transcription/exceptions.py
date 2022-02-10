class SoundFontNotFound(Exception):
    def __init__(self, path):
        self.path = path
        self.message = f'sound font not found'
        super().__init__(self.message)

    def __str__(self):
        return f'{self.path} -> {self.message}'