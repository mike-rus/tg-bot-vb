# Base class for different type of Teams
class TeamBase:
    def __init__(self, club_id, message_thread_id, team_name, team_id):
        self.team_id = team_id  # for website
        self.club_id = club_id  # same as chat_id
        self.message_thread_id = message_thread_id
        self.team_name = team_name

    def get_team_message_thread_id(self) -> int:
        return self.message_thread_id

    def get_team_id(self) -> int:
        return self.team_id

    def get_team_name(self) -> int:
        return self.team_name

    def get_club_id(self) -> int:
        return self.club_id

    def __str__(self):
        return f"Team {self.team_name} #{self.team_id} in Club with chat_id: {self.club_id}"

    def data_to_json(self):
        return {
            "club_id": self.club_id,
            "team_id": self.team_id,
            "message_thread_id": self.message_thread_id,
            "team_name": self.team_name,
        }
