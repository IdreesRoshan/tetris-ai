import pygame
import random

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 660
GRID_SIZE = 30
UI_WIDTH = 250

# Colours for pieces
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetrimino shapes. These lists/matrices 
# follow the guidelines for the Super Rotation System
SHAPES = [
    [[0, 1, 0],
     [1, 1, 1],
     [0, 0, 0]],

    [[0, 2, 2],
     [2, 2, 0],
     [0, 0, 0]],

    [[3, 3, 0],
     [0, 3, 3],
     [0, 0, 0]],

    [[4, 0, 0],
     [4, 4, 4],
     [0, 0, 0]],

    [[0, 0, 5],
     [5, 5, 5],
     [0, 0, 0]],

    [[0, 0, 0, 0],
     [6, 6, 6, 6],
     [0, 0, 0, 0],
     [0, 0, 0, 0]],

    [[7, 7],
     [7, 7]],
]

# Indexing the colours to be used later for each tetrimino
SHAPE_COLOURS = [PURPLE, RED, GREEN, PINK, ORANGE, CYAN, YELLOW]

# Tetrimino class responsible for drawing the pieces and rotation
class Tetrimino:
    def __init__(self, shape, colour=None):
        self.shape = shape
        self.colour = SHAPE_COLOURS[SHAPES.index(self.shape)]   # Assigns a colour to each tetrimino depending on its index
        self.x = SCREEN_WIDTH // 2
        self.y = 0

    # Rotate 90 degrees clockwise
    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    # Rotate 90 degrees anti-clockwise
    def rotate_Anti_Clockwise(self):
        self.shape = [list(row) for row in zip(*self.shape)][::-1]
    
    # This reads the data in the screen parameter and draws the tetrimino
    def draw(self, screen, offset_x, offset_y):
        for y, row in enumerate(self.shape):
            for x, value in enumerate(row):
                if value != 0:
                    pygame.draw.rect(screen, self.colour, (offset_x + x * GRID_SIZE, offset_y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Board:
    def __init__(self, screen_Width, screen_Height, grid_Size):

        num_Columns = screen_Width // grid_Size
        num_Rows = screen_Height // grid_Size
        self.grid = []
        for i in range(num_Rows):
            row = [0] * num_Columns
            self.grid.append(row)

        self.screen_Width = screen_Width
        self.screen_Height = screen_Height
        self.grid_Size = grid_Size
        self.lines_Cleared = 0
        self.score = 0
        self.level = 1

        # Bag is responsible for the 7 bag randomizer used in original Tetris games
        self.bag = self.get_New_Bag()

        # Tetriminos used for the UI and the current tetrimino being played
        self.next_Tetrimino = self.get_Next_Tetrimino()
        self.current_Tetrimino = self.get_Next_Tetrimino()

    # Refills the bag with a new bag full of tetrimino pieces
    def get_New_Bag(self):
        return random.sample(SHAPES, len(SHAPES))

    def get_Next_Tetrimino(self):
        if not self.bag:    # If the bag is empty then it will refill the bag
            self.bag = self.get_New_Bag()
        shape = self.bag.pop()  # Otherwise it will take a tetrimino out of the bag and return it
        return Tetrimino(shape)
    
    # This adds a piece to the board, by looking for non-zero values and updating the grid
    def add_Piece(self, tetrimino):
        for y, row in enumerate(tetrimino.shape):
            for x, value in enumerate(row):
                if value != 0:
                    grid_x = (tetrimino.x // self.grid_Size) + x
                    grid_y = (tetrimino.y // self.grid_Size) + y

                    # This checks whether the position is within bounds or not, exception is raised if it's not
                    if 0 <= grid_x < len(self.grid[0]) and 0 <= grid_y < len(self.grid):
                        self.grid[grid_y][grid_x] = value
                    else:
                        raise IndexError("Trying to add piece out of bounds")
                        
    # This function checks if move proposed is within bounds
    # Very important for rotation and the implementation of the Super Rotation System
    def is_Valid_Move(self, tetrimino, dx, dy):
        for y, row in enumerate(tetrimino.shape):
            for x, value in enumerate(row):
                if value:
                    new_x = (tetrimino.x // self.grid_Size) + x + dx
                    new_y = (tetrimino.y // self.grid_Size) + y + dy

                    # Similar to add Piece, it checks if it is within bounds
                    if new_x < 0 or new_x >= self.screen_Width // self.grid_Size or new_y < 0 or new_y >= self.screen_Height // self.grid_Size:
                        return False
                    if self.grid[new_y][new_x]:
                        return False
        return True

    # This function is essential when implementing wall kicks in game. Allows rotation on the barriers
    def adjust_For_Rotation(self, tetrimino):
        if self.is_Valid_Move(tetrimino, 0, 0):
            return True
        
        # This For loop checks whether it needs to move 1 or 2 spaces left or right in the grid
        for dx in [-1, 1, -2, 2]:
            original_x = tetrimino.x    # Store the original position in case the kick is not valid
            tetrimino.x += dx * self.grid_Size
            if self.is_Valid_Move(tetrimino, 0, 0):
                return True
            tetrimino.x = original_x
        return False

    def clear_Lines(self):
        lines_Cleared = 0
        
        new_Grid = []
        for row in self.grid:
            if all(cell != 0 for cell in row):
                lines_Cleared += 1  # Increment for each full line
            else:
                new_Grid.append(row)
        
        empty_Rows = [[0] * (self.screen_Width // self.grid_Size) for _ in range(lines_Cleared)]
        self.grid = empty_Rows + new_Grid

        # Multiplier for the points depending on how many 
        # lines were cleared, following Official Tetris Guidelines
        if lines_Cleared == 1:
            self.score += 40 * (self.level + 1)
        elif lines_Cleared == 2:
            self.score += 100 * (self.level + 1)
        elif lines_Cleared == 3:
            self.score += 300 * (self.level + 1)
        elif lines_Cleared == 4:
            self.score += 1200 * (self.level + 1)

        # Update lines cleared and level up every 10 lines
        self.lines_Cleared += lines_Cleared
        self.level = min(self.lines_Cleared // 10 + 1, 29) # Cap the max level at 29

        return lines_Cleared

    def drop_Piece(self, tetrimino):
        # Moves the tetrimino down y axis and until the move is not valid
        while self.is_Valid_Move(tetrimino, 0, 1):
            tetrimino.y += self.grid_Size
        
        # The tetrimino is then added to the last valid spot in the y axis of the grid
        self.add_Piece(tetrimino)

        # Check if any lines are cleared
        return self.clear_Lines()

    def simulate_Piece(self, tetrimino):
        # Create a temporary board to simulate the piece placement
        temp_board = [row[:] for row in self.grid]
        original_x, original_y = tetrimino.x, tetrimino.y
        
        while self.is_Valid_Move(tetrimino, 0, 1):
            tetrimino.y += self.grid_Size
        
        self.add_Piece(tetrimino)
        lines_cleared = self.clear_Lines()
        
        tetrimino.x, tetrimino.y = original_x, original_y
        self.grid = temp_board
        
        return lines_cleared


class TetrisAI:
    def __init__(self, board, weights=None, screen=None):
        self.board = board
        self.weights = weights if weights else [3.0, 0.5, 0.3, 8.5] # If there are no weights then use these as the default weights
        self.screen = screen 

    # This function calculates the total number of holes in the grid
    def calculate_Holes(self):
        holes = 0
        for x in range(len(self.board.grid[0])):
            column_Hole = False
            for y in range(len(self.board.grid)):
                if self.board.grid[y][x] == 0:
                    if column_Hole:
                        holes += 1
                else:
                    column_Hole = True
        return holes

    # This will check the drop height of the tetrimino passed through as a parameter    
    def get_Drop_Height(self, tetrimino):
        initial_y = tetrimino.y
        while self.board.is_Valid_Move(tetrimino, 0, 1):
            tetrimino.y += self.board.grid_Size
        drop_Height = tetrimino.y
        tetrimino.y = initial_y
        return drop_Height

    # This will calculate the variance in height of all the columns
    def calculate_Bumpiness(self):
        heights = []
        for x in range(len(self.board.grid[0])):
            column_Height = 0
            for y in range(len(self.board.grid)):
                if self.board.grid[y][x] != 0:
                    column_Height = len(self.board.grid) - y
                    break
            heights.append(column_Height)
        bumpiness = sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))
        return bumpiness

    #Each of these functions are used to test the efficacy of the heuristics
    def calculate_Cost(self, holes_created, drop_height, bumpiness, lines_cleared):
        return (holes_created * self.weights[0]) + (bumpiness * self.weights[1]) - (drop_height * self.weights[2]) - (lines_cleared * self.weights[3])
    
    def calculate_Cost_Holes(self, holes_created):
        return (holes_created * self.weights[0])

    def calculate_Cost_Holes_Height(self, holes_created, drop_height):
        return (holes_created * self.weights[0] - (drop_height * self.weights[2]))
    
    def calculate_Cost_Holes_Height_Bump(self, holes_created, drop_height, bumpiness):
        return (holes_created * self.weights[0]) + (bumpiness * self.weights[1]) - (drop_height * self.weights[2])

    # Calls the funtion to get all the heuristics, will be used later for the UI
    def get_Heuristics(self):
        heuristics = {
            "Holes": self.calculate_Holes(),
            "Drop Height": self.get_Drop_Height(self.board.current_Tetrimino),
            "Bumpiness": self.calculate_Bumpiness()
        }
        return heuristics

    # This funtion will calculate the cost 
    def get_Best_Move(self):
        best_Move = None
        Lowest_Cost = float('inf')

        original_x = self.board.current_Tetrimino.x
        original_y = self.board.current_Tetrimino.y
        original_Shape = self.board.current_Tetrimino.shape

        initial_Holes = self.calculate_Holes()  # Calculate the number of holes before placing any tetrimino

        for rotation in range(4):
            self.board.current_Tetrimino.shape = original_Shape  # Reset to original shape before rotating
            for _ in range(rotation):
                self.board.current_Tetrimino.rotate()

                for x in range(-self.board.grid_Size, self.board.screen_Width, self.board.grid_Size):
                    # Move the Tetrimino to the test position
                    self.board.current_Tetrimino.x = x
                    self.board.current_Tetrimino.y = 0

                    if self.board.is_Valid_Move(self.board.current_Tetrimino, 0, 0):
                        # Drop the piece to the bottom
                        drop_Height = self.get_Drop_Height(self.board.current_Tetrimino)
                        self.board.current_Tetrimino.y = drop_Height

                        # Simulate the piece placement
                        temp_Board = [row[:] for row in self.board.grid]
                        self.board.add_Piece(self.board.current_Tetrimino)
                        holes_After = self.calculate_Holes()  # Calculate the number of holes after placing the tetrimino

                        holes_Created = holes_After - initial_Holes  # Calculate the difference in holes

                        # Clear lines and calculate lines cleared
                        lines_Cleared = self.board.clear_Lines()

                        bumpiness = self.calculate_Bumpiness()  # Calculate the bumpiness

                        # Simulate next piece placement and calculate total cost
                        next_Piece = self.board.next_Tetrimino
                        next_Piece_Lines_Cleared = self.board.simulate_Piece(next_Piece)
                        total_Lines_Cleared = lines_Cleared + next_Piece_Lines_Cleared
                        
                        # Calculate the cost using the heuristics you want
                        cost = self.calculate_Cost(holes_Created, drop_Height, bumpiness, total_Lines_Cleared)

                        #cost = self.calculate_Cost_Holes(holes_created)

                        #cost = self.calculate_Cost_Holes_Height(holes_Created, drop_Height)

                        #cost = self.calculate_Cost_Holes_Height_Bump(holes_Created, drop_Height, bumpiness)


                        if cost < Lowest_Cost:
                            Lowest_Cost = cost
                            best_Move = (rotation, x)

                        # Reset the board state
                        self.board.grid = temp_Board
                        self.board.lines_Cleared -= lines_Cleared  # Reset lines cleared after simulation

        # Reset Tetrimino to original position and shape
        self.board.current_Tetrimino.x = original_x
        self.board.current_Tetrimino.y = original_y
        self.board.current_Tetrimino.shape = original_Shape

        return best_Move

def draw_Grid(screen):
    # Draws a grid using the grid's dimensions, makes the grid visible with white lines
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y))

def draw_UI(screen, board, heuristics):
    # Sets up the font and renders the text for the score, level, lines cleared and next tetrimino on screen
    font = pygame.font.SysFont("Times New Roman", 24)
    score_Text = font.render(f"Score: {board.score}", True, WHITE)
    level_Text = font.render(f"Level: {board.level}", True, WHITE)
    lines_Text = font.render(f"Lines Cleared: {board.lines_Cleared}", True, WHITE)
    next_Piece_Text = font.render("Next:", True, WHITE)

    screen.blit(score_Text, (SCREEN_WIDTH + 20, 20))
    screen.blit(level_Text, (SCREEN_WIDTH + 20, 60))
    screen.blit(lines_Text, (SCREEN_WIDTH + 20, 100))
    screen.blit(next_Piece_Text, (SCREEN_WIDTH + 20, 140))

    # Draw the next tetrimino
    if board.next_Tetrimino:
        for y, row in enumerate(board.next_Tetrimino.shape):
            for x, val in enumerate(row):
                if val:
                    pygame.draw.rect(screen, board.next_Tetrimino.colour, (SCREEN_WIDTH + 20 + x * GRID_SIZE, 180 + y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    
    # Render heuristic values
    heuristic_y_Offset = 240
    for heuristic, value in heuristics.items():
        heuristic_Text = font.render(f"{heuristic}: {value}", True, WHITE)
        screen.blit(heuristic_Text, (SCREEN_WIDTH + 20, heuristic_y_Offset))
        heuristic_y_Offset += 40

def get_Fall_Speed(level):
    # Each tetris level, an estimate on the speeds per level based on the Official Tetris Guidelines
    level_Speeds = {
        1: 100,
        2: 100,
        3: 100,
        4: 100,
        5: 100,
        6: 100,
        7: 100,
        8: 100,
        9: 100,
        10: 80,  # first 10 levels the speed increases
        11: 80,
        12: 80,
        13: 50,  # speed increase at 13
        14: 50,
        15: 50,
        16: 30,  # speed increase at 16
        17: 30,
        18: 30,
        19: 10,  # speed increase at 19
        20: 10,
        21: 10,
        22: 10,
        23: 10,
        24: 10,
        25: 10,
        26: 10,
        27: 10,
        28: 10,
        29: 5,  # speed increase at 29, kill screen
    }
    return level_Speeds.get(level, 100) / 1000.0  # Python.time works with seconds

def main(use_Ai, run_Multiple=False, num_Runs=100, results=None):
    # Draw the screen and add Tetris as screen header
    screen = pygame.display.set_mode((SCREEN_WIDTH + UI_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")

    # Introduce a clock for the game's framerate, and create a board instance
    clock = pygame.time.Clock()
    board = Board(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)
    best_Weights = [3.0, 0.5, 0.3, 8.5]
    ai = TetrisAI(board, best_Weights, screen)
    fall_Time = 0

    # Game loop
    running = True
    while running:
        # Make the screen background black and start the clock
        screen.fill(BLACK)
        fall_Time += clock.get_rawtime()
        clock.tick()

        # Adjust the fall speed depending on the game's level
        fall_Speed = get_Fall_Speed(board.level)

        # Checks if enough time has passed for the tetrimino to move down
        if fall_Time / 1000 >= fall_Speed:
            fall_Time = 0
            if use_Ai:
                # Use AI to find the best move
                best_Move = ai.get_Best_Move()
                if best_Move:
                    rotation, best_x = best_Move
                    for _ in range(rotation):
                        board.current_Tetrimino.rotate()
                    board.current_Tetrimino.x = best_x
                    while board.is_Valid_Move(board.current_Tetrimino, 0, 1):
                        board.current_Tetrimino.y += GRID_SIZE
                    board.drop_Piece(board.current_Tetrimino)
                    board.current_Tetrimino = board.next_Tetrimino
                    board.next_Tetrimino = board.get_Next_Tetrimino()
                    if not board.is_Valid_Move(board.current_Tetrimino, 0, 0):
                        running = False
            else:
                # Manually move the tetrimino down
                if board.is_Valid_Move(board.current_Tetrimino, 0, 1):
                    board.current_Tetrimino.y += GRID_SIZE
                else:
                    board.drop_Piece(board.current_Tetrimino)
                    board.current_Tetrimino = board.next_Tetrimino
                    board.next_Tetrimino = board.get_Next_Tetrimino()
                    if not board.is_Valid_Move(board.current_Tetrimino, 0, 0):
                        running = False

        # Event handling takes place for all the game controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Movement keys, checks if the move is valid before carrying it out
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and board.is_Valid_Move(board.current_Tetrimino, -1, 0):
                    board.current_Tetrimino.x -= GRID_SIZE

                if event.key == pygame.K_RIGHT and board.is_Valid_Move(board.current_Tetrimino, 1, 0):
                    board.current_Tetrimino.x += GRID_SIZE

                if event.key == pygame.K_DOWN and board.is_Valid_Move(board.current_Tetrimino, 0, 1):
                    board.current_Tetrimino.y += GRID_SIZE

                # Rotation keys, checks if the rotation is valid and integrates a wall kick if necessary
                if event.key == pygame.K_UP:
                    original_Shape = board.current_Tetrimino.shape
                    board.current_Tetrimino.rotate()
                    if not board.is_Valid_Move(board.current_Tetrimino, 0, 0):
                        if not board.adjust_For_Rotation(board.current_Tetrimino):
                            board.current_Tetrimino.shape = original_Shape

                if event.key == pygame.K_z:
                    original_Shape = board.current_Tetrimino.shape
                    board.current_Tetrimino.rotate_Anti_Clockwise()
                    if not board.is_Valid_Move(board.current_Tetrimino, 0, 0):
                        if not board.adjust_For_Rotation(board.current_Tetrimino):
                            board.current_Tetrimino.shape = original_Shape

                # Hard dropping the tetrimino
                if event.key == pygame.K_SPACE:
                    board.drop_Piece(board.current_Tetrimino)
                    board.current_Tetrimino = board.next_Tetrimino
                    board.next_Tetrimino = board.get_Next_Tetrimino()
                    if not board.is_Valid_Move(board.current_Tetrimino, 0, 0):
                        running = False

                # Pressing the 'a' key will turn the inteligent Agent mode on or off
                if event.key == pygame.K_a:
                    use_Ai = not use_Ai

        # Draws the playing grid with the white lines
        draw_Grid(screen)

        # Reads all the data on the grid and draws the correct placed tetriminos
        for y, row in enumerate(board.grid):
            for x, value in enumerate(row):
                if value:
                    pygame.draw.rect(screen, SHAPE_COLOURS[value - 1], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # This one draws the current Tetrimino in play
        board.current_Tetrimino.draw(screen, board.current_Tetrimino.x, board.current_Tetrimino.y)

        # Draw the UI with all the scores, levels, lines cleared and next tetrimino
        heuristics = ai.get_Heuristics()
        draw_UI(screen, board, heuristics)

        # Update each frame
        pygame.display.update()

    # Print final score and level before quitting
    print(f"Game Over! Final Score: {board.score}, Level: {board.level}, Lines Cleared: {board.lines_Cleared}")

    # If running multiple times, store the results
    if run_Multiple and results is not None:
        results.append((board.score, board.level, board.lines_Cleared))


def run_Multiple_Games(num_Runs=100):
    results = []
    for i in range(num_Runs):
        print(f"Running game {i + 1}...")
        main(use_Ai=True, run_Multiple=True, results=results)

    # Save the results to a text file
    #with open('tetris_results_holes_height_Bump.txt', 'w') as file:
   #     for score, level, lines_Cleared in results:
    ##        file.write(f"Score: {score}, Level: {level}, Lines Cleared: {lines_Cleared}\n")
    #print("Results saved to tetris_results.txt")

if __name__ == "__main__":
    mode = input("Enter 'a' to use AI, 'm' to play manually, or 'r' to run multiple AI games: ")
    if mode == 'r':
        run_Multiple_Games(100)
    elif mode == 'a':
        use_Ai = True
        main(use_Ai)
    else:
        use_Ai = False
        main(use_Ai)

# Clean up Pygame resources
pygame.quit()
