from typing import List

from classes.team import Team


class Club:
    def __init__(self, chat_id: int, title: str):
        self.chat_id = chat_id
        self.title = title
        self.teams: List[Team] = []

    def get_chat_id(self) -> int:
        return self.chat_id

    def get_title(self) -> str:
        return self.title

    def __str__(self):
        return f"Club with chat_id: {self.chat_id}"

    def data_to_json(self):
        return {"chat_id": self.chat_id, "title": self.title, "teams": []}
    
    # TODO: is it okay to have it here or club should not know about teams?
    def add_team(self, team):
        self.teams.append(team)
        
    def remove_team(self, team):
        self.teams.remove(team)        
        
    def has_team(self, team_id: int) -> bool:
        return any(team.get_team_id() == team_id for team in self.teams)
    
    def get_team_by_id(self, team_id: int) -> Team:
        return next((team for team in self.teams if team.get_team_id() == team_id), None)

    # TODO add polling
