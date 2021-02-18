import sys
import time
import copy
import heapq

# Some code sourced from:
# AI Sem2 2019 Tutorial 2 Soltuions
# 
# Alex | 31 July 2019
#
# Additional code sourced from:
#
#    COMP3702 2019 Assignment 1 Support Code
#
#    Last updated by njc 11/08/19
#


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

    def __init__(self, filename):
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
        self.count = len(self.tgt_positions)
        
        self.rootNode = Node()
        self.rootNode.setBox_positions(self.box_positions)
        self.rootNode.setPlayer_position(self.player_position)
        
        self.set_state_wp(self.rootNode)

        
    def apply_move(self, move, node):
        """
        Apply a player move to the map.
        :param move: 'L', 'R', 'U' or 'D'
        :return: True if move was successful, false if move could not be completed
        """
        
        # basic obstacle check
        if move == self.LEFT:
            if self.obstacle_map[node.player_y][node.player_x - 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = node.player_x - 1
                new_y = node.player_y

        elif move == self.RIGHT:
            if self.obstacle_map[node.player_y][node.player_x + 1] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = node.player_x + 1
                new_y = node.player_y

        elif move == self.UP:
            if self.obstacle_map[node.player_y - 1][node.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = node.player_x
                new_y = node.player_y - 1

        else:
            if self.obstacle_map[node.player_y + 1][node.player_x] == self.OBSTACLE_SYMBOL:
                return False
            else:
                new_x = node.player_x
                new_y = node.player_y + 1

        # pushed box collision check
        if (new_y, new_x) in node.box_positions:
            if move == self.LEFT:
                if self.obstacle_map[new_y][new_x - 1] == self.OBSTACLE_SYMBOL or (new_y, new_x - 1) in node.box_positions:
                    return False
                else:
                    new_box_x = new_x - 1
                    new_box_y = new_y

            elif move == self.RIGHT:
                if self.obstacle_map[new_y][new_x + 1] == self.OBSTACLE_SYMBOL or (new_y, new_x + 1) in node.box_positions:
                    return False
                else:
                    new_box_x = new_x + 1
                    new_box_y = new_y

            elif move == self.UP:
                if self.obstacle_map[new_y - 1][new_x] == self.OBSTACLE_SYMBOL  or (new_y - 1, new_x) in node.box_positions:
                    return False
                else:
                    new_box_x = new_x
                    new_box_y = new_y - 1

            else:
                if self.obstacle_map[new_y + 1][new_x] == self.OBSTACLE_SYMBOL or (new_y + 1, new_x) in node.box_positions:
                    return False
                else:
                    new_box_x = new_x
                    new_box_y = new_y + 1

            # update box position
            node.box_positions.remove((new_y, new_x))
            node.box_positions.append((new_box_y, new_box_x))

        # update player position
        node.setPlayer_position((new_y, new_x))


        return True
    
    def set_state_wp(self, node):
        state = self.tgt_positions.copy()
        for i in node.box_positions:
            state.append(i)
        state.append((node.player_x, node.player_y))       
        node.setState(tuple(state))
        return

        
    def goal_state(self):
        states = self.tgt_positions.copy()
        for i in self.tgt_positions:
            states.append(i)     
        return tuple(states)
    
    def calc_heuristic2(self, node):
        mnhtn_dist = 0
        for box in node.box_positions:
            if box not in self.tgt_positions:
                x = abs(box[0] - node.player_position[0]) + abs(box[1] - node.player_position[1])
                if(x < mnhtn_dist):
                    mnhtn_dist = x
                
        node.setHeuristic(mnhtn_dist)
        return
    
    def calc_heuristicAstar(self, node):
        mnhtn_dist = 0
        for box in node.box_positions:
            min_dis = self.x_size + self.y_size
            for target in self.tgt_positions:
                x = abs(box[0] - target[0]) + abs(box[1] - target[1])
                if(x < min_dis):
                    min_dis = x
            mnhtn_dist += min_dis
        node.setHeuristic(mnhtn_dist)
        return
    
    def calc_heuristicUCS(self, node):
        return 0
    
    
    def done(self, node):
        """ The prupose of this function  is: Trace back this node to the founding granpa.
        Print out the states through out
        """
        founding_father = node
        states = []  # the retraced states will be stored here.
        counter = 0
        solution = []
        while founding_father:
            states.append(founding_father)
            founding_father = founding_father.parent
            counter += 1
            # Keep doing this until you reach the founding father that has a parent None (see default of init method)
        for i in reversed(states):  # Cause we want to print solution from initial to goal not the opposite.
   #         self.render(i)
            if(i.action != None):
                solution.append(i.action)      
        return solution

    def render(self, node):
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
                if (r, c) in node.box_positions:
                    symbol = self.BOX_GLYPH
                if node.player_x == c and node.player_y == r:
                    symbol = self.PLAYER_GLYPH
                line += symbol
            print(line)

        print('\n\n')

    def is_finished(self, node):
        finished = True
        for i in node.box_positions:
            if i not in self.tgt_positions:
                finished = False
        return finished
    

    
    def Astar(self):
        start = time.time()
        frontier = []# queue of found but unvisited nodes, FIFO
        heapq.heapify(frontier)
        heapq.heappush(frontier, self.rootNode)
        frontier_max_size = len(frontier)  # We measure space / memory requirements of the algo via this metric.
        ft = set()
        ft.add(self.rootNode.get_state_wp())
        explored = set([])
        ct = 0
        self.rootNode.setHeuristic(self.calc_heuristicAstar(self.rootNode))
        while len(frontier) != 0:

            if len(frontier) > frontier_max_size: frontier_max_size = len(frontier)

            current_node = heapq.heappop(frontier) # select and remove the first node in the queue

            ft.remove(tuple(current_node.get_state_wp()))
            explored.add(tuple(current_node.get_state_wp()))         
            
            if (self.is_finished(current_node)):
                solution = self.done(current_node)
                return [-start + time.time(), len(explored), len(frontier), solution]
            
            actions = ['u', 'd', 'r', 'l']

            for anaction in actions: 
                new_node = Node(current_node, anaction, current_node.depth+1)
                new_node.populateChild(current_node)
                if(self.apply_move(anaction, new_node)):
                    self.calc_heuristicAstar(new_node)
                    self.set_state_wp(new_node)
                    if tuple(new_node.get_state_wp()) not in explored:
                        if tuple(new_node.get_state_wp()) not in ft:
                            heapq.heappush(frontier, new_node)
                            ft.add(tuple(new_node.get_state_wp()))
                
        return False
    
    def UCS(self):
        start = time.time()
        frontier = []# queue of found but unvisited nodes, FIFO
        heapq.heapify(frontier)
        heapq.heappush(frontier, self.rootNode)
        frontier_max_size = len(frontier)  # We measure space / memory requirements of the algo via this metric.
        ft = set()
        ft.add(self.rootNode.get_state_wp())
        explored = set([])
        ct = 0
        self.rootNode.setHeuristic(self.calc_heuristicUCS(self.rootNode))
        while len(frontier) != 0:

            if len(frontier) > frontier_max_size: frontier_max_size = len(frontier)

            current_node = heapq.heappop(frontier) # select and remove the first node in the queue

            ft.remove(tuple(current_node.get_state_wp()))
            explored.add(tuple(current_node.get_state_wp()))         
            
            if (self.is_finished(current_node)):
                solution = self.done(current_node)
                return [-start + time.time(), len(explored), len(frontier), solution]
            
            actions = ['u', 'd', 'r', 'l']

            for anaction in actions:  # add exploration results to the frontier.
                new_node = Node(current_node, anaction, current_node.depth+1)
                new_node.populateChild(current_node)
                
                if(self.apply_move(anaction, new_node)):
                    self.calc_heuristicUCS(new_node)
                    self.set_state_wp(new_node)
                    if tuple(new_node.get_state_wp()) not in explored:
                        if tuple(new_node.get_state_wp()) not in ft:
                            heapq.heappush(frontier, new_node)
                            ft.add(tuple(new_node.get_state_wp()))
                

        return len(explored)
    
    
class Node:
    """
    Created on Thu Aug 22 10:50:49 2019
    
    @author: Angus
    """
    def __init__(self, parent=None, action=None, depth=0):
        self.parent = parent  # parent node, a NODE! not just a matrix.
        self.action = action  # The one that led to this node (useful for retracing purpose)
        self.depth = depth  # depth of the node in the tree. This is the criterion for who's next in DFS, BFS.
        
    
    def populateChild(self, node):
        self.setState(node.state)
        self.setHeuristic(node.heuristic)
        self.setBox_positions(node.box_positions)
        self.setPlayer_position(node.player_position)
    
    def setState(self, state):
        self.state = copy.deepcopy(state)
        
    def setHeuristic(self, heuristic):
        self.heuristic = copy.deepcopy(heuristic)
    
    def setBox_positions(self, box_positions):
        self.box_positions = copy.deepcopy(box_positions)
        
        
    def setPlayer_position(self, player_position):
        self.player_position = copy.deepcopy(player_position)
        self.player_x = self.player_position[1]
        self.player_y = self.player_position[0]
        
    def get_state_wp(self):
        return self.state
    
    def __lt__(self, other):
        return (self.depth + self.heuristic) < (other.depth + other.heuristic)                         
                
def main(arglist):
    """
    Run a playable game of Sokoban using the given filename as the map file.
    :param arglist: map file name
    """
    
    map_inst = SokobanMap(arglist[0])
    
    output = map_inst.Astar()
    if output:
        print(output[3])
        print([output[1] + output[2],  output[2], output[1],output[0]])
    else:
        print("Solution not found")
#    print(len(output[3]))
    


if __name__ == '__main__':
    main(sys.argv[1:])

