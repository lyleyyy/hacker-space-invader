from a3_support import *
import tkinter as tk
import random
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import filedialog

class Entity:
    """Entity is an abstract class that is used to represent any element
    that can appear on the game’s grid."""
    def display(self):
        """Return the character used to represent this entity in a
        text-based grid."""
        raise NotImplementedError

    def __repr__(self) -> str:
        """Return a representation of this entity."""
        return f'{self.__class__.__name__}()'

class Player(Entity):
    """A subclass of Entity representing a Player within the game."""
    def display(self) -> str:
        """Return the character representing a player: ’P’"""
        return PLAYER

class Destroyable(Entity):
    """A subclass of Entity representing a Destroyable within the game.
    A destroyable can be destroyed by the player but not collected."""
    def display(self):
        """Return the character representing a destroyable: ’D’"""
        return DESTROYABLE

class Collectable(Entity):
    """A subclass of Entity representing a Collectable within the game.
    A collectable can be destroyed or collected by the player."""
    def display(self):
        """Return the character representing a collectable: ’C’"""
        return COLLECTABLE

class Blocker(Entity):
    """A subclass of Entity representing a Blocker within the game.
    A blocker cannot be destroyed or collected by the player."""
    def display(self):
        """Return the character representing a blocker: ’B’"""
        return BLOCKER

class Bomb(Entity):
    """A subclass of Entity representing a Bomb within the game that
    player’s can destroy other entities with.
    A bomb removes all entities within a ‘splash damage’ radius.
    The SPLASH constant refers to the specific offsets.
    A bomb can be destroyed but cannot be collected."""
    def display(self):
        """Return the character representing a bomb: ’B’"""
        return BOMB

class Grid:
    """The Grid class is used to represent the 2D grid of entities.
    The top left position of the grid is indicated by (0, 0)."""
    def __init__(self, size: int) -> None:
        """A grid is constructed with a size representing the number of
        rows (equal to the number of columns) in the grid.
        Entities should be stored in a dictionary. Initially a grid does
        not contain any entities."""
        self._size = size
        self._entities = {}

    def get_size(self) -> int:
        """Return the size of the grid."""
        return self._size

    def add_entity(self, position: Position, entity: Entity) -> None:
        """Add a given entity into the grid at a specified position.
        This entity is only added if the position is valid.
        If an entity already exists at the specified position, this method will
        replace the current entity at the specified position.

        Parameters:
            position: Position,
            the Position class in support.py

            entity: Entity,
        """
        if isinstance(entity, Player):
            self._entities[position] = entity

        elif self.in_bounds(position):
            self._entities[position] = entity

    def get_entities(self) -> Dict[Position, Entity]:
        """Return the dictionary containing grid entities.
        Updating the returned dictionary should have no side-effects.

        return:
            Dict in format: {Position:Entity}
        """
        return self._entities

    def get_entity(self, position: Position) -> Optional[Entity]:
        """Return a entity from the grid at a specific position or None if
        the position does not have a mapped entity."""
        return self.get_entities().get(position)

    def remove_entity(self, position: Position) -> None:
        """Remove an entity from the grid at a specified position."""
        if position in self.get_entities():
            self._entities.pop(position)

    def serialise(self) -> Dict[Tuple[int, int], str]:
        """Convert dictionary of Position and Entities into a simplified,serialised
        dictionary mapping tuples to characters, and return this serialised mapping.

        return:
            Dict in format: {Tuple(int, int):str}
        """
        return {(position.get_x(), position.get_y()):entity.display() for position, entity in self.get_entities().items()}

    def in_bounds(self, position: Position) -> bool:
        """Return a boolean based on whether the position is valid in terms of
        the dimensions of the grid."""
        return 0 <= position.get_x() < self.get_size() and 1 <= position.get_y() < self.get_size()

    def __repr__(self) -> str:
        """Return a representation of this Grid."""
        return f'Grid({self.get_size()})'

class Game:
    """The Game handles the logic for controlling the actions of the entities within the grid."""
    def __init__(self, size: int) -> None:
        """A game is constructed with a size representing the dimensions of the playing grid.
        A game should be constructed with at least the following variable:"""
        self._size = size
        self._grid = Grid(size)
        self._player_position = Position(GRID_SIZE//2,0)
        self._num_collected = 0
        self._num_destroyed = 0
        self._total_shots = 0
        self._won_or_lose = None

    def get_grid(self) -> Grid:
        """Return the instance of the grid held by the game."""
        return self._grid

    def get_player_position(self) -> Position:
        """Return the position of the player in the grid (top row, centre column).
        This position should be constant."""
        return self._player_position

    def get_num_collected(self) -> int:
        """Return the total of Collectables acquired."""
        return self._num_collected

    def get_num_destroyed(self) -> int:
        """Return the total of Destroyables removed with a shot."""
        return self._num_destroyed

    def get_total_shots(self) -> int:
        """Return the total of shots taken."""
        return self._total_shots

    def rotate_grid(self, direction: str) -> None:
        """Rotate the positions of the entities within the grid depending on
        the direction they are being rotated."""
        rotated_entities = {}
        offset_tuple = ROTATIONS[DIRECTIONS.index(direction)]
        offset_position = Position(offset_tuple[0], offset_tuple[1])

        for position, entity in self.get_grid().get_entities().items():
            if isinstance(entity, Player):
                rotated_entities[position] = entity

            else:
                rotated_position = position.add(offset_position)
                if rotated_position.get_x() > 6:
                    rotated_position._x = 0

                elif rotated_position.get_x() < 0:
                    rotated_position._x = 6

                rotated_entities[rotated_position] = entity

        self._grid._entities = rotated_entities

    def create_entity(self, display: str) -> Entity:
        """Uses a display character to create an Entity. Raises a NotImplementedError
        if the character parsed into as the display is not an existing Entity."""
        if display == PLAYER:
            return Player()

        elif display == COLLECTABLE:
            return Collectable()

        elif display == DESTROYABLE:
            return Destroyable()

        elif display == BLOCKER:
            return Blocker()

        elif display == BOMB:
            return Bomb()

        else:
            raise NotImplementedError

    def generate_entities(self) -> None:
        """
        Method given to the students to generate a random amount of entities to
        add into the game after each step
        """
        # Generate amount
        entity_count = random.randint(0, self.get_grid().get_size() - 3)
        entities = random.choices(ENTITY_TYPES, k=entity_count)

        # Blocker in a 1 in 4 chance
        blocker = random.randint(1, 4) % 4 == 0

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        if TASK == 3:
            bomb = False
            if not blocker:
                bomb = random.randint(1, 4) % 4 == 0

        total_count = entity_count
        if blocker:
            total_count += 1
            entities.append(BLOCKER)

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        if TASK == 3:
            if bomb:
                total_count += 1
                entities.append(BOMB)

        entity_index = random.sample(range(self.get_grid().get_size()),
                                     total_count)

        # Add entities into grid
        for pos, entity in zip(entity_index, entities):
            position = Position(pos, self.get_grid().get_size() - 1)
            new_entity = self.create_entity(entity)
            self.get_grid().add_entity(position, new_entity)

    def step(self) -> None:
        """Moves all entities on the board by an offset of (0, -1)."""
        steped_entities = {}

        for position, entity in self.get_grid().get_entities().items():
            if isinstance(entity, Player):
                steped_entities[position] = entity

            else:
                steped_position = position.add(Position(0,-1))

                if steped_position.get_y() < 1 and isinstance(entity, Destroyable):
                    self._won_or_lose = False

                elif steped_position.get_y() >= 1:
                    steped_entities[steped_position] = entity

        self._grid._entities = steped_entities
        self.generate_entities()

    def fire(self, shot_type: str) -> None:
        """Handles the firing/collecting actions of a player towards an entity
        within the grid.

        Parameter:
            shot_type: str,
            shot_type refers to whether a collect or destroy shot has been fired
            (refer to Entity descriptions for how different entities react to
            being hit by different types).
        """
        self._total_shots += 1
        x = self.get_player_position().get_x()
        for y in range(1, self.get_grid().get_size()):
            target_position = Position(x, y)
            target_entity = self.get_grid().get_entity(target_position)

            if isinstance(target_entity, Blocker):
                break

            elif isinstance(target_entity, (Collectable, Destroyable, Bomb)):
                if shot_type == COLLECT:
                    if isinstance(target_entity, Collectable):
                        self.get_grid().remove_entity(target_position)
                        self._num_collected += 1
                        if self.get_num_collected() >= COLLECTION_TARGET:
                            self._won_or_lose = True
                            break
                        break

                    else:
                        break

                elif shot_type == DESTROY:
                    if isinstance(target_entity, Collectable):
                        self.get_grid().remove_entity(target_position)
                        break

                    elif isinstance(target_entity, Destroyable):
                        self.get_grid().remove_entity(target_position)
                        self._num_destroyed += 1
                        break

                    elif isinstance(target_entity, Bomb):
                        self.get_grid().remove_entity(target_position)
                        self._num_destroyed += 1

                        for x,y in SPLASH:
                            splash_offset = Position(x,y)
                            splashed_position = target_position.add(splash_offset)
                            if isinstance(self.get_grid().get_entity(splashed_position), Destroyable):
                                self._num_destroyed += 1

                            if not isinstance(self.get_grid().get_entity(splashed_position), Player):
                                self.get_grid().remove_entity(splashed_position)
                        break

    def has_won(self) -> bool:
        """Return True if the player has won the game."""
        return self._won_or_lose

    def has_lost(self) -> bool:
        """Returns True if the game is lost (a Destroyable has reached the top row)."""
        return self._won_or_lose

class AbstrackField(tk.Canvas):
    def __init__(self, master, rows: int, cols: int, width: int, height: int, **kwargs):
        """AbstractField is an abstract view class which inherits from tk.Canvas
        and provides base functionality for other view classes. An AbstractField
        can be thought of as a grid with a set number of rows and columns, which
        supports creation of text at specific positions based on row and column.
        The number of rows may differ from the number of columns, and the cells
        may be non-square.

        Parameters:
            master: master,
            The parent window

            rows: int,
            The rows of the grid

            cols: int,
            The cols of the grid

            width: int(in this assignment),
            The width in pixels, inherits from tk.Canvas

            height: int(in this assignment),
            The height in pixels, inherits from tk.Canvas

            **kwargs:
            Signifies that any additional named arguments supported by tk.Canvas
            should also be supported by this class.
        """
        super().__init__(master, width=width, height=height, **kwargs)

        self._master = master
        self._rows = rows
        self._cols = cols
        self._cell_width = width/cols
        self._cell_height = height/rows

    def get_bbox(self, position: Position) -> Tuple:
        """Returns the bounding box for the position; this is a tuple containing
        information about the pixel positions of the edges of the shape,
        in the form (x_min, y_min, x_max, y_max).

        Paramters:
            position: Position,
            the Position class

        return:
            Tuple(int, int, int, int)
        """
        x_min, y_min = position.get_x()*self._cell_width, position.get_y()*self._cell_height
        x_max, y_max = (position.get_x()+1)*self._cell_width, (position.get_y()+1)*self._cell_height
        return (x_min, y_min, x_max, y_max)

    def pixel_to_position(self, pixel: Tuple) -> Position:
        """Converts the (x, y) pixel position (in graphics units) to a (row, column) position.

        Parameter:
            pixel: Tuple(int/float, int/float),
            The pixel position in graphics units

        return: An instance of Position class
        """
        pixel_x, pixel_y = pixel[0], pixel[1]
        x, y = pixel_x//self._cell_width, pixel_y//self._cell_height
        return Position(x, y)

    def get_position_center(self, position: Position) -> Tuple:
        """Gets the graphics coordinates for the center of the cell at the given (row, column) position.

        Parameter:
            position: Position,

        return: Tuple(int/float, int/float)
        """
        x_min, y_min, x_max, y_max = self.get_bbox(position)
        x, y = (x_min+x_max)/2, (y_min+y_max)/2
        return (x, y)

    def annotate_position(self, position: Position, text: str) -> None:
        """Annotatesthecenterofthecellatthegiven (row, column) position with the provided text."""
        center = self.get_position_center(position)
        self.create_text(center[0], center[1], text=text)

class GameField(AbstrackField):
    """GameField is a visual representation of the game grid which inherits from
    AbstractField. Entities are drawn on the map using coloured rectangles at
    different (row, column) positions."""
    def __init__(self, master, size: int, width: int, height: int, **kwargs):
        """The size parameter is the number of rows (= number of columns) in the grid,
        width and height are the width and height of the grid (in pixels).

        Parameters:
            master: master,
            The parent window

            size: int,
            The rows and cols of the grid, size=rows=cols

            width: int(in this assignment),
            The width in pixels, inherits from AbstrackField, equal in tk.Canvas

            height: int(in this assignment),
            The height in pixels, inherits from AbstrackField, equal in tk.Canvas

            **kwargs:
            Signifies that any additional named arguments supported by tk.Canvas
            should also be supported by this class.
        """
        super().__init__(master, rows=size, cols=size, width=width, height=height, **kwargs)
        self._master = master
        self._size = size

    def draw_grid(self, entities: Dict[Position, Entity]) -> None:
        """Draws the entities (found in the Grid’s entity dictionary) in the game
        grid at their given position using a coloured rectangle with superimposed
        text identifying the entity (this includes the Player entity).

        Parameter:
            entities: Dict[Position, Entity],
            The dictionary of all entities from instance of Grid class.
        """
        self.delete(tk.ALL)

        for position, entity in entities.items():
            x_min, y_min, x_max, y_max = self.get_bbox(position)
            self.create_rectangle(x_min, y_min, x_max, y_max, fill=COLOURS[entity.display()])
            self.annotate_position(position, entity.display())

    def draw_player_area(self) -> None:
        """Draws the grey area a player is placed on."""
        self.create_rectangle(0, 0, (MAP_WIDTH//GRID_SIZE*3), (MAP_WIDTH//GRID_SIZE*1), fill=PLAYER_AREA)
        self.create_rectangle((MAP_WIDTH//GRID_SIZE*4), 0, MAP_WIDTH, (MAP_WIDTH//GRID_SIZE*1), fill=PLAYER_AREA)

class ScoreBar(AbstrackField):
    """ScoreBar is a visual representation of shot statistics from the player which inherits from AbstractField."""
    def __init__(self, master, rows: int, **kwargs):
        """rows is the number of rows contained in the ScoreBar canvas.
        This should match the size of the grid. By default, columns should be set to 2.

        Parameters:
            master: master,
            The parent window

            rows: int,
            The rows of this score bar

            **kwargs:
            Signifies that any additional named arguments supported by tk.Canvas
            should also be supported by this class.
        """
        super().__init__(master, rows=rows, cols=2, width=SCORE_WIDTH, height=MAP_HEIGHT, **kwargs)
        self.create_text(SCORE_WIDTH/2, MAP_HEIGHT/GRID_SIZE/2, text="Score", fill="white", font=TITLE_FONT)
        self.create_text(SCORE_WIDTH/4, MAP_HEIGHT/GRID_SIZE*1.5, text="Collected: ", fill="white")
        self.create_text(SCORE_WIDTH/4, MAP_HEIGHT/GRID_SIZE*2.5, text="Destroyed: ", fill="white")

class HackerController:
    """HackerController acts as the controller for the Hacker game."""
    def __init__(self, master, size: int):
        """The parameter master represents the master window and size represents
        the number of rows (equal to columns) in the game map. The title label,
        Game Model, Game Field, Scorebar and game's step will be initialized here."""
        self._master = master
        self._size = size
        self._master.bind("<Key>", self.handle_keypress)
        self._master.after(2*1000, self.step)

        # initialize the game mode and store its grid including initializing the player entity
        self._game = Game(self._size)
        grid = self._game.get_grid()
        grid.add_entity(Position(GRID_SIZE//2,0), Player())

        # draw the hacker title using Label
        self._hacker_lbl = tk.Label(self._master, text=TITLE, bg=TITLE_BG, font=TITLE_FONT, fg="white")
        self._hacker_lbl.pack(side=tk.TOP, fill=tk.BOTH)

        # create a frame to contain game field and score bar
        self._frame = tk.Frame(self._master)
        self._frame.pack(side=tk.TOP)

        # initialize and draw the game field, and it is in the frame:
        self._game_field = GameField(self._frame, self._size, MAP_WIDTH, MAP_HEIGHT, bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT)
        self._game_field.draw_grid(grid.get_entities())
        self._game_field.draw_player_area()

        # initialize and draw the score bar, and it is in the frame:
        self._score_bar = ScoreBar(self._frame, self._size, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.LEFT)

        self._text_id_1 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*1.5, text=self._game.get_num_collected(), fill="white")
        self._text_id_2 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*2.5, text=self._game.get_num_destroyed(), fill="white")

    def handle_keypress(self, event) -> None:
        """This method should be called when the user presses any key during the game.
        It must handle error checking and event calling and execute methods to update
        both the model and the view accordingly.

        Parameter:
            event: tkinter event,
        """
        if event.keysym in [LEFT, RIGHT, LEFT.lower(), RIGHT.lower()]:
            self.handle_rotate(event.keysym.upper())

        elif event.keysym.upper() in [COLLECT, DESTROY]:
            self.handle_fire(event.keysym.upper())

    def draw(self, game: Game) -> None:
        """Clears and redraws the view based on the current game state.

        Parameter:
            game: Game,
            An instance of the Game class
        """
        # draw a new game field
        self._game_field.draw_grid(game.get_grid().get_entities())
        self._game_field.draw_player_area()

        # for the score, delete the previous score number and draw the new one
        self._score_bar.delete(self._text_id_1)
        self._score_bar.delete(self._text_id_2)

        self._text_id_1 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*1.5, text=self._game.get_num_collected(), fill="white")
        self._text_id_2 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*2.5, text=self._game.get_num_destroyed(), fill="white")

    def handle_rotate(self, direction: str) -> None:
        """Handles rotation of the entities and redrawing the game. It may be
        easiest for the handle_keypress method to call handle_rotate with the
        relevant arguments.

        Parameter:
            direction: str,
        """
        self._game.rotate_grid(direction)
        self.draw(self._game)

    def handle_fire(self, shot_type: str) -> None:
        """Handles the firing of the specified shot type and redrawng of the game.
        It may be easiest for the handle_keypress method to call handle_fire with
        the relevant arguments."""
        self._game.fire(shot_type)
        self.draw(self._game)

    def step(self):
        """This method is called every 2 seconds and triggers the step method for
        the game and updates the view accordingly."""
        self._game.step()
        self.draw(self._game)

        # controll the game and messagebox by win or lost
        if self._game.has_won() is None:
            pass

        elif self._game.has_won():
            if messagebox.showinfo("WIN", "Congratulation! You Win!"):
                self._master.destroy()

        elif not self._game.has_lost():
            if messagebox.showinfo("LOSE", "Sorry! You Lost!"):
                self._master.destroy()
        
        # recursive
        self._master.after(2*1000, self.step)

class ImageGameField(GameField):
    """ImageGameField extends the existing GameField class and behaves similarly
    to GameField, except that images should be used to display each square."""
    def __init__(self, master, size: int, width: int, height: int, **kwargs):
        """The size parameter is the number of rows (= number of columns) in the grid,
        width and height are the width and height of the grid (in pixels).

        Parameters:
            master: master,
            The parent window

            size: int,
            The rows and cols of the grid, size=rows=cols

            width: int(in this assignment),
            The width in pixels, inherits from AbstrackField, equal in tk.Canvas

            height: int(in this assignment),
            The height in pixels, inherits from AbstrackField, equal in tk.Canvas

            **kwargs:
            Signifies that any additional named arguments supported by tk.Canvas
            should also be supported by this class.
        """
        super().__init__(master, size, width, height, **kwargs)
        self._master = master
        self._size = size
        self._images = []

    def draw_grid(self, entities: Dict[Position, Entity]) -> None:
        """Draws the entities (found in the Grid’s entity dictionary) in the game
        grid at their given position using respective image identifying the entity
        (this includes the Player entity).

        Parameter:
            entities: Dict[Position, Entity],
            The dictionary of all entities from instance of Grid class.
        """
        self.delete(tk.ALL)

        # if draw_player_area in AdvanceHackerControll, the player image will be covered, or the area be covered
        self.draw_player_area()

        for position, entity in entities.items():
            center = self.get_position_center(position)
            image = ImageTk.PhotoImage(Image.open(f'images/{IMAGES[entity.display()]}'))
            self._images.append(image)
            self.create_image(center[0], center[1], image=image)

    def draw_player_area(self) -> None:
        """Draws the grey area a player is placed on."""
        self.create_rectangle(0, 0, (MAP_WIDTH//GRID_SIZE*7), (MAP_HEIGHT//GRID_SIZE*1), fill=PLAYER_AREA)

class AdvancedHackerController(HackerController):
    """AdvancedHackerController extends the functionality of HackerController."""
    def __init__(self, master, size: int):
        """The parameter master represents the master window and size represents
        the number of rows (equal to columns) in the game map. The title label,
        Game Model, Game Field, Scorebar, Statusbar and game's step will be initialized here."""
        self._master = master
        self._size = size
        self._master.bind("<Key>", self.handle_keypress)
        self._master.after(2*1000, self.step)

        self._timer_m = 0
        self._timer_s = 0

        # initialize the game mode and store its grid including initializing the player entity
        self._game = Game(self._size)
        grid = self._game.get_grid()
        grid.add_entity(Position(GRID_SIZE//2,0), Player())

        # draw the hacker title using Label
        self._hacker_lbl = tk.Label(self._master, text=TITLE, bg=TITLE_BG, font=TITLE_FONT, fg="WHITE")
        self._hacker_lbl.pack(side=tk.TOP, fill=tk.BOTH)
        
        # create a frame to contain game field and score bar
        self._frame = tk.Frame(self._master)
        self._frame.pack(side=tk.TOP)

        # initialize and draw the image game field, and it is in the frame:
        self._game_field = ImageGameField(self._frame, self._size, MAP_WIDTH, MAP_HEIGHT, bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT)
        self._game_field.draw_grid(grid.get_entities())

        # initialize and draw the score bar, and it is in the frame:
        self._score_bar = ScoreBar(self._frame, self._size, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.LEFT)

        self._text_id_1 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*1.5, text=self._game.get_num_collected(), fill="white")
        self._text_id_2 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*2.5, text=self._game.get_num_destroyed(), fill="white")

        # initialize StatusBar
        self._status_bar = StatusBar(self._master, self.update_timer)
        self._status_bar.pack(side=tk.TOP)

        if self._status_bar.get_pause_or_play():
            self._master.after(1*1000, self.update_timer)

        # initialize the file menu
        self._file_menu = FileMenu(self._master, self.new_game, self.save_game, self.load_game)
        self._master.config(menu=self._file_menu)

    def new_game(self) -> None:
        """This method initializes a new game and apply it to current game."""
        # create an new empty game mode
        self._game = Game(self._size)

        # initialize the player and draw the image game field, including the collected, destroyed and total shots.
        self._game.get_grid().add_entity(Position(GRID_SIZE//2,0), Player())
        self.draw(self._game)

        # initialize the timer and pause/play button.
        self._status_bar._timer.config(text=f"0m 0s")
        self._status_bar._pause_or_play = True
        self._status_bar._pause_play_button.config(text="Pause")

    def save_game(self) -> None:
        """This method saves the current game status including the timer, total shots,
        number of collected and destroyed, and the entitis' current position into
        a nominated directory."""
        # directory = tk.filedialog.askdirectory()
        # with open(f"{directory}/save_game.txt", "w") as file:
        with open(f"director_test_game_save.save", "w") as file:
            file.write(f'time_m@{self._timer_m}')
            file.write(f'\ntime_s@{self._timer_s}')
            file.write(f'\ntotal_shots@{self._game.get_total_shots()}')
            file.write(f'\ncollected@{self._game.get_num_collected()}')
            file.write(f'\ndestroyed@{self._game.get_num_destroyed()}')
            file.write(f'\nentities@{self._game.get_grid().get_entities()}')

    def load_game(self) -> None:
        """This method loads the saved game file and apply it to current game."""
        file = tk.filedialog.askopenfile()

        # store the saved game information in a dict
        saved_game_info = {}
        for line in file:
            key, value = line.split("@")
            saved_game_info[key] = value.strip()
        file.close()

        # load the saved data of timer and apply them to current game
        self._timer_m = int(saved_game_info["time_m"])
        self._timer_s = int(saved_game_info["time_s"])
        self._status_bar._timer.config(text=f"{self._timer_m}m {self._timer_s}s")

        # load the saved data of total shots, collected, destroyed
        self._game._total_shots = int(saved_game_info["total_shots"])
        self._game._num_collected = int(saved_game_info["collected"])
        self._game._num_destroyed = int(saved_game_info["destroyed"])

        # load the saved data of entities
        self._game.get_grid()._entities = eval(saved_game_info["entities"])

        # apply loaded data to current game
        self.draw(self._game)

    def draw(self, game: Game) -> None:
        """Clears and redraws the view based on the current game state."""
        # draw a new image game field
        self._game_field.draw_grid(game.get_grid().get_entities())

        # for the score, delete the previous score number and draw the new one
        self._score_bar.delete(self._text_id_1)
        self._score_bar.delete(self._text_id_2)

        self._text_id_1 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*1.5, text=self._game.get_num_collected(), fill="white")
        self._text_id_2 = self._score_bar.create_text(SCORE_WIDTH/4*3, MAP_HEIGHT/GRID_SIZE*2.5, text=self._game.get_num_destroyed(), fill="white")

        # update the number of total shots
        self._status_bar.update_total_shots(self._game.get_total_shots())

    def step(self):
        """This method is called every 2 seconds and triggers the step method for
        the game and updates the view accordingly."""
        self._game.step()
        self.draw(self._game)

        # # controll the game and messagebox by win or lost
        # if self._game.has_won() is None:
        #     pass

        # elif self._game.has_won():
        #     if messagebox.showinfo("WIN", "Congratulation! You Win!"):
        #         self._master.destroy()

        # elif not self._game.has_lost():
        #     if messagebox.showinfo("LOSE", "Sorry! You Lost!"):
        #         self._master.destroy()

        # recursive
        self._master.after(2*1000, self.step)

    def update_timer(self):
        """This method is similarly to step, called every 1 second and triggers
        the update_timer method for the game and updates the view accordingly
        if the game is not paused."""
        if self._status_bar.get_pause_or_play():
            self._master.after(1*1000, self.update_timer)
            self._timer_s += 1
            if not self._timer_s % 60:
                self._timer_m += 1
                self._timer_s = 0

        self._status_bar._timer.config(text=f"{self._timer_m}m {self._timer_s}s")

class StatusBar(tk.Frame):
    """StatusBar inherits from tk.Frame."""
    def __init__(self, master, update_timer, **kwargs):
        """Displays a shot counter, a timer and a pause/play button.

        Parameters:
            master: master,
            The parent window

            update_timer: method,
            The purpose of this argument is for accessing the update_timer method
            from AdvancedHackerController to implement the functionality of stopping
            and continuing the time count through button toggle.

            **kwargs:
            Signifies that any additional named arguments supported by tk.Canvas
            should also be supported by this class.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._pause_or_play = True
        self._update_timer = update_timer

        # frame to contain total shots
        self._shots_frame = tk.Frame(master)
        self._shots_frame.pack(side=tk.LEFT, expand=True)

        self._total_shots_header = tk.Label(self._shots_frame, text="Total Shots")
        self._total_shots_header.pack(side=tk.TOP)

        self._total_shots = tk.Label(self._shots_frame, text="0")
        self._total_shots.pack(side=tk.TOP)

        # frame to contain timer
        self._timer_frame = tk.Frame(master)
        self._timer_frame.pack(side=tk.LEFT, expand=True)

        self._timer_header = tk.Label(self._timer_frame, text="Timer")
        self._timer_header.pack(side=tk.TOP)

        self._timer = tk.Label(self._timer_frame, text="0m 0s")
        self._timer.pack(side=tk.TOP)

        # to place the button
        self._pause_play_button = tk.Button(master, text="Pause", width=5, command=self.button_toggle)
        self._pause_play_button.pack(side=tk.LEFT, expand=True)

    def update_total_shots(self, total_shots: int) -> None:
        """Update the number of total shots."""
        self._total_shots.config(text=f"{total_shots}")

    def button_toggle(self) -> None:
        """Control the pause and play situation."""
        if self._pause_or_play:
            self._pause_play_button.config(text="Play")

        elif not self._pause_or_play:
            self._pause_play_button.config(text="Pause")
            self._master.after(1*1000, self._update_timer)

        self._pause_or_play = not self._pause_or_play

    def get_pause_or_play(self) -> bool:
        """Return the current pause or play bool value."""
        return self._pause_or_play

class FileMenu(tk.Menu):
    """FileMenu inherits from tk.Menu to add file menu with some options."""
    def __init__(self, master, new_game, save_game, load_game, **kwargs):
        """Initialize the file menu and its options.

        Parameters:
            master: master,
            The parent window

            new_game: method,
            The purpose is to command the new game method from AdvanceHackerControll

            save_game: method,
            The purpose is to command the save game method from AdvanceHackerControll

            load_game: method,
            The purpose is to command the load game method from AdvanceHackerControll

            **kwargs:
            Signifies that any additional named arguments supported by tk.Canvas
            should also be supported by this class.
        """
        super().__init__(master, **kwargs)
        self._master = master

        # initialize the file menu
        file_menu = tk.Menu(self)
        self.add_cascade(label="File", menu=file_menu)

        # set up the new game, save, load and quit options
        file_menu.add_command(label="New game", command=new_game)
        file_menu.add_command(label="Save game", command=save_game)
        file_menu.add_command(label="Load game", command=load_game)
        file_menu.add_command(label="Quit", command=self.quit)

    def quit(self) -> None:
        """Pop out a message box to ask the user whether to quit the game or not."""
        if messagebox.askyesno("Quit", "Are you going to quit this game?"):
            self._master.destroy()

def start_game(root, TASK=TASK):
    """Execute the game through HackerController or AdvanceHackerControll."""
    controller = HackerController

    if TASK != 1:
        controller = AdvancedHackerController

    app = controller(root, GRID_SIZE)
    return app

def main():
    """Initialize root and execute the game."""
    root = tk.Tk()
    root.title(TITLE)
    app = start_game(root)
    root.mainloop()


if __name__ == '__main__':
    main()
