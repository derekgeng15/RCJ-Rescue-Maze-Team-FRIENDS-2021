import os.path


class cell:
    def __init__(self):
        self.visited = False
        self.wall = [False, False, False, False]  # Up, Right, Down, Left
        self.victim = False
        self.checkpoint = False

    def blackout(self):
        self.wall = [True, True, True, True]  # All walls up
        self.visited = True


class Nav:
    def __init__(self, readInWall):
        print("Initialized AI!")
        # 2D array
        self.initialPosition = (20, 20)
        self.rows, self.cols = (40, 40)
        self.field = [[cell() for j in range(self.cols)]
                      for i in range(self.rows)]
        self.startPosition = self.initialPosition
        # row, column. Robot's current position on the field
        self.location = self.startPosition
        self.direction = 0  # The current direction of the robot
        self.previousDirection = 0
        self.previousLocation = (-1, -1)
        if os.path.isfile('wall.txt'): # If wall.txt already exists
            self.filePtr = open("wall.txt", 'r+')
        else:  # If wall.txt does not exist
            print("Creating wall.txt!")
            self.filePtr = open('wall.txt', 'w+')
            self.markVisited(writeToFile=True) # mark visited and write to file at starting location to make sure robot knows it is visited
            self.filePtr.flush()
        if self.filePtr:
            print("Wall.txt is opened successfully")
        else:
            print("Wall.txt did not open successfully. . .")
            raise SystemExit
        # This is to hold stuff to write out to file when we see checkpoint
        self.writeFileBuffer = []
        
        if readInWall:
            # Read in whole file, and then turn string into list of words
            data = self.filePtr.read().split()
            while len(data) > 0:
                row = int(data.pop(0))
                col = int(data.pop(0))
                typeOfData = data.pop(0)
                print("Read in:", row, col, typeOfData)
                if typeOfData == 'V':
                    print("Read visited!")
                    self.field[row][col].visited = True
                elif typeOfData == "VICTIM":
                    print("Read victim!")
                    self.field[row][col].victim = True
                elif typeOfData == "CHECKPOINT":
                    print("Read checkpoint!")
                    self.field[row][col].checkpoint = True
                    # Update starting position to last found checkpoint
                    self.location = (row, col)
                else:  # Data is giving a wall direction
                    self.markWall(typeOfData, (row, col), writeToFile=False)
            if self.location == self.initialPosition:
                self.markVisited(self.initialPosition)
        print("Starting Position:", self.location)
        print()
    
    def getLocation(self):
        return self.location
    
    def getPrevLocation(self):
        return self.previousLocation
    
    def getDirection(self):
        return self.direction
    
    def getPrevDirection(self):
        return self.previousDirection
    
    def markEverythingVisited(self):
        print("Marking Everything Visited!")
        for i in range(self.rows):
            for j in range(self.cols):
                self.field[i][j].visited = True
    
    #If wall data and victim data looks solid, then all data in buffer will actually be written to file.
    def flush(self):
        for i in range(len(self.writeFileBuffer)):
            self.filePtr.write(self.writeFileBuffer[i])
        self.filePtr.flush()
        print("Flushed data buffer to file!")
        self.clearFileBuffer()

    # Clears wall.txt
    def clearFileBuffer(self):
        self.writeFileBuffer.clear()

    # Converts a direction in str to int format or int to str format
    def convertDirection(self, direction):
        if isinstance(direction, str):
            if direction == 'NORTH':
                return 0
            if direction == 'EAST':
                return 1
            if direction == 'SOUTH':
                return 2
            if direction == 'WEST':
                return 3
        elif isinstance(direction, int):
            if direction == 0:
                return 'NORTH'
            if direction == 1:
                return 'EAST'
            if direction == 2:
                return 'SOUTH'
            if direction == 3:
                return 'WEST'
        else:
            print("Direction Conversion Error!")
            raise SystemExit

    # Converts a command in str to int format or int to str format
    def convertCommand(self, command):
        if isinstance(command, str):
            if command == 'FORWARD':  # Move forward
                return 0
            if command == 'RIGHT':  # Turn right 90 deg, then move forward
                return 1
            if command == 'BACKWARD':  # Turn 180 deg, then move forward
                return 2
            # Turn left 90 deg (-90 deg), then move forward
            if command == 'LEFT':
                return 3
        elif isinstance(command, int):
            if command == 0:
                return 'FORWARD'
            if command == 1:
                return 'RIGHT'
            if command == 2:
                return 'BACKWARD'
            if command == 3:
                return 'LEFT'
        else:
            print("Command Conversion Error!")
            raise SystemExit

    # This function returns the correct relative command for the robot to traverse. Call this funtion BEFORE you update self.location during calculate()!
    # @return Returns the needed command given circumstances and returns the new direction of the robot after executing this command
    def determineCommand(self, currentDirection, newPosition, oldPosition=None):
        if oldPosition is None:  # Defualt oldPosition to current location
            oldPosition = self.location

        # 1. Calculate the new needed direction
        adjustRow = newPosition[0] - oldPosition[0]
        adjustCol = newPosition[1] - oldPosition[1]
        if adjustRow == 1:  # Moving up
            newDirection = 0
        elif adjustCol == 1:  # Moving right
            newDirection = 1
        elif adjustRow == -1:  # Moving down
            newDirection = 2
        else:  # Moving left
            newDirection = 3

        # 2. Calculate what command to adjust the current direction into the new direction
        adjustDirection = ((newDirection-currentDirection) + 4) % 4
        if adjustDirection == 0:
            return 'FORWARD', newDirection
        elif adjustDirection == 1:
            return 'RIGHT', newDirection
        elif adjustDirection == 2:
            return 'BACKWARD', newDirection
        else:
            return 'LEFT', newDirection

    # This function takes the direction of the wall, enters it at a specified location [or the current location], and optionally writes the wall data to a file.
    # str, [tuple], [boolean]
    def markWall(self, direction, loc=None, writeToFile=True):
        if loc is None:  # Defualt loc to current location
            loc = self.location
        if isinstance(direction, str):  # Convert direction to integer
            direction = direction.upper()  # uppercase everything to match formatting
            direction = self.convertDirection(direction)

        self.field[loc[0]][loc[1]].wall[direction] = True  # Mark Wall

        direction = self.convertDirection(direction)  # Convert direction to string
        if writeToFile:
            # Row, Col, Direction
            self.writeFileBuffer.append(str(loc[0]) + ' ' +
                               str(loc[1]) + ' ' + direction + '\n')
            #self.filePtr.flush()
            print("Entered & wrote wall: ", direction, 'at:', loc[0], loc[1])
        else:
            print("Entered wall: ", direction, 'at:', loc[0], loc[1])

    def markCheckpoint(self, loc=None):
        if loc is None:  # Defualt loc to current location
            loc = self.location
        print("Wrote:", '\"' + str(loc[0]), str(loc[1]), 'CHECKPOINT' + '\"', "to File!")
        # Row, Col, Direction
        self.writeFileBuffer.append(str(loc[0]) + ' ' + str(loc[1]) + ' ' + 'CHECKPOINT' + '\n')
        self.field[loc[0]][loc[1]].checkpoint = True  # Mark Victim
        #self.filePtr.flush()

    def markVisited(self, loc=None, writeToFile=True):
        if loc is None:  # Defualt loc to current location
            loc = self.location
        print("Wrote", str(loc[0]) + ' ' + str(loc[1]) + ' ' + 'V', "to File!")
        self.field[loc[0]][loc[1]].visited = True  # Mark Victim
        if writeToFile:
            # Row, Col, Direction
            self.writeFileBuffer.append(str(loc[0]) + ' ' + str(loc[1]) + ' ' + 'V' + '\n')
           # self.filePtr.flush()

    # Marks seen victim at current location
    def markVictim(self, loc=None):
        if loc is None:  # Defualt loc to current location
            loc = self.location
        print("Wrote Victim to File at:", loc[0], loc[1])
        # Row, Col, Direction
        self.writeFileBuffer.append(str(loc[0]) + ' ' +
                           str(loc[1]) + ' ' + 'VICTIM' + '\n')
        self.field[loc[0]][loc[1]].victim = True  # Mark Victim
        #self.filePtr.flush()

    # Function if want to move up
    # if backtrack = true, only returns if you can or can't move up. If you can, then also returns coordinates
    # @return: if True, then moved will be successfull. Will then also return new coordinates. if False, then move will not be allowed.
    def canMove(self, direction, loc=None, backtrack=False):
        if loc is None:  # Defualt loc to current location
            loc = self.location
        if isinstance(direction, str):  # Convert direction to integer
            direction = direction.upper()  # uppercase everything to match formatting
            direction = self.convertDirection(direction)

        # Convert direction to adjust row & adjust col
        adjustRow = 0
        adjustCol = 0
        if direction == 0:  # Moving up
            adjustRow = 1
        elif direction == 1:  # Moving right
            adjustCol = 1
        elif direction == 2:  # Moving down
            adjustRow = -1
        else:  # Moving left
            adjustCol = -1

        newLoc = (loc[0] + adjustRow, loc[1] + adjustCol)  # Row, Col
        # If coordinates are out of bounds
        if newLoc[0] < 0 or newLoc[0] >= self.rows or newLoc[1] < 0 or newLoc[1] >= self.cols:
            return False, None
        # If there is a wall in the direction trying to go
        if self.field[loc[0]][loc[1]].wall[direction]:
            return False, None
        # If robot isn't backtracking but the new tile is already visited
        if (not backtrack) and self.field[newLoc[0]][newLoc[1]].visited:
            return False, None
        return True, newLoc

    def calculate(self):
        newDirection, newLocation, foundMove, commands = 1, (-1, -1), False, list()  # Default values
        for direction in range(0, 4):
            moveIsPossible, newLocation = self.canMove(
                ((direction + self.direction)%4), backtrack=False)
            if moveIsPossible:
                command, newDirection = self.determineCommand(self.direction, newLocation)
                commands.append(command)
                foundMove = True
                break

        if not foundMove:  # Need to BFS
            commands, newLocation, newDirection = self.backtrackBFS()

        if len(commands) == 0: # Visited all possible tiles
            commands, newLocation, newDirection = self.backtrackHomeBFS() # Then backtrack home
            if len(commands)==0:
                print("Already at home. Finishing program!")
                #Send Signal
                return []
            else:
                print("!!!GOING BACK HOME!!!")
        
        self.previousDirection = self.direction
        self.direction = newDirection  # Update Direction
        self.previousLocation = self.location  # Update previous location
        self.location = newLocation  # Update location to new location
        self.markVisited(newLocation, writeToFile=True)  # Mark new location as visited
        
        print("Commands:", commands)
        print()
        return commands

    def blackout(self):
        self.field[self.location[0]][self.location[1]].blackout()
        self.markVisited(writeToFile=True)
        for i in range(0, 4):
            self.markWall(i, writeToFile=True)
        self.location = self.previousLocation

    def markObstacle(self):
        adjustRow = 0
        adjustCol = 0
        if self.direction == 0:  # Moving up
            adjustRow = 1
        elif self.direction == 1:  # Moving right
            adjustCol = 1
        elif self.direction == 2:  # Moving down
            adjustRow = -1
        else:  # Moving left
            adjustCol = -1
        obsLocation = (self.location[0] + adjustRow, self.location[1] + adjustCol)
        self.markVisited(loc=obsLocation, writeToFile=True)
        self.field[obsLocation[0]][obsLocation[1]].blackout()
        for i in range(0, 4):
            self.markWall(i, loc=obsLocation, writeToFile=True)
        pass

    # Finds the path to the nearest unvisited tile via BFS
    # @return Returns the set of commands to reach the new location, the new location's coordinates, and the new direction. Does NOT update location & direction for you
    def backtrackBFS(self):
        print("BFS Initiated!")
        # visited = [[False]*self.cols]*self.rows  # Visited array
        visited = [[False for j in range(self.cols)] for i in range(self.rows)]
        # prevCell = [(-1, -1)*self.cols]*self.rows  # Previous cell array
        prevCell = [[[-1, -1] for j in range(self.cols)] for i in range(self.rows)]
        queue = list()
        queue.append(self.location)  # first add current location
        targetLocation = None
        while len(queue) > 0 and targetLocation == None:
            currentCell = queue.pop(0)
            visited[currentCell[0]][currentCell[1]] = True
            for direction in range(0, 4):
                moveIsPossible, newCell = self.canMove(direction, currentCell, backtrack=True)
                if moveIsPossible:
                    # if new cell is unvisited and possible to access
                    if self.field[newCell[0]][newCell[1]].visited == False:
                        prevCell[newCell[0]][newCell[1]] = (currentCell[0], currentCell[1])
                        targetLocation = newCell
                        break
                    # new cell is not in the queue and new cell has not been visited yet
                    elif (not newCell in queue) and visited[newCell[0]][newCell[1]] == False:
                        prevCell[newCell[0]][newCell[1]] = (currentCell[0], currentCell[1])
                        queue.append(newCell)
                    else:
                        pass

        if targetLocation == None:  # No more unvisited tiles
            return [], (-10000, -10000), -1  # return none to indicate go back home

        # Now it's time to backtrack each location! One by One!
        locations = [targetLocation]
        newPosition = list(targetLocation)
        while newPosition != self.location:
            newPosition = prevCell[newPosition[0]][newPosition[1]]
            locations.append(newPosition)
        locations.reverse()

        self.location = tuple(locations[len(locations)-2])

        # With each tile's coordinates on the path, we can now calculate the commands
        commands = list()
        currentPosition = locations[0]
        currentDirection = self.direction
        i = 1
        while i < len(locations):
            newPosition = locations[i]
            command, newDirection = self.determineCommand(currentDirection, newPosition, oldPosition=currentPosition)
            commands.append(command)
            currentPosition = newPosition
            currentDirection = newDirection
            i += 1

        return commands, currentPosition, currentDirection

    # Finds the path to the nearest unvisited tile via BFS
    # @return Returns the set of commands to reach the new location, the new location's coordinates, and the new direction. Does NOT update location & direction for you
    def backtrackHomeBFS(self):
        print("Home:", self.initialPosition)
        if self.location == self.initialPosition:
            return [], self.initialPosition, self.direction
        print("BFS Home Initiated!")
        # visited = [[False]*self.cols]*self.rows  # Visited array
        visited = [[False for j in range(self.cols)] for i in range(self.rows)]
        # prevCell = [(-1, -1)*self.cols]*self.rows  # Previous cell array
        prevCell = [[[-1, -1] for j in range(self.cols)] for i in range(self.rows)]
        queue = list()
        queue.append(self.location)  # first add current location
        while len(queue) > 0:
            currentCell = queue.pop(0)
            visited[currentCell[0]][currentCell[1]] = True
            for direction in range(0, 4):
                moveIsPossible, newCell = self.canMove(direction, currentCell, backtrack=True)
                if moveIsPossible:
                    # if new cell is the home tile and possible to access
                    if self.field[newCell[0]][newCell[1]].visited == False:
                        prevCell[newCell[0]][newCell[1]] = (currentCell[0], currentCell[1])
                        break
                    # new cell is not in the queue and new cell has not been visited yet
                    elif (not newCell in queue) and visited[newCell[0]][newCell[1]] == False:
                        prevCell[newCell[0]][newCell[1]] = (currentCell[0], currentCell[1])
                        queue.append(newCell)
                    else:
                        pass

        # Now it's time to backtrack each location! One by One!
        locations = [self.initialPosition]
        newPosition = list(self.initialPosition)
        while newPosition != self.location:
            newPosition = prevCell[newPosition[0]][newPosition[1]]
            locations.append(newPosition)
        locations.reverse()

        # With each tile's coordinates on the path, we can now calculate the commands
        commands = list()
        currentPosition = locations[0]
        currentDirection = self.direction
        i = 1
        while i < len(locations):
            newPosition = locations[i]
            command, newDirection = self.determineCommand(currentDirection, newPosition, oldPosition=currentPosition)
            commands.append(command)
            currentPosition = newPosition
            currentDirection = newDirection
            i += 1

        return commands, currentPosition, currentDirection
