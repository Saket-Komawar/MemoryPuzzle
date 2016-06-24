#Importing Useful Modules required for MemoryPuzzle
import pygame, sys, random
from pygame.locals import *

#Syntactic Sugars
FPS = 30
REVEALSPEED = 8
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 40
GAPSIZE = 10
COLUMNS = 10 #No. of icons in a column 
ROWS = 7 #NO.of icons in a row

#Checking for Code Dump
assert (COLUMNS * ROWS) % 2 == 0, "Board needs to have even number of boxs for pairs of matches"
XMARGIN = int((WINDOWWIDTH - (COLUMNS * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (ROWS * (BOXSIZE + GAPSIZE))) / 2)

#Colors
#		     R	  G	   B
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

#Elements Color
BACKGROUNDCOLOR = NAVYBLUE
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE
LIGHTBGOUNDCOLOR = GRAY

#Shapes
DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

#Checking for Code Dump
ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= COLUMNS * ROWS, "Board is too big for the number of shapes/colors defined."

#Main Function
def main():
	global FpsClock, DISPLAYSURF
	
	pygame.init()
	
	FpsClock = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	pygame.display.set_caption('Memory Puzzle')

	mousex = 0 # used to store x coordinate of mouse event
	mousey = 0 # used to store y coordinate of mouse event
	
	MainBoard = GetRandomizedBoard()
	RevealedBoxes = GenerateRevealedBoxesData(False) 

	FirstSelection = None
	
	DISPLAYSURF.fill(BACKGROUNDCOLOR)
	StartGameAnimation(MainBoard)

	#Game Loop
		#Game States
			#MainBoard
			#RevealedBoxes
			#FirstSelection
			#MouseClicked
			#mousex
			#mousey
	while True:
		MouseClicked = False
		
		DISPLAYSURF.fill(BACKGROUNDCOLOR)
		DrawBoard(MainBoard, RevealedBoxes)

		#Event Handling Loop
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.type == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mousex, mousey = event.pos
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				MouseClicked = True

		boxx, boxy = GetBoxAtPixel(mousex, mousey)
		if boxx != None and boxy != None:
			#The Mouse is currently over a box
			if not RevealedBoxes[boxx][boxy]:
				DrawHighlightBox(boxx, boxy)
			if not RevealedBoxes[boxx][boxy] and MouseClicked:
				RevealBoxesAnimation(MainBoard, [(boxx, boxy)])
				RevealedBoxes[boxx][boxy] = True
				if FirstSelection == None:
					FirstSelection = (boxx, boxy)
				else:
					Icon1Shape, Icon1Color = GetShapeAndColor(MainBoard, FirstSelection[0], FirstSelection[1])
					Icon2Shape, Icon2Color = GetShapeAndColor(MainBoard, boxx, boxy)

					if Icon1Shape != Icon2Shape or Icon1Color != Icon2Color:
						#Boxes aren't same
						pygame.time.wait(1000) #1sec
						CoverBoxesAnimation(MainBoard, [(FirstSelection[0], FirstSelection[1]), (boxx, boxy)])
						RevealedBoxes[FirstSelection[0]][FirstSelection[1]] = False
						RevealedBoxes[boxx][boxy] = False
					elif HasWon(RevealedBoxes):
						GameWonAnimation(MainBoard)
						pygame.time.wait(2000)

						#Reset the Board
						MainBoard = GetRandomizedBoard()
						RevealedBoxes = GenerateRevealedBoxesData(False)

						#Show fully unrevealed Board for a second
						DrawBoard(MainBoard, RevealedBoxes)
						pygame.display.update()
						pygame.time.wait(1000)

						#Repaly the start Game Animation
						StartGameAnimation(MainBoard)
					FirstSelection = None
		#Redraw the Screen and wait for the next tick
		pygame.display.update()
		FpsClock.tick(FPS)

def GenerateRevealedBoxesData(val):
	revealedBoxes = []
	for i in range(COLUMNS):
		revealedBoxes.append([val] * ROWS)
	return revealedBoxes

def GetRandomizedBoard():
	#List of icons of every possible shape in every possible color
	icons = []
	for color in ALLCOLORS:
		for shape in ALLSHAPES:
			icons.append((shape, color))
	random.shuffle(icons) #Shuffles the icons list
	NumIconsUsed = int((COLUMNS * ROWS) / 2)
	icons = icons[:NumIconsUsed] * 2
	random.shuffle(icons)

	#Create the board data structure randomly
	board = []
	for i in range(COLUMNS):
		column = []
		for r in range(ROWS):
			column.append(icons[0])
			del icons[0] 
		board.append(column)
	return board

def SplitIntoGroupsOf(groupsize, thelist):
	result = []
	for i in range(0, len(thelist), groupsize):
		result.append(thelist[i:i + groupsize])
	return result

def LeftTopCoordsOfBox(bx, by):
	left = bx * (BOXSIZE + GAPSIZE) + XMARGIN
	top = by * (BOXSIZE + GAPSIZE) + YMARGIN
	return(left, top)

def GetBoxAtPixel(x, y):
	for bx in range(COLUMNS):
		for by in range(ROWS):
			left, top = LeftTopCoordsOfBox(bx, by)
			BoxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
			if BoxRect.collidepoint(x, y):
				return(bx, by)
	return(None, None)

#To Draw Icons with given shape, color and position
def DrawIcon(shape, color, bx, by):
	left, top = LeftTopCoordsOfBox(bx, by)
	quarter = int(BOXSIZE * 0.25) #Syntactic Sugar
	half = int(BOXSIZE * 0.5) #Syntactic Sugar
	#Draw Shapes
	if shape == DONUT:
		pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
		pygame.draw.circle(DISPLAYSURF, BACKGROUNDCOLOR, (left + half, top + half), quarter - 5)
	elif shape == SQUARE:
		pygame.draw.rect(DISPLAYSURF, color, (left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
	elif shape == DIAMOND:
		pygame.draw.polygon(DISPLAYSURF, color, ((left + half, top), (left + (BOXSIZE - 1), top + half), (left + half, top + (BOXSIZE - 1)), (left, top + half)))
	elif shape == LINES:
		right = left + BOXSIZE
		bottom = top + BOXSIZE
		for i in range(0, BOXSIZE, 4):
			pygame.draw.line(DISPLAYSURF, color, (left + i, top), (left, top + i))
			pygame.draw.line(DISPLAYSURF, color, (right - i, bottom), (right, bottom - i))
		pygame.draw.line(DISPLAYSURF, color, (left + BOXSIZE, top), (left, top + BOXSIZE))
	elif shape == OVAL:
		pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))

def GetShapeAndColor(board, bx, by):
	#Returns shape and color
	return board[bx][by][0], board[bx][by][1]	

#HighLights the Covered Box
def DrawHighlightBox(bx, by):
	left, top = LeftTopCoordsOfBox(bx, by)
	pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def DrawBoxCovers(board, boxes, coverage):
	# Draws boxes being covered/revealed. "boxes" is a list
	# of two-item lists, which have the x & y spot of the box.
	for box in boxes:
		left, top = LeftTopCoordsOfBox(box[0], box[1])
		pygame.draw.rect(DISPLAYSURF, BACKGROUNDCOLOR, (left, top, BOXSIZE, BOXSIZE))
		shape, color = GetShapeAndColor(board, box[0], box[1])
		DrawIcon(shape, color, box[0], box[1])
		if coverage > 0:
			pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
	pygame.display.update()
	FpsClock.tick(FPS)

def RevealBoxesAnimation(board, boxestoreveal):
	for coverage in range(BOXSIZE, -REVEALSPEED - 1, -REVEALSPEED):
		DrawBoxCovers(board, boxestoreveal, coverage)

def CoverBoxesAnimation(board, boxestocover):
	for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
		DrawBoxCovers(board, boxestocover, coverage)

def DrawBoard(board, revealed):
	for bx in range(COLUMNS):
		for by in range(ROWS):
			left, top = LeftTopCoordsOfBox(bx, by)
			if not revealed[bx][by]:
				pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
			else:
				shape, color = GetShapeAndColor(board, bx, by)
				DrawIcon(shape, color, bx, by)

def StartGameAnimation(board):
	coveredboxes = GenerateRevealedBoxesData(False)
	boxes = []
	for x in range(COLUMNS):
		for y in range(ROWS):
			boxes.append((x, y))
	random.shuffle(boxes)
	BoxGroups = SplitIntoGroupsOf(8, boxes)
	DrawBoard(board, coveredboxes)
	for BoxGroup in BoxGroups:
		RevealBoxesAnimation(board, BoxGroup)
		CoverBoxesAnimation(board, BoxGroup)

def GameWonAnimation(board):
	coveredboxes = GenerateRevealedBoxesData(True)
	color1 = LIGHTBGOUNDCOLOR
	color2 = BACKGROUNDCOLOR

	for i in range(15):
		color1, color2 = color2, color1
		DISPLAYSURF.fill(color1)
		DrawBoard(board, coveredboxes)
		pygame.display.update()
		pygame.time.wait(300)

def HasWon(revealedboxes):		
	for i in revealedboxes:
		if False in i:
			return False
	return True

if __name__ == "__main__":
	main()
