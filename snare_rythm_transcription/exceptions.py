class SoundFontNotFound(Exception):
    def __init__(self, path):
        self.message = f'sound font "{path}" not found'
        super().__init__(self.message)

    def __str__(self):
        return self.message