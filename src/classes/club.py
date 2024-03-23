class Club:
    def __init__(self, chat_id: int, title: str):
        self.chat_id = chat_id
        self.title = title

    def get_chat_id(self) -> int:
        return self.chat_id

    def get_title(self) -> str:
        return self.title

    def __str__(self):
        return f"Club with chat_id: {self.chat_id}"

    def data_to_json(self):
        data = {"chat_id": self.chat_id, "title": self.title}
        return data

    # TODO add polling
