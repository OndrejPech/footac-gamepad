"""
BE SURE YOU UPDATE game_setup before running this file
"""

import sys
import csv
import pygame
from pygame.locals import *
from typing import Union, Tuple
from config import config as cf
from config.pyvidplayer import Video
from config.game_setup import *

# from DB
ACTIONS_IDS = {'shot': 1, 'pass': 2, 'foul': 3, 'throw in': 4, 'corner': 5,
               'goal kick': 6, 'free kick': 7, 'substitution': 8, 'offside': 9,
               'goal': 10, 'penalty kick': 11, 'yellow card': 12,
               'red card': 13, 'lob cross': 14, }
LEFT_SIDE_ID = 1
RIGHT_SIDE_ID = 2

always_defending_side = {'goal kick'}
always_attacking_side = {'offside', 'corner'}
# penalty kick can be neutral side after the game


class TextField:
    """ A class to represent text label"""

    def __init__(self, rectangle: Rect, font, color: tuple,
                 text: Union[str, int] = 0, anchor='center', action_type=''):
        self.rct = rectangle
        self.position = self.rct.center
        self.value = text  # can be str or int  # later change text to value
        self.font = font
        self.color = color
        self.anchor = anchor
        self.type = action_type
        self.text_surface = None
        self.rect = None

    def render(self, color=None, value=None) -> None:
        """render a text_surface and anchor it to chosen position"""
        if not color:
            color = self.color
        if not value:
            value = self.value
        self.text_surface = self.font.render(str(value), 1, color)
        self.rect = self.text_surface.get_rect()  # get position
        setattr(self.rect, self.anchor, self.position)  # set new position

    def draw(self, surface) -> None:
        """blit text_surface on rect position of surface"""
        surface.blit(self.text_surface, self.rect)


def get_text_field(button_value, team, rt, lt):
    """return correct textfield object based on button. Value and team_with_ball"""

    home_data = {0: h_passes, 1: h_shots, 2: h_lobs, 3: h_fouls,
                 4: h_offsides, 5: h_score}
    away_data = {0: a_passes, 1: a_shots, 2: a_lobs, 3: a_fouls,
                 4: a_offsides, 5: a_score}

    # RT or LT pressed together with foul button Y
    if button_value == 3 and rt:
        if team:
            return h_red_cards
        else:
            return a_red_cards
    elif button_value == 3 and lt:
        if team:
            return h_yell_cards
        else:
            return a_yell_cards
    # LT pressed together with shot button B
    elif button_value == 1 and lt:
        if team:
            return h_penalties
        else:
            return a_penalties
    # LT pressed together with lob button X
    elif button_value == 2 and lt:
        if team:
            return h_subs
        else:
            return a_subs

    try:
        if team:  # true means home_team
            return home_data[button_value]
        else:  # false means away_team
            return away_data[button_value]
    except KeyError:  # pressed button_value which is not assign to textfield
        return None


def get_text_field_crosspad(crosspad_value: tuple, team) -> TextField:
    """return correct textfield object based on crosspad button and team_with_ball"""
    home_data = {(0, 1): h_corners, (-1, 0): h_goal_kicks,
                 (1, 0): h_free_kicks, (0, -1): h_throw_ins}

    away_data = {(0, 1): a_corners, (-1, 0): a_goal_kicks,
                 (1, 0): a_free_kicks, (0, -1): a_throw_ins}

    if team:  # true means home_team
        return home_data[crosspad_value]
    else:  # false means away_team
        return away_data[crosspad_value]


def get_bool_from_axis(l_axis, r_axis):
    """
    check both analog sticks
    left one is stronger(has advance) than the right one
    can return True, False or None
    """
    if abs(l_axis) > SENSITIVITY:  # left analog in action:
        if l_axis < SENSITIVITY:  # pointing upwards on y or right on x
            return True
        else:  # pointing downwards on y or left on x
            return False

    elif abs(r_axis) > SENSITIVITY:  # right analog in action:
        if r_axis < SENSITIVITY:  # pointing upwards on y or right on x
            return True
        else:  # pointing downwards on y or left on x
            return False

    else:  # no analog in action or low sensitivity on analog
        return None


def string_to_ms(string_time: str) -> int:
    """convert string to milliseconds"""
    mins, sec = string_time.split(":")
    mins = int(mins)
    sec = int(sec)
    ms = 60000 * mins + 1000 * sec
    return ms


def ms_to_sec(ms: int) -> int:
    return int(ms / 1000)


def sec_to_string(sec: int) -> str:
    mins, sec = divmod(sec, 60)
    return f"{mins:02d}:{sec:02d}"


def get_team(home_team: bool) -> Tuple[str, int, int]:
    if home_team:
        return HOME_TEAM, HOME_TEAM_ID, AWAY_TEAM_ID
    else:
        return AWAY_TEAM, AWAY_TEAM_ID, HOME_TEAM_ID


def save_to_list(team, ttype, time):
    """saving event data to list"""
    team_name, team_id, opp_team_id = get_team(team)
    if HOME_TEAM_LEFT_PITCH:
        left_side_team_id = HOME_TEAM_ID
        right_side_team_id = AWAY_TEAM_ID
    else:
        left_side_team_id = AWAY_TEAM_ID
        right_side_team_id = HOME_TEAM_ID

    try:
        type_id = ACTIONS_IDS[ttype]
    except KeyError:
        print(f'{ttype} not in db')
        return None

    if ttype in always_defending_side:
        if team_id == right_side_team_id:
            side = RIGHT_SIDE_ID
        elif team_id == left_side_team_id:
            side = LEFT_SIDE_ID
    elif ttype in always_attacking_side:
        if team_id == right_side_team_id:
            side = LEFT_SIDE_ID
        elif team_id == left_side_team_id:
            side = RIGHT_SIDE_ID
    else:  # action type can be on both sides
        if field_side is None:
            side = None  # save NULL to DB
        elif field_side:  # left side of the pitch
            side = LEFT_SIDE_ID
        else:  # right side of the pitch
            side = RIGHT_SIDE_ID

    match_time = ms_to_sec(time)  # in seconds to be saved in db
    human_game_time = sec_to_string(match_time)  # human-readable format
    video_time = match_time + GT_VT_DIFF  # in seconds
    human_video_time = sec_to_string(video_time)
    if first_half and match_time > HALF_TIME_DURATION:  # added time in first_half
        match_time = HALF_TIME_DURATION  # save to db as 45:00

    csv_template = (human_game_time, ttype, team_name,
                    GAME_ID, type_id, team_id, opp_team_id,
                    left_side_team_id, right_side_team_id, side,
                    match_time, video_time, human_video_time,
                    )
    print(csv_template)
    lines_to_save.append(csv_template)


def save_to_csv(lines):
    """saving event data from list to csv file"""
    with open('stats.csv', 'a+') as f:
        writer = csv.writer(f)
        writer.writerows(lines)


def end_app(unsaved_events):
    """save events and quit app"""
    save_to_csv(unsaved_events)  # save data
    unsaved_events.clear()
    pygame.quit()
    sys.exit()


pygame.init()

# SCREEN SETUP
WIDTH, HEIGHT = 1680, 752  # fit my display with space for terminal output
screen = pygame.display.set_mode((WIDTH, HEIGHT))
ws, hs = pygame.display.get_surface().get_size()
pygame.display.set_caption('Footac Controller')
FPS = 60
clock = pygame.time.Clock()

# SCREEN STATS-part
w = ws / 5  # use 20% for stats
h = hs  # use full height of screen

# SCREEN VIDEO-part
video_width = ws - w  # use 80% for video
video_height = video_width / 1.7777  # keep video ratio
video = Video(video_file)
video.set_size((video_width, video_height))
video.toggle_pause()  # pause video

# FONT SETUPS
FONT_SIZE = int(h / 50)  # 20
data_font = pygame.font.SysFont('arial', FONT_SIZE)
warning_font = pygame.font.SysFont('arial', FONT_SIZE * 3)
credits_font = pygame.font.SysFont('arial', int(FONT_SIZE * 0.9))
score_font = pygame.font.SysFont('Helvetica', int(FONT_SIZE * 1.7))
time_font = pygame.font.SysFont('Helvetica', FONT_SIZE * 2)
video_time_font = pygame.font.SysFont('Helvetica', int(FONT_SIZE * 0.9))

# JOYSTICK SETUP
SENSITIVITY = 0.2
active_joystick = None
JOY_ID = 0  # id of active joystick, it is usually the first joystick
# joystick is initialized in the main loop

# difference between game time and video time
if first_half:
    GT_VT_DIFF = ms_to_sec(string_to_ms(first_half_start_video_time))  # in sec
else:
    GT_VT_DIFF = ms_to_sec(string_to_ms(second_half_start_video_time)) \
                 - HALF_TIME_DURATION  # in sec
    # SWAP SIDES
    HOME_TEAM_LEFT_PITCH = not HOME_TEAM_LEFT_PITCH

# video player starting frame
video_time = string_to_ms(timer_start_at) // 1000 + GT_VT_DIFF  # in sec
video.seek(video_time)  # set frame

# PRINT BASIC INFORMATION to TERMINAL
print(f'PLaying first half: {first_half}')
print(f'GT_VT_DIFF:{sec_to_string(GT_VT_DIFF)}')
if HOME_TEAM_LEFT_PITCH:
    print(f'Home team {HOME_TEAM}, id:{HOME_TEAM_ID} is on the left')
    print(f'Away team {AWAY_TEAM}, id:{AWAY_TEAM_ID} is on the right')
else:
    print(f'Away team {AWAY_TEAM}, id:{AWAY_TEAM_ID} is on the left')
    print(f'Home team {HOME_TEAM}, id:{HOME_TEAM_ID} is on the right')

# CREATE BACKGROUND LAYOUT
# split screen into rectangles, width of each rect is 33.3% of total width
rect_1a = Rect(0, 0, w / 3, h / 5)  # height is 20% of total height
rect_2a = Rect(0, h / 5, w / 3, h / 4 * 3)  # 75%
rect_1b1 = Rect(w / 3, 0, w / 3, h / 10)  # 10%
rect_1b2 = Rect(w / 3, h / 10, w / 3, h / 10)  # 10%
rect_2b = Rect(w / 3, h / 5, w / 3, h / 4 * 3)  # 75%
rect_1c = Rect(w / 3 * 2, 0, w / 3, h / 5)  # 20%
rect_2c = Rect(w / 3 * 2, h / 5, w / 3, h / 4 * 3)  # 75%
# button rect is 100% width
rect_3a = Rect(0, h - h / 20, w, h / 20)  # 5%

# CREATE TEXT FIELDS(rectangles)
fw = w / 3  # field with
fh = h / 20  # field height

# LEFT COLUMN
h_score = TextField(Rect(0, 0, fw, fh * 2), score_font, cf.BLACK,
                    anchor='center',
                    action_type='goal')
h_name = TextField(Rect(0, 2 * fh, fw, fh * 2), data_font, cf.BLACK,
                   text=HOME_TEAM, anchor='center')
h_possession = TextField(Rect(0, 4 * fh, fw, fh), data_font, cf.BLACK, text=1)
h_shots = TextField(Rect(0, 5 * fh, fw, fh), data_font, cf.BLACK,
                    anchor='midright', action_type='shot')
h_passes = TextField(Rect(0, 6 * fh, fw, fh), data_font, cf.BLACK,
                     anchor='midright', action_type='pass')
h_lobs = TextField(Rect(0, 7 * fh, fw, fh), data_font, cf.BLACK,
                   anchor='midright', action_type='lob cross')
h_offsides = TextField(Rect(0, 8 * fh, fw, fh), data_font, cf.BLACK,
                       anchor='midright', action_type='offside')
h_corners = TextField(Rect(0, 9 * fh, fw, fh), data_font, cf.BLACK,
                      anchor='midright', action_type='corner')
h_throw_ins = TextField(Rect(0, 10 * fh, fw, fh), data_font, cf.BLACK,
                        anchor='midright', action_type='throw in')
h_free_kicks = TextField(Rect(0, 11 * fh, fw, fh), data_font, cf.BLACK,
                         anchor='midright', action_type='free kick')
h_goal_kicks = TextField(Rect(0, 12 * fh, fw, fh), data_font, cf.BLACK,
                         anchor='midright', action_type='goal kick')
h_fouls = TextField(Rect(0, 13 * fh, fw, fh), data_font, cf.BLACK,
                    anchor='midright', action_type='foul')
h_yell_cards = TextField(Rect(0, 14 * fh, fw, fh), data_font, cf.BLACK,
                         anchor='midright', action_type='yellow card')
h_red_cards = TextField(Rect(0, 15 * fh, fw, fh), data_font, cf.BLACK,
                        anchor='midright', action_type='red card')
h_subs = TextField(Rect(0, 16 * fh, fw, fh), data_font, cf.BLACK,
                   anchor='midright', action_type='substitution')
h_penalties = TextField(Rect(0, 17 * fh, fw, fh), data_font, cf.BLACK,
                        anchor='midright', action_type='penalty kick')
a18 = TextField(Rect(0, 18 * fh, fw, fh), data_font, cf.BLACK, text='',
                anchor='midright')

# MIDDLE COLUMN
i_time = TextField(Rect(w / 3, 0, fw, fh * 2), time_font, cf.BLACK,
                   text=timer_start_at)
i_l_side = TextField(Rect(w / 3, 1.5 * fh, fw / 2, fh * 2), video_time_font,
                     cf.LIGHT_BLACK, text='L')
i_r_side = TextField(Rect(w / 2, 1.5 * fh, fw / 2, fh * 2), video_time_font,
                     cf.LIGHT_BLACK, text='R')
v_time = TextField(Rect(w / 3, 2 * fh, fw, fh * 2), video_time_font,
                   cf.LIGHT_BLACK, text=sec_to_string(video_time))
i_video = TextField(Rect(w / 3, 2.3 * fh, fw, fh * 2), video_time_font,
                    cf.LIGHT_BLACK, text='*video time')
i_possession = TextField(Rect(w / 3, 4 * fh, fw, fh), data_font, cf.BLACK,
                         text='Possession')
i_shots = TextField(Rect(w / 3, 5 * fh, fw, fh), data_font, cf.BLACK,
                    text='Shots')
i_passes = TextField(Rect(w / 3, 6 * fh, fw, fh), data_font, cf.BLACK,
                     text='Passes')
i_lobs = TextField(Rect(w / 3, 7 * fh, fw, fh), data_font, cf.BLACK,
                   text='Lobs/Crosses')
i_offsides = TextField(Rect(w / 3, 8 * fh, fw, fh), data_font, cf.BLACK,
                       text='Offsides')
i_corners = TextField(Rect(w / 3, 9 * fh, fw, fh), data_font, cf.BLACK,
                      text='Corners')
i_throw_ins = TextField(Rect(w / 3, 10 * fh, fw, fh), data_font, cf.BLACK,
                        text='Throw ins')
i_free_kicks = TextField(Rect(w / 3, 11 * fh, fw, fh), data_font, cf.BLACK,
                         text='Free kicks')
i_goal_kicks = TextField(Rect(w / 3, 12 * fh, fw, fh), data_font, cf.BLACK,
                         text='Goal kicks')
i_fouls = TextField(Rect(w / 3, 13 * fh, fw, fh), data_font, cf.BLACK,
                    text='Fouls')
i_yell_cards = TextField(Rect(w / 3, 14 * fh, fw, fh), data_font, cf.BLACK,
                         text='Yellow cards')
i_red_cards = TextField(Rect(w / 3, 15 * fh, fw, fh), data_font, cf.BLACK,
                        text='Red cards')
i_subs = TextField(Rect(w / 3, 16 * fh, fw, fh), data_font, cf.BLACK,
                   text='Substitutions')
i_penalties = TextField(Rect(w / 3, 17 * fh, fw, fh), data_font, cf.BLACK,
                        text='Penalties')
b18 = TextField(Rect(w // 3, 18 * fh, fw, fh), data_font, cf.BLACK, text='')
i_help = TextField(Rect(w / 3, 19 * fh, fw, fh), credits_font, cf.LIGHT_BLACK,
                   text='To PAUSE/CONTINUE press ≡')

# RIGHT COLUMN
a_score = TextField(Rect(w / 3 * 2, 0, fw, fh * 2), score_font, cf.BLACK,
                    anchor='center', action_type='goal')
a_name = TextField(Rect(w / 3 * 2, 2 * fh, fw, fh * 2), data_font, cf.BLACK,
                   text=AWAY_TEAM, anchor='center', )
a_possession = TextField(Rect(w / 3 * 2, 4 * fh, fw, fh), data_font, cf.BLACK,
                         text=1, anchor='midleft')
a_shots = TextField(Rect(w / 3 * 2, 5 * fh, fw, fh), data_font, cf.BLACK,
                    anchor='midleft', action_type='shot')
a_passes = TextField(Rect(w / 3 * 2, 6 * fh, fw, fh), data_font, cf.BLACK,
                     anchor='midleft', action_type='pass')
a_lobs = TextField(Rect(w / 3 * 2, 7 * fh, fw, fh), data_font, cf.BLACK,
                   anchor='midleft', action_type='lob cross')
a_offsides = TextField(Rect(w / 3 * 2, 8 * fh, fw, fh), data_font, cf.BLACK,
                       anchor='midleft', action_type='offside')
a_corners = TextField(Rect(w / 3 * 2, 9 * fh, fw, fh), data_font, cf.BLACK,
                      anchor='midleft', action_type='corner')
a_throw_ins = TextField(Rect(w / 3 * 2, 10 * fh, fw, fh), data_font, cf.BLACK,
                        anchor='midleft', action_type='throw in')
a_free_kicks = TextField(Rect(w / 3 * 2, 11 * fh, fw, fh), data_font, cf.BLACK,
                         anchor='midleft', action_type='free kick')
a_goal_kicks = TextField(Rect(w / 3 * 2, 12 * fh, fw, fh), data_font, cf.BLACK,
                         anchor='midleft', action_type='goal kick')
a_fouls = TextField(Rect(w / 3 * 2, 13 * fh, fw, fh), data_font, cf.BLACK,
                    anchor='midleft', action_type='foul')
a_yell_cards = TextField(Rect(w / 3 * 2, 14 * fh, fw, fh), data_font, cf.BLACK,
                         anchor='midleft', action_type='yellow card')
a_red_cards = TextField(Rect(w / 3 * 2, 15 * fh, fw, fh), data_font, cf.BLACK,
                        anchor='midleft', action_type='red card')
a_subs = TextField(Rect(w / 3 * 2, 16 * fh, fw, fh), data_font, cf.BLACK,
                   anchor='midleft', action_type='substitution')
a_penalties = TextField(Rect(w / 3 * 2, 17 * fh, fw, fh), data_font, cf.BLACK,
                        anchor='midleft', action_type='penalty kick')
c18 = TextField(Rect(w / 3 * 2, 18 * fh, fw, fh), data_font, cf.BLACK, text='',
                anchor='midleft')

pause_game_field = TextField(Rect(0, 0, ws, ws), warning_font, cf.RED,
                             text='GAME PAUSED')

fields = {
    h_score, i_time, a_score,
    i_l_side, i_r_side,
    h_name, v_time, i_video, a_name,
    h_possession, i_possession, a_possession,
    h_shots, i_shots, a_shots,
    h_passes, i_passes, a_passes,
    h_lobs, i_lobs, a_lobs,
    h_offsides, i_offsides, a_offsides,
    h_corners, i_corners, a_corners,
    h_throw_ins, i_throw_ins, a_throw_ins,
    h_free_kicks, i_free_kicks, a_free_kicks,
    h_goal_kicks, i_goal_kicks, a_goal_kicks,
    h_fouls, i_fouls, a_fouls,
    h_yell_cards, i_yell_cards, a_yell_cards,
    h_red_cards, i_red_cards, a_red_cards,
    h_subs, i_subs, a_subs,
    h_penalties, i_penalties, a_penalties,
    a18, b18, c18,
    i_help,
}

# RENDER all text fields
for field in fields:
    field.render()

# GAME VARIABLES inside loop
team_with_ball = None  # {True: home_team, False: away_team, None: no team}
field_side = None  # {True: left side, False: right side, None: no data}
LT = False
RT = False
game_runs = False
game_time_passed = string_to_ms(timer_start_at)  # in ms
game_time = 0  # in ms
lines_to_save = []

# RUNNING APP MAIN LOOP
while True:
    pygame.draw.rect(screen, cf.GREEN1, rect_1a)
    pygame.draw.rect(screen, cf.GREEN2, rect_2a)
    pygame.draw.rect(screen, cf.SEA_GREEN, rect_3a)
    pygame.draw.rect(screen, cf.GREEN3, rect_1b1)
    pygame.draw.rect(screen, cf.GREEN2, rect_1b2)
    pygame.draw.rect(screen, cf.GREEN1, rect_2b)
    pygame.draw.rect(screen, cf.GREEN1, rect_1c)
    pygame.draw.rect(screen, cf.GREEN2, rect_2c)

    # ANALOG INPUTS
    if active_joystick and game_runs:

        if active_joystick.get_axis(2) > SENSITIVITY:  # hold LT
            LT = True
        else:
            LT = False

        if active_joystick.get_axis(5) > SENSITIVITY:  # hold RT
            RT = True
        else:
            RT = False

        left_analog_x = active_joystick.get_axis(0)
        left_analog_y = active_joystick.get_axis(1)
        right_analog_x = active_joystick.get_axis(3)
        right_analog_y = active_joystick.get_axis(4)

        # if upwards -> True -> home_team | downwards -> False -> away_team
        team_with_ball = get_bool_from_axis(left_analog_y, right_analog_y)

        # if right -> True -> right_side | left -> False -> left_side
        field_side = get_bool_from_axis(left_analog_x, right_analog_x)

    # USER INTERACTION
    for event in pygame.event.get():  # User did something.

        # HANDLE QUIT OF APP
        if event.type == QUIT:
            end_app(lines_to_save)
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:  # esc pressed
                end_app(lines_to_save)

        # HANDLE JOYSTICK connection/ disconnection
        if event.type == JOYDEVICEADDED:  # if joystick is connected
            joysticks = [pygame.joystick.Joystick(i) for i in
                         range(pygame.joystick.get_count())]
            for i, joystick in enumerate(joysticks):
                print(f'{joystick.get_name()} connected')
                if i == JOY_ID:
                    active_joystick = joystick

        if event.type == JOYDEVICEREMOVED:  # if joystick is disconnected
            print('Joystick disconnected')
            joysticks = [pygame.joystick.Joystick(i) for i in
                         range(pygame.joystick.get_count())]
            try:
                active_joystick = joysticks[JOY_ID]
            except IndexError:
                active_joystick = None
            team_with_ball = None

        # HANDLE USER(JOYSTICK) INPUT
        if event.type == JOYBUTTONDOWN:  # button is pressed

            if event.button == 10:  # middle button ≡ to PAUSE GAME
                game_runs = not game_runs
                if game_runs:  # continue counting time
                    start_time = pygame.time.get_ticks()
                    video.toggle_pause()
                else:  # pause counting time
                    game_time_passed += game_time
                    team_with_ball = None
                    video.toggle_pause()
                    save_to_csv(lines_to_save)  # save data
                    lines_to_save.clear()

            else:  # other buttons
                # print(f"Button {event.button} pressed.")
                if team_with_ball is not None:
                    field_to_update = get_text_field(event.button,
                                                     team_with_ball,
                                                     RT, LT)  # can return None
                    if field_to_update:
                        field_to_update.value += 1
                        field_to_update.render()

                        save_to_list(team_with_ball, field_to_update.type,
                                     total_game_time)

        if event.type == JOYHATMOTION:  # pressed cross-pad
            if team_with_ball is not None and event.value != (0, 0):
                field_to_update = get_text_field_crosspad(event.value,
                                                          team_with_ball)
                field_to_update.value += 1
                field_to_update.render()

                save_to_list(team_with_ball, field_to_update.type,
                             total_game_time)

    # RENDER TEAM NAMES
    if team_with_ball is None:
        h_name.render()
        a_name.render()
    elif team_with_ball:  # home team
        h_possession.value += 1
        h_name.render(color=cf.BLUE)
        a_name.render()
    else:  # away team
        a_possession.value += 1
        a_name.render(color=cf.BLUE)
        h_name.render()

    # RENDER field side, where is the balll
    if field_side is None:
        i_l_side.render()
        i_r_side.render()
    elif field_side:  # left side of the pitch
        i_l_side.render(color=cf.PINK)
        i_r_side.render()
    else:  # right side of the pitch
        i_l_side.render()
        i_r_side.render(color=cf.PINK)

    # RENDER POSSESSION:
    total_possession = h_possession.value + a_possession.value
    home_possession = round(h_possession.value / total_possession * 100)
    away_possession = 100 - home_possession
    h_possession.render(value=f'{home_possession} %')
    a_possession.render(value=f'{away_possession} %')

    # RENDER TIME
    if game_runs:  # count and display time in MM:SS
        game_time = pygame.time.get_ticks() - start_time
        total_game_time = game_time + game_time_passed  # in ms
        seconds = total_game_time // 1000
        i_time.render(value=sec_to_string(seconds))
        v_time.render(value=sec_to_string(seconds + GT_VT_DIFF))
    else:  # stop counting and show PAUSE
        pause_game_field.render()
        pause_game_field.draw(screen)

    # UPDATE DISPLAY
    for field in fields:
        field.draw(screen)
    video.draw(screen, (w, 0), force_draw=False)
    pygame.display.update()
    clock.tick(FPS)
