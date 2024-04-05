from typing import List

from classes.team_base import TeamBase


class Club:
    def __init__(self, chat_id: int, title: str):
        self._chat_id = chat_id
        self._title = title
        # TODO: make team list also a property
        self.teams: List[TeamBase] = []

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def title(self) -> str:
        return self._title

    def __str__(self) -> str:
        return f"Club with chat_id: {self._chat_id}"

    def data_to_json(self) -> dict:
        return {
            "chat_id": self._chat_id,
            "title": self._title,
            "teams": [team.data_to_json() for team in self.teams],
        }

    def add_team(self, team: TeamBase) -> bool:
        if self.has_team(team.team_id):
            return False
        self.teams.append(team)
        return True

    def remove_team(self, team_id: int) -> bool:
        team_to_remove = self.get_team_by_id(team_id)
        if team_to_remove:
            self.teams.remove(team_to_remove)
            return True
        return False

    def has_team(self, team_id: int) -> bool:
        return any(team.team_id == team_id for team in self.teams)

    def get_team_by_id(self, team_id: int) -> TeamBase | None:
        return next((team for team in self.teams if team.team_id == team_id), None)

    # TODO add polling
