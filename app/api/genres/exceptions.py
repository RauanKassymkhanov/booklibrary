class GenreNotFoundError(Exception):
    def __init__(self, genre_id: int):
        self.genre_id = genre_id
        self.message = f"Genre with id {genre_id} was not found"
        super().__init__(self.message)
