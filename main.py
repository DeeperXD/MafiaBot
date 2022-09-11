import discord
from discord.ext import commands
import asyncio
import random
import embed_messages
import appinfo

import roles as role_controller

# region ---------------------TITLE------------------------------

# mafiabot v.0.1 - support only for one game seance
# made by DeeperXD

#   ##     ##       #       #########   #       #
#   # #   # #      # #      #                  # #
#   #  # #  #     #   #     #           #     #   #
#   #   #   #    #######    ######      #    #######
#   #       #   #       #   #           #   #       #
#   #       #  #         #  #           #  #         #

# endregion --------------------------------------------------------

# region ---------------------BASIC_INFO-------------------------

TOKEN = appinfo.TOKEN
command_prefix = '!'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=command_prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')

guild_id = appinfo.guild_id
text_channel_id = appinfo.text_channel_id
voice_channel_id = appinfo.voice_channel_id
mafia_text_channel_id = 0

working_channel_id = appinfo.working_channel_id
# endregion ---------------------BASIC_INFO-------------------------

# region ---------------------GAME_RULES-------------------------

all_roles = ['mafia', 'doctor', 'detective', 'citizen', 'citizen', 'mafia', 'citizen']  # add at least 16 roles

night_time = 5
talking_time = 0
private_talking_time = 30
voice_time = 35

show_role_after_death = True

play_less_4 = True
mafia_suicide = True

check_end_game = False

private_talking = False
talking = False

nickname_case_insensitive = True

is_developer_mode = True

show_player_voiting = True

# endregion ---------------------GAME_RULES-------------------------

# region ----------------------CLASSES---------------------------


class Act:
    def __init__(self, action, description, access_roles, on_fail_access_msg, include_empty_target):
        self.action = action
        self.description = description
        self.access_roles = access_roles
        self.on_fail_access_msg = on_fail_access_msg
        self.include_empty_target = include_empty_target


class GameLogic:
    def __init__(self):
        self.is_voiting = False
        self.is_night_voiting = False
        self.is_started = False
        self.voice_map = {}  # first - who voice, second purpose of voice
        self.active_voice_map = {}  # first - who voice, second purpose of voice
        self.current_day = 1
        self.players = []
        self.nickname_map = {}


    def clean(self):
        GameLogic.__init__(self)

    async def on_voice(self, ctx, from_player, to_player):
        previous_choice = 0 # self.voice_map[from_player.user.id] or 0
        print(f"{from_player.user.nick} previous choice: {previous_choice}")

        if not to_player:
            if ctx.author.id in self.voice_map:
                del self.voice_map[ctx.author.id]
                del self.nickname_map[from_player.user.nick]
                await ctx.send(f"Тепер ти ні за кого не голосуєш")
            else:
                await ctx.send(f"Ти **не** проголосував ні за кого, **курва**")
                return
        else:
            self.voice_map[from_player.user.nick] = to_player.user.id
            self.nickname_map[from_player.user.nick] = to_player.user.nick
            await ctx.send(f"Твій голос за: {to_player.user.nick} - **прийнятий**")

        emb, embed = embed_messages.show_voice(self.nickname_map)
        await emb.edit(embed=embed)


# endregion

# region ---------------------MAIN_COMMANDS----------------------
@bot.event
async def on_ready():
    global voice_channel
    global text_channel
    global guild
    global actions
    guild = bot.get_guild(guild_id)
    voice_channel = bot.get_channel(voice_channel_id)
    if is_developer_mode:
        text_channel = bot.get_channel(working_channel_id)
    else:
        text_channel = bot.get_channel(text_channel_id)

    actions = [
        Act(heal, "with this action you can heal somebody", ["doctor"], "You can't heal(attention)", True),
        Act(kill, "with this action you can kill somebody", ["mafia"], "You can't kill(attention)", True),
        Act(check, "with this action you can check somebody", ["detective"], "You can't check(attention)", False)
    ]

    print("bot started")


@bot.command(name='stop', description="stop current game seance")
async def stop(ctx):
    if not g_logic.is_started:
        await ctx.send("Game not started.")
    else:
        clear_game()
        await ctx.send("Game stopped")


@bot.command(name='seance', description="create new game seance")
async def start_seance(ctx):
    if not g_logic.is_started:
        await ctx.send("Game seance sucessfully crated!")
        await start_game()
    else:
        await ctx.send("You cant start game while last game not ended")


@bot.command(name='help', description="show all user commands")
async def help_kek(ctx): await ctx.send(embed=embed_messages.help_def(actions))

# endregion ---------------------MAIN_COMMANDS----------------------

# region ---------------------GAME_COMMANDS----------------------


@bot.command(name='active', description="show active players in game")
async def active(ctx):
    if not g_logic.is_started:
        await ctx.message.channel.send("Game not started")
        return

    await ctx.send(embed=embed_messages.show_active_players(g_logic.players))


async def basic_access(ctx, act_nickname, include_empty_target=True):
    if not g_logic.is_started:
        await ctx.send("You can't make any activity while game not started")
        return None, None

    player = get_player_by_id(ctx.author.id)

    if not player:
        await ctx.send("You are not in game")
        return None, None

    if not player.is_alive:
        await ctx.send("You died(")
        return None, None

    if act_nickname == '-' and include_empty_target:
        return player, None

    target_players = get_players_by_nick(act_nickname)
    print(target_players)
    if len(target_players) > 1:
        await ctx.send(f"Finded more that one player with nick: {act_nickname}")
        return None, None

    if len(target_players) == 0:
        await ctx.send(f"{act_nickname} are not in game")
        return None, None

    if not target_players[0].is_alive:
        await ctx.send(f'{act_nickname} is died, dude')
        return None, None

    return player, target_players[0]


@bot.command(name='a', description="any activity, voice for player")
async def activity(ctx, act_name, act_nickname):
    if nickname_case_insensitive:
        act_nickname = act_nickname.lower()
    #act_nickname = nickname_case_insensitive if act_nickname.lower() else act_nickname

    # check channel

    for act in actions:
        if act.action.__name__ == act_name:
            player, target_player = await basic_access(ctx, act_nickname, act.include_empty_target)
            if not player:
                return

            if player.role not in act.access_roles:
                await ctx.send(act.on_fail_access_msg)
                return

            act_message = player.action_access(g_logic)

            if act_message != '':
                await ctx.send(act_message)
                return

            await act.action(ctx, player, target_player)
            return

    await ctx.send(f"You enter incorrect action")


@bot.command(name='voice', description="game active command to choose player in day voiting")
async def voice(ctx, act_nickname):
    if nickname_case_insensitive:
        act_nickname = act_nickname.lower()
    player, target_player = await basic_access(ctx, act_nickname)
    if not player:
        return

    if not g_logic.is_voiting:
        await ctx.send(f"You can't voice now")
        return

    await g_logic.on_voice(ctx, player, target_player)


async def kill(ctx, player, target_player):
    print(f"{player.user.nick}decided to kill: {target_player.user.nick}")

    if not target_player:
        del g_logic.voice_map[player.user.id]
        await ctx.send(f"Your choice removed")
        return

    if not mafia_suicide and player == target_player:
        await ctx.send(f"You can't voice for mafia team")
        return

    g_logic.voice_map[ctx.author.id] = target_player.user.id
    await ctx.send(f"You decide to kill: {target_player.user.nick}")


async def heal(ctx, player, target_player):
    if not target_player:
        del g_logic.active_voice_map[player.user.id]
        await ctx.send(f"Your choice removed")
        return

    if player.last_heal_player == target_player.user.id:
        await ctx.send(f"You choice {target_player.user.nick} last night")
        return

    g_logic.active_voice_map[player.user.id] = target_player.user.id
    await ctx.send(f"You choice to heal {target_player.user.nick}")


async def check(ctx, player, target_player):
    if player.checked_this_night:
        await ctx.send(f"You already checked somebody this night")
        return

    if target_player == player:
        await ctx.send(f"You can't check yourself")
        return

    player.checked_this_night = True
    await ctx.send(f"{target_player.user.nick} is: {target_player.role}")


# endregion ---------------------GAME_COMMANDS----------------------

# region ---------------------FUNCTIONS--------------------------


def get_players_roles(roles, count):
    active_roles = roles[:count]
    random.shuffle(active_roles)

    return active_roles


def get_player_by_id(player_id):
    for player in g_logic.players:
        if player.user.id == player_id:
            return player
    return None


def get_players_by_nick(nickname):
    finded_players = []
    for player in g_logic.players:
        nick = player.user.nick
        if nickname_case_insensitive:
            nick = nick.lower()
        if nick == nickname:
           finded_players.append(player)
    return finded_players

# endregion ---------------------FUNCTIONS--------------------------

# region ---------------------GAME_LOGIC-------------------------


game_loop_task = None
g_logic = GameLogic()


async def start_game():
    global game_loop_task
    g_logic.is_started = True

    voice_members = voice_channel.members
    members = []
    for member in voice_members:
        if not member.bot:
            members.append(member)

    print(f"count of players: {len(members)}")

    if len(members) < 4 and not play_less_4:
        await text_channel.send("You can't play while players less than 4")
        return

    roles = get_players_roles(all_roles, len(members))

    await text_channel.send(embed=embed_messages.start_game())

    # TODO: give all players role - Mafia-player

    for i in range(len(roles)):
        player = role_controller.create_player(members[i], roles[i]) # create player by her role

        #await members[i].add_roles(role)

        await player.user.send(embed=embed_messages.player_and_rol(members[i].mention, player.role))

        g_logic.players.append(player)

    game_loop_task = asyncio.create_task(game_loop())


async def game_loop():
    global game_loop_task

    # region ---NIGHT---
    await start_night()
    print("night send tag")
    print(g_logic.current_day)
    print('try to print data')
    await text_channel.send(embed=embed_messages.start_night(g_logic.current_day))
    print("night send tag")
    await asyncio.sleep(night_time)

    died_players = await end_night()

    print('night ended')

    await text_channel.send(embed = embed_messages.end_night(died_players))
    print("try to print end night")
    if check_end_game:
        end_game, mafia_win = try_end_game()

        if end_game:
            if mafia_win:
                winn = 'Мафія'
            else:
                winn = 'Мирні жителі'

            await text_channel.send(embed=embed_messages.win(winn))
            clear_game()
            return

    # endregion

    # region ---DISCUSSING---
    if talking:
        await text_channel.send(embed = embed_messages.speach(talking_time))

        await asyncio.sleep(talking_time)

    if private_talking:

        # region ---PRIVATE_TALKING---

        # TODO - наголосити про початок висказування кожного гравця
        await text_channel.send(f"Now is time to private talking")

        # endregion

        await asyncio.sleep(5)
        for player in g_logic.players:
            if player.is_alive:

                # region ---PRIVATE_TALKING_FOR_PERSON---

                # TODO - наголосити про висказування певного ігрока

                await text_channel.send(f"{player.user.nick} have {private_talking_time} second to talk")

                # endregion

                await asyncio.sleep(private_talking_time)

                # TODO: skip private voice
    # endregion

    # region ---VOITING---

    await start_voiting()
    await text_channel.send(embed=embed_messages.vote(voice_time))
    emb = await text_channel.send(embed=embed_messages.start_embed())
    embed_messages.mem_embed(emb)


    await asyncio.sleep(voice_time)

    voutened, voices = await end_voiting()
    await text_channel.send(embed=embed_messages.end_vote(voutened, voices, show_role_after_death))

    if check_end_game:
        end_game, mafia_win = try_end_game()

        if end_game:
            if mafia_win:
                winn = 'Мафія'
            else:
                winn = 'Мирні жителі'

            await text_channel.send(embed=embed_messages.win(winn))
            clear_game()
            return
    # endregion

    g_logic.current_day += 1

    game_loop_task = asyncio.create_task(game_loop())


async def start_night():
    g_logic.is_night_voiting = True

    for player in g_logic.players:
        if player.tag == 'mafia' and player.is_alive:
            await player.user.send("you should voice")

    # mute all micro and camera


async def end_night():
    g_logic.is_night_voiting = False

    player_to_kill, voice_count = get_voice_target(g_logic.voice_map)
    g_logic.voice_map = {}

    if player_to_kill:
        player_to_kill.can_die = True

    for player in g_logic.players:
        if player.is_alive:
            if player.user.id in g_logic.active_voice_map:
                #print(f"{player.user.name} make action to {active_voice_map[player.user.id]}")

                target_player = get_player_by_id(g_logic.active_voice_map[player.user.id])
                await player.action(target_player)
            else:
                #print(f"{player.user.name} don't make action")
                await player.action(None)

    g_logic.active_voice_map = {}
    g_logic.nickname_map = {}
    if player_to_kill:
        if player_to_kill.can_die:
            player_to_kill.can_die = False
            player_to_kill.is_alive = False

            await player_to_kill.kill()
            return [player_to_kill]

    return []


def get_voice_target(all_map):
    voices = {}

    for player in g_logic.players:
        voices[player.user.id] = 0

    values = all_map.values()
    for i in values:
        voices[i] += 1

    print("voiting ended")
    items = voices.items()

    finded_same = False
    best_item = None
    for i in items:
        if not best_item:
            best_item = i
        elif i[1] == best_item[1]:
            finded_same = True
        elif i[1] > best_item[1]:
            best_item = i
            finded_same = False

    if finded_same or best_item[1] == 0:
        return None, 0

    print(best_item)

    voited_player = None
    for player in g_logic.players:
        if best_item[0] == player.user.id:
            voited_player = player
            break

    return voited_player, best_item[1]


async def start_voiting():
    g_logic.is_voiting = True

    print("try to show voiting")
    # embed_messages.start_embed()
    print("voiting started")


async def end_voiting():
    g_logic.is_voiting = False

    player, voices = get_voice_target(g_logic.voice_map)
    g_logic.voice_map = {}
    g_logic.nickname_map = {}
    if not player:
        return None, 0
    else:
        await player.kill()
        return player, voices


def try_end_game():
    mafia_count = 0
    other_count = 0
    for player in g_logic.players:
        if player.is_alive:
            if player.tag == 'mafia':
                mafia_count += 1
            else:
                other_count += 1

    print(f"mafia count: {mafia_count}, other players count: {other_count}")

    if mafia_count >= other_count or mafia_count == 0:
        is_mafia_win = mafia_count > 0

        if is_mafia_win:
            print('mafia win')
        else:
            print('citizen win')

        return True, is_mafia_win

    return False, False


def clear_game():
    global game_loop_task
    game_loop_task.cancel()

    g_logic.clean() # or GameInfo.clean(game_info)

# endregion ---------------------GAME_LOGIC----------------------



# TODO: more roles
# TODO: MAFIA_BOSS
#

# TODO: give special role for active players
# TODO: command like !seance of !stop can controlls only mafia-admins
# TOOD: skip command

# TODO: add mafia to special channel
# TODO: access for active roles send command only in local chat with bot or special active channel

# for globalization
# TODO: localization 'ua', 'eng'

# sounds like good idea
# TODO: sound in voice channel "night begins","day begins" and "game end"
# TODO: mark dead player nick as dead or his role(if access): "deeper[dead]

# @bot.command(name='break', description="switch seance state")
# async def break_seance(ctx):
#     if Seance == None:
#         print("not exist seance now")
#     else:
#         game.switchbreak()

# commands list
# !seance - create new game seance, to begin playing you need to be in special voice chanel
# !break - stops game while players(future support)
# !stop - crash current game
#
# !kill - kill player in night when you mafia
# !heal - heal player in night when you doctor
# !check - check somebody in night when you detective


# game cycle
# get all roles for players

# start first night
# voice for killing in special mafia channel and local chat voicing for target of doctor, detective a.o.
# killing and reviving players after night
# few minuts discuss
# voice for killing

# repeat

# stop game when mafia count >= citizen or mafia count == 0
# win message

bot.run(TOKEN)