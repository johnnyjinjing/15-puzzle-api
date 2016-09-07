#Full Stack Nanodegree Project 4 -- The Fifteen Puzzle Game

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's running by visiting the API Explorer - by default `localhost:8080/_ah/api/explorer`. The datastore can be accessed at `http://localhost:8000/datastore`
1.  (Optional) Generate your client library(ies) with the endpoints tool. Deploy your application.

##Game Description:
The 15-puzzle (also called Gem Puzzle, Boss Puzzle, Game of Fifteen, Mystic Square and many others) is a sliding puzzle that consists of a frame of numbered square tiles in random order with one tile missing. The object of the puzzle is to place the tiles in order (see diagram) by making sliding moves that use the empty space.

Many different 15-puzzle games can be played by many different Users at any given time. Each game can be retrieved or played by using the path parameter `urlsafe_game_key`.

Score of each player is calculated by the total game they finished and won. The rank of the player is based on the minimum number of moves he/she used to finish a game.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a random new Game. user_name provided must correspond to an existing user - will raise a NotFoundException if not.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: POST
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Cancel the game. Game is marked finished, and player lose the game. If the game is already completed an error will be thrown.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, move direction
    - Returns: GameForm with new game state.
    - Description: Accepts a move and returns the updated state of the game. If this causes a game to end, a corresponding Score entity will be created.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history''
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage containing history
    - Description: Returns the move history of a game as a stringified list.

 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms with 1 or more GameForm inside.
    - Description: Returns the current state of all the User's active games.

 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered). Will raise a NotFoundException if the User does not exist.

- **get_high_scores**
    - Path: 'highestscores'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Rank all players that have played at least one game by game won.

- **get_user_rankings**
    - Path: 'ranking'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Rank all players that have played at least one game by their minimum move.

##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address, the game played, won, and minimum move.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state.
 - **GameForms**
    - Container for one or more GameForm.
 - **NewGameForm**
    - Used to create a new game.
 - **MakeMoveForm**
    - Inbound make move form.
 - **ScoreForm**
    - Representation of a completed game's Score.
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserForm**
    - Representation of User.
 - **UserForms**
    - Container for one or more UserForm.
 - **StringMessage**
    - General purpose String container.