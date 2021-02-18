import sys
import time
import copy

class SokobanMap:
    """
    Instance of a Sokoban game map. You may use this class and its functions
    directly or duplicate and modify it in your solution. You should avoid
    modifying this file directly.

    COMP3702 2019 Assignment 1 Support Code

    Last updated by njc 11/08/19
    """

    # input file symbols
    BOX_SYMBOL = 'B'
    TGT_SYMBOL = 'T'
    PLAYER_SYMBOL = 'P'
    OBSTACLE_SYMBOL = '#'
    FREE_SPACE_SYMBOL = ' '
    BOX_ON_TGT_SYMBOL = 'b'
    PLAYER_ON_TGT_SYMBOL = 'p'

    # move symbols (i.e. output file symbols)
    LEFT = 'l'
    RIGHT = 'r'
    UP = 'u'
    DOWN = 'd'

    # render characters
    FREE_GLYPH = '   '
    OBST_GLYPH = 'XXX'
    BOX_GLYPH = '[B]'
    TGT_GLYPH = '(T)'
    PLAYER_GLYPH = '<P>'

    def __init__(self, filename, parent=None, action=None, depth=0):
        """
        Build a Sokoban map instance from the given file name
        :param filename:
        """
        f = open(filename, 'r')

        rows = []
        for line in f:
            if len(line.strip()) > 0:
                rows.append(list(line.strip()))

        f.close()

        row_len = len(rows[0])
        for row in rows:
            assert len(row) == row_len, "Mismatch in row length"

        num_rows = len(rows)

        
        box_positions = []
        tgt_positions = []
        player_position = None
        
        
        for i in range(num_rows):
            for j in range(row_len):
                if rows[i][j] == self.BOX_SYMBOL:
                    box_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.TGT_SYMBOL:
                    tgt_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.PLAYER_SYMBOL:
                    player_position = (i, j)
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.BOX_ON_TGT_SYMBOL:
                    box_positions.append((i, j))
                    tgt_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL
                elif rows[i][j] == self.PLAYER_ON_TGT_SYMBOL:
                    player_position = (i, j)
                    tgt_positions.append((i, j))
                    rows[i][j] = self.FREE_SPACE_SYMBOL

        assert len(box_positions) == len(tgt_positions), "Number of boxes does not match number of targets"

        self.x_size = row_len
        self.y_size = num_rows
        self.box_positions = box_positions
        self.tgt_positions = tgt_positions
        self.player_position = player_position
        self.player_x = player_position[1]
        self.player_y = player_position[0]
        self.obstacle_map = rows

        self.parent = parent  # parent node, a NODE! not just a matrix.
        self.action = action  # The one that led to this node (useful for retracing purpose)
        self.depth = depth  # depth of the node in the tree. This is the criterion for who's next in DFS, BFS.
    
    def apply_move(self, move):
        """
        Apply a player move to the map.
        :param move: 'L', 'R', 'U' or 'D'
        :return: True if move was successful, false if move could not be completed
        """
        
        # basic obstacle check
        if move == self.LEFT:
            if self.obstacle_map[self.player_y][self.player_x - 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x - 1
                new_y = self.player_y

        elif move == self.RIGHT:
            if self.obstacle_map[self.player_y][self.player_x + 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x + 1
                new_y = self.player_y

        elif move == self.UP:
            if self.obstacle_map[self.player_y - 1][self.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x
                new_y = self.player_y - 1

        else:
            if self.obstacle_map[self.player_y + 1][self.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = self.player_x
                new_y = self.player_y + 1

        # pushed box collision check
        if (new_y, new_x) in self.box_positions:
            if move == self.LEFT:
                if self.obstacle_map[new_y][new_x - 1] == self.OBSTACLE_SYMBOL or (new_y, new_x - 1) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x - 1
                    new_box_y = new_y

            elif move == self.RIGHT:
                if self.obstacle_map[new_y][new_x + 1] == self.OBSTACLE_SYMBOL or (new_y, new_x + 1) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x + 1
                    new_box_y = new_y

            elif move == self.UP:
                if self.obstacle_map[new_y - 1][new_x] == self.OBSTACLE_SYMBOL  or (new_y - 1, new_x) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x
                    new_box_y = new_y - 1

            else:
                if self.obstacle_map[new_y + 1][new_x] == self.OBSTACLE_SYMBOL or (new_y + 1, new_x) in self.box_positions:
                    return False
                else:
                    new_box_x = new_x
                    new_box_y = new_y + 1

            # update box position
            self.box_positions.remove((new_y, new_x))
            self.box_positions.append((new_box_y, new_box_x))

        # update player position
        self.player_x = new_x
        self.player_y = new_y

        return True
    
    def get_state_wp(self):
        states = self.tgt_positions.copy()
        for i in self.box_positions:
            states.append(i)
        states.append((self.player_x, self.player_y))       
        return tuple(states)
    
    def get_state(self):
        states = self.tgt_positions.copy()
        for i in self.box_positions:
            states.append(i)     
        return tuple(states)
        
    def goal_state(self):
        states = self.tgt_positions.copy()
        for i in self.tgt_positions:
            states.append(i)     
        return tuple(states)
        
  
    
    def done(self, current_node):
        """ The prupose of this function  is: Trace back this node to the founding granpa.
        Print out the states through out
        """
        founding_father = current_node
        states = []  # the retraced states will be stored here.
        counter = 0
        limit = 50  # if the trace is longer than 50, don't print anything, it will be a mess.
        while founding_father:
            states.append(founding_father)
            founding_father = founding_father.parent
            counter += 1
            # Keep doing this until you reach the founding father that has a parent None (see default of init method)
        print('Number of steps to the goal = ', counter)
        if counter > limit:
            print('Too many steps to be printed')
        else:
            for i in reversed(states):  # Cause we want to print solution from initial to goal not the opposite.
                i.render()
                print('\n')

    def render(self):
        """
        Render the map's current state to terminal
        """
        for r in range(self.y_size):
            line = ''
            for c in range(self.x_size):
                symbol = self.FREE_GLYPH
                if self.obstacle_map[r][c] == self.OBSTACLE_SYMBOL:
                    symbol = self.OBST_GLYPH
                if (r, c) in self.tgt_positions:
                    symbol = self.TGT_GLYPH
                # box or player overwrites tgt
                if (r, c) in self.box_positions:
                    symbol = self.BOX_GLYPH
                if self.player_x == c and self.player_y == r:
                    symbol = self.PLAYER_GLYPH
                line += symbol
            print(line)

        print('\n\n')

    def is_finished(self):
        finished = True
        for i in self.box_positions:
            if i not in self.tgt_positions:
                finished = False
        return finished
    
    def explore_actions(self):     
          possibilities = ['u', 'd', 'r', 'l']
          actions = []
          for apossibility in possibilities:
              new_state = copy.deepcopy(self)
              if(new_state.apply_move(apossibility)):
                   actions.append(apossibility)
          return actions
    
    def BFS(self):
        start = time.time()
        frontier = [self]  # queue of found but unvisited nodes, FIFO
        frontier_max_size = len(frontier)  # We measure space / memory requirements of the algo via this metric.
        ft = set()
        ft.add(self.get_state_wp())
        explored = set([])
        ct = 0
        
        while frontier:
            ct += 1
            print(ct, end='\r')
            if len(frontier) > frontier_max_size: frontier_max_size = len(frontier)

            current_node = frontier.pop(0) # select and remove the first node in the queue

            ft.remove(tuple(current_node.get_state_wp()))
            explored.add(tuple(current_node.get_state_wp()))
            
            
            
            if (current_node.is_finished()):
                print('Time required = ', -start + time.time())
                print('Explored states = ', len(explored))
                print('Frontier max size = ', frontier_max_size)
                self.done(current_node)
                return True
            
            actions = current_node.explore_actions()

            for anaction in actions:  # add exploration results to the frontier.
                new_node = copy.deepcopy(current_node)
                new_node.apply_move(anaction)
                new_node.depth += 1
                new_node.parent = current_node
                new_node.action = anaction

                if tuple(new_node.get_state_wp()) not in explored:
                    if tuple(new_node.get_state_wp()) not in ft:
                        frontier.append(new_node)
                        ft.add(tuple(new_node.get_state_wp()))
                                    
        print('Failed to reach target goal. Number of states explored = ')
        return len(explored) 
                            
                
def main(arglist):
    """
    Run a playable game of Sokoban using the given filename as the map file.
    :param arglist: map file name
    """
    try:
        import msvcrt
        getchar = msvcrt.getch
    except ImportError:
        getchar = sys.stdin.read(1)

#    if len(arglist) != 1:
#        print("Running this file directly launches a playable game of Sokoban based on the given map file.")
#        print("Usage: sokoban_map.py [map_file_name]")
#        return

#    print("Use the arrow keys to move. Press 'q' to quit. Press 'r' to restart the map.")

    map_inst = SokobanMap("D:/DAngus/uni/2019/SEM2/COMP3702/a1/comp3702-a1/testcases/4box_m2.txt")
#    print(map_inst.player_position)
#    print(map_inst.box_positions)
#    print(map_inst.tgt_positions)
#    print(map_inst.get_state_wp())
#    print(map_inst.get_state())
#    print(map_inst.goal_state())
    
    map_inst.BFS()

#    map_inst.render()
    

    steps = 0
    


#    while True:
#        char = getchar()
#
#        if char == b'q':
#            break
#
#        if char == b'r':
#            map_inst = SokobanMap(arglist[0])
#            map_inst.render()
#
#            steps = 0
#
#        if char == b'\xe0':
#            # got arrow - read direction
#            dir = getchar()
#            if dir == b'H':
#                a = SokobanMap.UP
#            elif dir == b'P':
#                a = SokobanMap.DOWN
#            elif dir == b'K':
#                a = SokobanMap.LEFT
#            elif dir == b'M':
#                a = SokobanMap.RIGHT
#            else:
#                print("!!!error")
#                a = SokobanMap.UP
#
#            map_inst.apply_move(a)
#            map_inst.render()
#
#            steps += 1
#
#            if map_inst.is_finished():
#                print("Puzzle solved in " + str(steps) + " steps!")
#                return


if __name__ == '__main__':
    main(sys.argv[1:])

