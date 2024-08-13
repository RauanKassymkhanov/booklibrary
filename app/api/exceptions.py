class NotFoundError(Exception):
    def __init__(self, name: str, name_id: int):
        self.name = name
        self.name_id = name_id
        self.message = f"{name.capitalize()} with id {name_id} was not found."
        super().__init__(self.message)
