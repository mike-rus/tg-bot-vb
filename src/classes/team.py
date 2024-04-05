from classes.team_base import TeamBase


class Team(TeamBase):
    def __init__(self, team_id: int, topic_id: int, team_name: str = ""):
        super().__init__(team_id, topic_id, team_name)
