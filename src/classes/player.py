from classes.member import Member


class Player(Member):
    def __init__(self, telegram_id, team, person_id, surname, name):
        super().__init__(telegram_id, surname, name)
        self.team = team
        self.person_id = person_id
