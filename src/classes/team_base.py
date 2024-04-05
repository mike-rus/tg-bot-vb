# Base class for different type of Teams
class TeamBase:
    def __init__(self, team_id: int, message_thread_id: int, team_name: str):
        # TODO Verify team id existence in the system
        self._team_id = team_id  # for website
        self._message_thread_id = message_thread_id
        self._team_name = team_name

    @property
    def message_thread_id(self) -> int:
        return self._message_thread_id

    @property
    def team_id(self) -> int:
        return self._team_id

    @property
    def team_name(self) -> int:
        return self._team_name

    def __str__(self) -> str:
        return f"Team {self._team_name} #{self._team_id}"

    def data_to_json(self) -> dict:
        return {
            "team_id": self._team_id,
            "message_thread_id": self._message_thread_id,
            "team_name": self._team_name,
        }
