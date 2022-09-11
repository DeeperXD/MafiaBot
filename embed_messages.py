from random import randint
from discord import Embed, Colour

random_messages_night = ['Мафія вилазить зі щілин', 'Наводиться шухер', 'Шухер! Мафія йде']

random_messages_morning = ['Нечесть поховалась']


def player_and_rol(player, rol):
    embed = Embed(
        title='**Нова гра - почалась**',
        description='------------------------------------------\n'
                    f'{player}\nТвоя роль : **{rol}**'
    )
    return embed


def win(winner):
    if winner == 'Мафія':
        r, g, b = 125, 0, 0
    else:
        r, g, b = 50, 205, 50
    embed = Embed(
        title='**Переможець:**',
        description=f'**{winner}**',
        colour=Colour.from_rgb(r, g, b)
    )
    return embed


def start_game():
    embed = Embed(
        title='**Нова гра - почалась**',
        colour=Colour.from_rgb(50, 205, 50)
    )
    return embed


def start_night(number_of_day):
    global random_messages_night
    num = randint(0, len(random_messages_night))
    print(num)
    embed = Embed(
        title=f'День {number_of_day}',
        description=f'**Ніч - почалась**\n{random_messages_night[num]}\n'
                    '°　　　•　　.°•　　　 ✯\n'
                    '　　　★　*　　　　　°　　　　 　°·　　\n\n'
                    '.　　　•　° ★　•\n'
                    '▁▂▃▄▅▆▇▇▆▅▄▃▁▂\n',
        colour=Colour.from_rgb(0, 0, 0)
    )

    return embed



def vote(time):
    embed = Embed(
        title='Голосування',
        description=f'Голосування буде впродовж **{time}** секунд\n'
                    'Для голосування введіть: **!voice <нік>**\n'
                    'Для відміни голосу введіть: **!voice -**',
        colour=Colour.from_rgb(255, 140, 0)
    )
    return embed


def get_ending_by_voice_count(voice_count):
    if 4 < voice_count < 20:
        return 'гравців'
    else:
        remainder = voice_count % 10
        if remainder == 1:
            return 'гравець'
        if 1 < remainder < 5:
            return 'гравці'

    return 'гравців'


def get_zakidalo(voice_count): return 'закидав' if voice_count == 1 else 'закидав'
    # if voice_count == 1:
    #     return 'закидав'
    #
    # return 'закидало'

def end_vote(player, count, show_role_after_death):

    if player:
        description = f"Гравця **{player.user.nick}** {get_zakidalo(count)} {count} {get_ending_by_voice_count(count)}"
        print(description)
        if show_role_after_death:
            description += f'\n**{player.user.nick}** був **{player.role}**'
            print(description)

        embed = Embed(
            title='**Досмерті закиданий помідорами:**',
            description=description,
            colour=Colour.from_rgb(255, 255, 0)
        )
    else:
        embed = Embed(
            title='**Сьогодні нікого не стратили**',
            colour=Colour.from_rgb(255, 255, 0)
        )
    return embed


def speach(time):
    global random_messages_morning

    num = randint(0, len(random_messages_morning))

    embed = Embed(
        title='**Ніч накінчилась**',
        description=f'**{random_messages_morning[num]}**,\n'
                    f'Ви маєте {time} секунд для обговорення',
        colour=Colour.from_rgb(255, 140, 0)
    )
    return embed


def end_night(list):
    players = []
    for j in list:
        players.append(j.user.nick)
    if len(list) != 0:
        embed = Embed(
            title='**Убиті гравці**',
            description='\n'.join(players),
            colour=Colour.from_rgb(128, 0, 128)
        )
    else:
        embed = Embed(
            title='**Сьогодні в ночі нікого не убили**',
            colour=Colour.from_rgb(128, 0, 128)
        )
    return embed


def help_def(actions):
    com_list = []
    for action in actions:
        name = action.action.__name__
        desc = action.description

        com_list.append(f"**{name}** - {desc}")
    embed = Embed(
        title='**Commands list:**',
        description='\n'.join(com_list),
        colour=Colour.from_rgb(0, 0, 255)
    )
    return embed


def show_active_players(player_list):
    print('msg')
    alive_list = []
    for player in player_list:
        alive = 'мертвий'
        if player.is_alive:
            alive = 'живий'
        alive_list.append(f'{player.user.nick} - **{alive}**')
    embed = Embed(
        title='**Список гравців**',
        description='\n'.join(alive_list)
    )
    return embed


emb = None
players_list = {}


def start_embed():
    embed = Embed(
        title='**Голосування**',
        colour=Colour.from_rgb(255, 255, 0)
    )
    return embed


def mem_embed(embed):
    global emb
    emb = embed


def show_voice(nickname_dick):
    global emb
    global players_list
    voic = []


    for key, value in nickname_dick.items():
        if value in players_list:
            players_list[value].append(key)
        else:
            players_list[value] = [key]
        print(key, value)

    for a in players_list:
        message = f'Гравець **{a}**\n{len(players_list[a])}'
        voic.append(message)

    embed = Embed(
        title='**Голосування**',
        description='\n'.join(voic),
        colour=Colour.from_rgb(255, 255, 0)
    )

    players_list = {}
    return emb, embed
