# Footac Gamepad

Use Xbox Controller to tag and save events from football game.

## Why I create this project?

As my hobby I occasionally record amateur football games. By video-edit is handy to have some extra info about the game
events, like number of shots or fouls for each team. Data-companies are collecting these statistics for professional
leagues, but from obvious reasons not for amateur leagues. I used pen or paper for this purpose , but after learning
basic concepts of programming I decide to create a program which can help me to get this data from any game by watching
it just once with gamepad in my hand.

## How it works?

Have you ever played FIFA on any gaming console? So imagine you don't control the game, you're just pressing the
buttons, depending on actions of the game. If player on the screen shoot , you press 'shot' button. If home team has a
ball, I point analog joystick to one direction. If away team has a ball I point it to opposite direction. My programm
reads input data from xbox controller, show it on screen during a game and save it to csv file for later usage.

## Can I use it?

I create this only for my own purpose. At the moment it is tested only on my Macbook with Microsoft Xbox controller
model 1708. If you find this idea useful, have no concerns to use my program or create your own. With help
of [pygame](https://www.pygame.org/docs/ref/joystick.html) you can create it for other controllers or even keyboard.

## Will you improve it?

This is just side project for other bigger project. It helps me get the data I need. I have ideas how to improve the
visual side of the project as well as saving and editing data live. I cooperate with one football so based on their
feedback more changes can be applied.


## Run play.py

It's necessary to have access to video file through your OS. This program can not open files from remote directories. I
personally use mp4 files, no other video files are tested.
The video should be full length of the game for the best results, otherwise you can miss some actions and game_time will
not be real.

##### Before start please update variables in config/game_setup.py:

* HALF_TIME_DURATION = keep 2700 seconds, for regular 45 minutes game, for kids games with shorter period, please adjust
* video_file = path to your file
* HOME_TEAM = name of home team displayed on the screen
* AWAY_TEAM = name of away team displayed on the screen

* GAME_ID = from your DB
* HOME_TEAM_ID = from your DB
* AWAY_TEAM_ID = from your DB
* HOME_TEAM_LEFT_PITCH = True if home team start at the beginning of the game on the left recorded side of the pitch, otherwise False
* first_half_start_video_time = 'MM:SS' # at what time first half start in your video file
* second_half_start_video_time = 'MM:SS' # at what time second half start in your video file
* first_half = True/False
* timer_start_at = 'MM:SS' # 00:00 for first half, 45:00 for second half, or you can start the timer anytime you want

When first half is done, run program again. Don't change all setup, but you need to adjust
first_half and timer_start_at for sure.

 ###### WARNING: By re-running the program, all data from screen will be set to 0. All is in saved csv except possessions.

After you run play.py new pygame window will open. On left side on your screen you will see current statistics of the game and on the right is place the video file. Video will be open at timeframe based on your setup timer_start_at and will see it as soon you start a game.
Program window is not resizable during running of the program at the moment, it is created to fit my needs. If you need to adjust it you need to change WIDTH and HEIGHT variables in screen setup part.


##### Controls



##### Saving data
Every time you press pause button, program save data to csv file in your directory. The csv_template is created for my own needs. In save_to_list() method under csv_template  variable you can remove fields, which you don't want to save to csv. Or just keep it and don't worry about the csv at all :-)
