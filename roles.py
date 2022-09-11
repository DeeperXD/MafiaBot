
class Citizen:
    tag = 'civilian'
    can_die = False

    def __init__(self, user, role):
        self.role = role
        self.user = user
        self.is_alive = True

    async def kill(self):
        self.is_alive = False
        await self.user.send('Ти здох лашпет')

    async def action(self, target_player):
        if target_player:
            print(f"action to {target_player.user.nick}")

    def action_access(self, game_info):
        return ''


class Mafia(Citizen):
    tag = "mafia"

    def action_access(self, game_info):
        if not game_info.is_night_voiting:
            return "Mafia can kill only in night"
        return ''


class Doctor(Citizen):
    last_heal_player = 0

    def can_heal(self, target_id):
        return self.last_heal_player != target_id

    async def action(self, target_player):
        print("doc action")
        if not target_player:
            self.last_heal_player = 0
            return

        self.last_heal_player = target_player.user.id

        if target_player.can_die:
            target_player.can_die = False
            print(f'healed {target_player.user.nick}')

    def action_access(self, game_info):
        if not game_info.is_night_voiting:
            return 'Doctor can heal only in night'
        return ''


class Detective(Citizen):
    checked_this_night = False

    async def action(self, target_player):
        self.checked_this_night = False

    def action_access(self, game_info):
        if not game_info.is_night_voiting:
            return 'Detective can check only in night'
        return ''


active_players = {
    'citizen': Citizen,
    'doctor': Doctor,
    'mafia': Mafia,
    'detective': Detective
}


def create_player(member, role):
    if role in active_players:
        return active_players[role](member, role)
    else:
        return None
