# Footac Gamepad

Use Xbox Controller to tag and save events from football game.

## Why I created this project?

As my hobby I occasionally record amateur football games. By video-edit is handy to have some extra info about the game
events, like number of shots or fouls for each team. Data-companies are collecting these statistics for professional
leagues, but from obvious reasons not for amateur leagues. I used pen or paper for this purpose , but after learning
basic concepts of programming I decided to create a program which can help me to get this data from any game by watching
it just once with gamepad in my hand.

## How it works?

Have you ever played FIFA on any gaming console? So imagine you don't control the game, you're just pressing the
buttons, depending on actions of the game. If player on the screen shoots, you press 'shot' button. If home team has a
ball, I point analog joystick to one direction. If away team has a ball I point it to opposite direction. My program
reads input data from xbox controller, shows it on screen during a game and saves it to csv file for later usage.
<img src="images/full program.png" width="980">

## Can I use it?

I create this only for my own purposes. At the moment it is tested only on my Macbook with Microsoft Xbox controller
model 1708. If you find this idea useful, have no concerns to use my program or create your own. With help
of [pygame](https://www.pygame.org/docs/ref/joystick.html) you can create it for other controllers or even keyboard.

## Will you improve it?

This is just side project for my other bigger project called [Footac](https://github.com/OndrejPech/Footac). It helps me get the data I need. I have ideas how to improve the
visual side of the project as well as saving and editing data live. More changes can be applied through cooperation with football teams in the future.


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

After you run play.py new pygame window will open. On left side on your screen you will see current statistics of the game and on the right site there is a video file. Video will be opened at timeframe based on your setup timer_start_at and will see it as soon as you start a game.
Program window is not resizable during running of the program at the moment, it is created to fit my needs. If you need to adjust it you need to change WIDTH and HEIGHT variables in screen setup part.


##### Controls
<img src="images/controller front.jpg" width="400">  <img src="images/controller back.jpg" width="400"> 

After running program you see confirmation in terminal window that your controller is connected. If not please connect it to your PC/MAC.


Use joystick(1) horizontal movement to choose which side of the field is the action taking on
* moving left means action is on left side and L lights on the stats screen
* moving right means action is on right side and R lights on the stats screen

Use joystick(1) vertical movement to choose which team is in possession
* moving up means home team is in possession and HOME_TEAM_NAME lights on the stats screen
* moving down means away team is in possession and AWAY_TEAM_NAME lights on the stats screen

| xbox BUTTON | button number | ACTION        |
|:-----------:|:-------------:|:--------------|
|      ≡      |       6       | start / pause |
|      A      |       A       | ground pass   |
|      X      |       X       | air pass      |
|      B      |       B       | shot          |
|      Y      |       Y       | foul          |
|   Y + LT    |    Y + 14     | yellow card   |
|   Y + RT    |    Y + 11     | red card      |
|   B + LT    |    B + 14     | penalty       |
|      ↓      |      8 ↓      | goal kick     |
|      →      |      8 →      | free kick     |
|      ↑      |      8 ↑      | corner        |
|      ←      |      8 ←      | throw in      |
|     LB      |       2       | offside       |
|     RB      |       7       | goal          |
|   X + LT    |    X + LT     | substitution  |

joystick has to be either up for home team or down for away team when you press any action button. If no team is chosen, action is not recorded.

##### Saving data
Every time you press pause button ≡, program saves data to csv file in your directory. The csv_template is created for my own needs. In save_to_list() method under csv_template  variable you can remove fields, which you don't want to save to csv. Or just keep it and don't worry about the csv at all :-)
