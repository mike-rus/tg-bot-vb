from classes.club import Club


class Team(Club):
    def __init__(self, chat_id, team_id, topic_id, title):
        super().__init__(chat_id)
        self.team_id = team_id  # for website
        self.topic_id = topic_id  # message_thread_id
        self.team_title = title

    def __str__(self):
        return f"Team {self.team_id} in Club with chat_id: {self.chat_id}"
