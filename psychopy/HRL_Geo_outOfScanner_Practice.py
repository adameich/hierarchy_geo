from __future__ import division
from matplotlib import pyplot as plt
from psychopy import core, visual, data, event, parallel, monitors
from psychopy import gui
from psychopy import sound
from psychopy.tools.filetools import fromFile, toFile
from pyglet.window import key 
import time, random, os, sys, serial, ctypes, itertools
import numpy as np
from PIL import Image, ImageDraw
import copy as copy
import os.path
from math import atan2, degrees
import pandas as pd
import itertools

def Pres_stim(Boarder_Shape, Aperture, Imgage_Stimulus, Washout_Filter, conf = False):
    Boarder_Shape.draw()
    Aperture.enabled = True
    Imgage_Stimulus.draw()
    Washout_Filter.draw()
    Aperture.enabled = False
    if conf != False:
        conf.draw()

def main(argv = sys.argv):
    TESTMODE = False
    skipP1 = False

    data_dir_root = '/Users/Eichenbaum/HWNI/Experiments/HRL_Geometry/scripts/psychopy'

    d = 57 # Distance between monitor and participant in cm  ## This scales everything that is coded in degrees!

    my_monitor = monitors.Monitor(name='DesktopLab')
    my_monitor.setSizePix((1920,1080)) # (2560,1440) (1024, 768) (1920,1080)## This scales everything that is coded in degrees!
    my_monitor.setDistance(d)  ## This scales everything that is coded in degrees!
    my_monitor.setWidth(50.88)  ## This scales everything that is coded in degrees!
    my_monitor.saveMon()
    
    monitor = 'DesktopLab'
    res = [1024, 768] # [1920,1080] [1024, 768]

    if not TESTMODE:
        SubID = str(sys.argv[1]) # str(expInfo['SubID'])
        Age = int(sys.argv[2]) # int(expInfo['Age'])
        Gen = str(sys.argv[3]) # str(expInfo['Gender'])
        Date = str(data.getDateStr()) # ['DateTime'])
    else:
        SubID = str(sys.argv[1]) # str(expInfo['SubID'])
        Age = int(sys.argv[2]) # int(expInfo['Age'])
        Gen = str(sys.argv[3]) # str(expInfo['Gender'])
        Date = str(data.getDateStr()) # ['DateTime'])
    
    CounterBalanceNumber = int(SubID) % 4
    
    win = visual.Window(res, fullscr = True, monitor = monitor, color = [-.375, -.375, -.375], units = 'deg', allowStencil = True)
    
    # Shared Parameter Values#
    h = 28.62 # 34.544 # Monitor height in cm
    r = win.size[1] # Vertical resolution of the monitor
    deg_per_px = degrees(atan2(.5*h, d)) / (.5*r) # Calculate the number of degrees that correspond to a single pixel. This will generally be a very small value, something like 0.03.    

    #########################################################################
    ######## Data file creation for trial info and user response info #######
    #########################################################################    
    file_name = SubID + '_HRL_Geo_Practice_outside'
    complete_file_name = os.path.join(data_dir_root, 'data', file_name + '.csv')
    HRLDataFile = open(complete_file_name,'w')
    firstLine =['DateTime', ### The Date and Time at the start of the session.
                'SubID', ###### The 3-digit numeric code given to the participant
                'Round', ###### The number of times the participant fails to meet criterion performance (0-based)
                'tAns', ####### The correct answer for the current trial. Will be a string of either 'v', 'b', 'n', or 'm'.
                'tOut', ####### Whether the response was Correct (1), Incorrect (-1), or No Response provided ('Nan') 
                'StimIdx' ##### The number associated with that stimulus conjunction. This will be a good cross check to make sure that everything is coding appropriately for e.g. numSince
    ]
    firstLine = ','.join(firstLine)
    HRLDataFile.write(firstLine+'\n')

    ########################
    ## Drawing Parameters ##
    ########################
    wrapWidth = 22.5
    line_width_val = 0.0
    stim_rad = 5.0 *.8
    opa_val = 1.0
    rect_width = 10.0 *.8 
    rect_height = 10.0 *.8  
    size = .4 # How large everything will be from the aperture perspective
    border_size_boost = 1.3 
    text_win_size = .55 #.75
    
    ### Colors ###
    RGB_colors = (np.array([(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]) - 127.5) / 127.5 
    tutorial_colors = (np.array([(0,255,0), (0,0,128)]) - 127.5 ) / 127.5
    rgbNames = ['red', 'blue', 'yellow', 'magenta'] 

    ### Texture Images used ###
    texIdx_array = np.array((11, 37, 65, 87)) #Brodatz image idxs

    ###############################
    ## Block Creation Parameters ##
    ###############################
    nDims = 3
    
    #######################
    ## Timing Parameters ##
    #######################
    feedbackDur = .333 # how long should the visual feedback remain on screen
    RespDurLimit, RespDurClock = 2.0, core.Clock() # 120 frames will allow the subject to respond within a 2000ms window. 
    myOverallClock=core.Clock() # clock used for overall stimulus timing throughout the experiment
    fb_demo_clock = core.Clock()
    TTL_start_clock = core.Clock()
    timingClock = core.Clock()
    Feedback_Delay_Duration = .167
    practice_ITI = 2

    #########################
    ## Response Parameters ##
    #########################
    keyState=key.KeyStateHandler() 
    win.winHandle.push_handlers(keyState) 
    actions = [0,1,2,3]
    answer_keys_bBox = ['1', '2', '3', '4']
    answer_keys = ['v','b','n','m']

    ########################
    ##  Circle Stimulus   ##
    ########################
    circle = visual.Circle(     win, size = size,                             radius = stim_rad, units = 'deg', lineWidth = line_width_val, edges = 256, opacity = opa_val, interpolate = True,name = 'circle')
    circle2 = visual.Circle(    win, size = size * border_size_boost * 0.9,   radius = stim_rad, units = 'deg', lineWidth = line_width_val, edges = 256, opacity = opa_val, interpolate = True)
    circle3 = visual.Circle(    win, size = size * 0.8,                       radius = stim_rad, units = 'deg', lineWidth = line_width_val, edges = 256, opacity = opa_val, interpolate = True)
    ########################
    ##  Square Stimulus   ##
    ########################
    square = visual.Rect(       win, size = size,                             width = rect_width, height = rect_height, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True, name = 'square')
    square2 = visual.Rect(      win, size = size * border_size_boost * 0.9,   width = rect_width, height = rect_height, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True)
    square3 = visual.Rect(      win, size = size * .8,                        width = rect_width, height = rect_height, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True)
    ########################
    ## Triangle Stimulus  ##
    ########################
    triangle = visual.Polygon(  win, size = size,                           edges = 3.0, radius = 6.0, units = 'deg', pos = (0,-.1),  lineWidth = line_width_val, opacity = opa_val, interpolate = True, name = 'triangle')
    triangle2 = visual.Polygon( win, size = size * border_size_boost*.95,   edges = 3.0, radius = 6.0, units = 'deg', pos = (0,-.1),  lineWidth = line_width_val, opacity = opa_val, interpolate = True)
    triangle3 = visual.Polygon( win, size = size * .8,                      edges = 3.0, radius = 6.0, units = 'deg', pos = (0,-.25), lineWidth = line_width_val, opacity = opa_val, interpolate = True)
    ########################
    ## Pentagon Stimulus  ##
    ########################
    pentagon = visual.Polygon(  win, size = size,                             edges = 5.0, radius = stim_rad, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True, name = 'pentagon')
    pentagon2 = visual.Polygon( win, size = size * border_size_boost * 0.925, edges = 5.0, radius = stim_rad, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True)
    pentagon3 = visual.Polygon( win, size = size * .8,                        edges = 5.0, radius = stim_rad, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True)
    #####################
    ## Wash-out Filter ##
    #####################
    washOut_Filter = visual.Rect(win, width = win.size[0], height = win.size[1], units = 'pix', lineWidth = line_width_val, fillColor = [1,1,1], opacity = .1, interpolate = True)

    #####################
    ## (Tut.)  Diamond ##
    #####################
    vees = np.ones((4,2)) * np.nan
    for idx, tmp in enumerate([0,90,180,270]):
         vees[idx, 0] = ((5*np.sqrt(2)) * np.sin(np.deg2rad(tmp)))
         vees[idx, 1] = ((5*np.sqrt(2)) * np.cos(np.deg2rad(tmp)))
    diamond = visual.Rect(      win, size = size*.8,                                width = rect_width, height = rect_height, units = 'deg', lineWidth = line_width_val, opacity = opa_val, ori = 45.0, interpolate = True, name = 'diamond')
    diamond2 = visual.Rect(     win, size = .9*(size * border_size_boost * 0.95),   width = rect_width, height = rect_height, units = 'deg', lineWidth = line_width_val, opacity = opa_val, ori = 45.0, interpolate = True)
    #####################
    ## (Tut.)  Octagon ##
    #####################
    octagon = visual.Polygon(   win, size = size,                           edges = 8.0, radius = stim_rad, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True, name = 'pentagon')
    octagon2 = visual.Polygon(  win, size = size * border_size_boost * 0.9, edges = 8.0, radius = stim_rad, units = 'deg', lineWidth = line_width_val, opacity = opa_val, interpolate = True)

    ### Create Fixation Cross ###
    fixation1w = visual.Line(    win, units = 'deg', start = (0, -0.35), end = (0, 0.35), lineColor = 'white', lineWidth = 4)
    fixation2w = visual.Line(    win, units = 'deg', start = (-0.35, 0), end = (0.35, 0), lineColor = 'white', lineWidth = 4)

    ### Shapes ###
    shape_list = [circle, square, triangle, pentagon] # [circle, square, rectangle, triangle, pentagon, rhombus, trapezoid, star_six, oval, piri]
    shape_list2 = [circle2, square2, triangle2, pentagon2] # [circle2, square2, rectangle2, triangle2, pentagon2, rhombus2, trapezoid2, star_six2, oval2, piri2]
    shape_list3 = [circle3, square3, triangle3, pentagon3] # [circle3, square3, rectangle3, triangle3, pentagon3, rhombus3, trapezoid3,  oval3, star_six3, piri3]
    Shape_list_wTut = [octagon, diamond]
    Shape_list_wTut2 = [octagon2, diamond2]

    Positive_Feedback = visual.TextStim(win, height = text_win_size, units = 'deg', alignHoriz = 'center', alignVert = 'center',    text = '      $$$\nCORRECT',    color = 'black')
    Negative_Feedback = visual.TextStim(win, height = text_win_size, units = 'deg',                                                 text = 'INCORRECT',             color = 'black')
    MissTrialFeedback = visual.TextStim(win, height = text_win_size, units = 'deg',                                                 text = 'NO RESPONSE',           color = 'black')


    if CounterBalanceNumber == 0:
        CB_vals = [1,2]
        currShapeList1 = [circle, triangle]
        currShapeList2 = [circle2, triangle2]
        currShapeList3 = [circle3, triangle3]
        order = 0 # Sot-Cot

    elif CounterBalanceNumber == 1:
        CB_vals = [0,3]
        currShapeList1 = [square, pentagon]
        currShapeList2 = [square2, pentagon2]
        currShapeList3 = [square3, pentagon3]
        order = 0 # Sot-Cot

    elif CounterBalanceNumber == 2:
        CB_vals = [1,2]
        currShapeList1 = [circle, triangle]
        currShapeList2 = [circle2, triangle2]
        currShapeList3 = [circle3, triangle3]
        order = 1 # Cot-Sot

    elif CounterBalanceNumber == 3:
        CB_vals = [0,3]
        currShapeList1 = [square, pentagon]
        currShapeList2 = [square2, pentagon2]
        currShapeList3 = [square3, pentagon3]
        order = 1 # Cot-Sot
    

    currTexList = texIdx_array[CB_vals]
    currColList = RGB_colors[CB_vals]

    ##########################################################################
    ## Construct General Trial Array for Rule / Context #1 ==> Shape on Top ##
    ##########################################################################
    trialArray_SoT = np.zeros((2**nDims, 5))*np.nan
    trialArray_SoT[:,0] = [0,0,0,0,1,1,1,1] # Shape
    trialArray_SoT[:,1] = [0,0,1,1,0,0,1,1] # Color
    trialArray_SoT[:,2] = [0,1,0,1,0,1,0,1] # Texture
    trialArray_SoT[:,3] = [0,0,2,2,1,3,1,3] # Answer # 
    trialArray_SoT[:,4] = [0,1,2,3,4,5,6,7] # Unique Stim ID


    ##########################################################################
    ## Construct General Trial Array for Rule / Context #2 ==> Color on Top ##
    ##########################################################################
    trialArray_CoT = np.zeros((2**nDims, 5))*np.nan
    trialArray_CoT[:,0] = [0,0,0,0,1,1,1,1] # Shape
    trialArray_CoT[:,1] = [0,0,1,1,0,0,1,1] # Color
    trialArray_CoT[:,2] = [0,1,0,1,0,1,0,1] # Texture
    trialArray_CoT[:,3] = [2,1,3,3,2,1,0,0] # Answer 
    trialArray_CoT[:,4] = [0,1,2,3,4,5,6,7] # Unique Stim ID

    #############################################################################
    ## Construct Trial Array for Round 1 of Practice (4 repetitions / context) ##
    #############################################################################
    trialArray_SoT_Practice1 = np.zeros((trialArray_SoT.shape[0] * 4, trialArray_SoT.shape[1]))*np.nan
    tmp_p_SoT_1a = []
    tmp_p_SoT_1b = []
    tmp_p_SoT_1a = np.tile(trialArray_SoT[:,:],[2,1]) 
    tmp_p_SoT_1b = np.tile(trialArray_SoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_SoT_1a)
    np.random.shuffle(tmp_p_SoT_1b)
    trialArray_SoT_Practice1[0:16,:] = tmp_p_SoT_1a
    trialArray_SoT_Practice1[16:32,:] = tmp_p_SoT_1b

    trialArray_CoT_Practice1 = np.zeros((trialArray_CoT.shape[0] * 4, trialArray_CoT.shape[1]))*np.nan
    tmp_p_CoT_1a = []
    tmp_p_CoT_1b = []
    tmp_p_CoT_1a = np.tile(trialArray_CoT[:,:],[2,1]) 
    tmp_p_CoT_1b = np.tile(trialArray_CoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_CoT_1a)
    np.random.shuffle(tmp_p_CoT_1b)
    trialArray_CoT_Practice1[0:16,:] = tmp_p_CoT_1a
    trialArray_CoT_Practice1[16:32,:] = tmp_p_CoT_1b

    #############################################################################
    ## Construct Trial Array for Round 2 of Practice (4 repetitions / context) ##
    #############################################################################
    trialArray_SoT_Practice2 = np.zeros((trialArray_SoT.shape[0] * 4, trialArray_SoT.shape[1]))*np.nan
    tmp_p_SoT_2a = []
    tmp_p_SoT_2b = []
    tmp_p_SoT_2a = np.tile(trialArray_SoT[:,:],[2,1]) 
    tmp_p_SoT_2b = np.tile(trialArray_SoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_SoT_2a)
    np.random.shuffle(tmp_p_SoT_2b)
    trialArray_SoT_Practice2[0:16,:] = tmp_p_SoT_2a
    trialArray_SoT_Practice2[16:32,:] = tmp_p_SoT_2b

    trialArray_CoT_Practice2 = np.zeros((trialArray_CoT.shape[0] * 4, trialArray_CoT.shape[1]))*np.nan
    tmp_p_CoT_2a = []
    tmp_p_CoT_2b = []
    tmp_p_CoT_2a = np.tile(trialArray_CoT[:,:],[2,1]) 
    tmp_p_CoT_2b = np.tile(trialArray_CoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_CoT_2a)
    np.random.shuffle(tmp_p_CoT_2b)
    trialArray_CoT_Practice2[0:16,:] = tmp_p_CoT_2a
    trialArray_CoT_Practice2[16:32,:] = tmp_p_CoT_2b

    #############################################################################
    ## Construct Trial Array for Round 3 of Practice (2 repetitions / context) ##
    #############################################################################
    trialArray_SoT_Practice3 = np.zeros((trialArray_SoT.shape[0] * 2, trialArray_SoT.shape[1]))*np.nan
    tmp_p_SoT_3 = []
    tmp_p_SoT_3 = np.tile(trialArray_SoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_SoT_3)
    trialArray_SoT_Practice3 = tmp_p_SoT_3

    trialArray_CoT_Practice3 = np.zeros((trialArray_CoT.shape[0] * 2, trialArray_CoT.shape[1]))*np.nan
    tmp_p_CoT_3 = []
    tmp_p_CoT_3 = np.tile(trialArray_CoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_CoT_3)
    trialArray_CoT_Practice3 = tmp_p_CoT_3

    #####################################################################################
    ## Construct Trial Array for Round 4 of Practice (3 full runs (2 x 2) w/ feedback) ##
    #####################################################################################
    trialArray_SoT_Practice4 = np.zeros((trialArray_SoT.shape[0] * 6, trialArray_SoT.shape[1]))*np.nan
    tmp_p_SoT_4a = []
    tmp_p_SoT_4b = []
    tmp_p_SoT_4c = []
    tmp_p_SoT_4a = np.tile(trialArray_SoT[:,:],[2,1]) 
    tmp_p_SoT_4b = np.tile(trialArray_SoT[:,:],[2,1]) 
    tmp_p_SoT_4c = np.tile(trialArray_SoT[:,:],[2,1])  
    np.random.shuffle(tmp_p_SoT_4a)
    np.random.shuffle(tmp_p_SoT_4b)
    np.random.shuffle(tmp_p_SoT_4c)
    trialArray_SoT_Practice4[0:16,:] = tmp_p_SoT_4a
    trialArray_SoT_Practice4[16:32,:] = tmp_p_SoT_4b
    trialArray_SoT_Practice4[32:48,:] = tmp_p_SoT_4c

    trialArray_CoT_Practice4 = np.zeros((trialArray_CoT.shape[0] * 6, trialArray_CoT.shape[1]))*np.nan
    tmp_p_CoT_4a = []
    tmp_p_CoT_4b = []
    tmp_p_CoT_4c = []
    tmp_p_CoT_4a = np.tile(trialArray_CoT[:,:],[2,1]) 
    tmp_p_CoT_4b = np.tile(trialArray_CoT[:,:],[2,1]) 
    tmp_p_CoT_4c = np.tile(trialArray_CoT[:,:],[2,1])  
    np.random.shuffle(tmp_p_CoT_4a)
    np.random.shuffle(tmp_p_CoT_4b)
    np.random.shuffle(tmp_p_CoT_4c)
    trialArray_CoT_Practice4[0:16,:] = tmp_p_CoT_4a
    trialArray_CoT_Practice4[16:32,:] = tmp_p_CoT_4b
    trialArray_CoT_Practice4[32:48,:] = tmp_p_CoT_4b

    #######################################################################################
    ## Construct Trial Array for Round 5 of Practice (1 full run (2 x 2) w/out feedback) ##
    #######################################################################################
    trialArray_SoT_Practice5 = np.zeros((trialArray_SoT.shape[0] * 2, trialArray_SoT.shape[1]))*np.nan
    tmp_p_SoT_5a = []
    tmp_p_SoT_5a = np.tile(trialArray_SoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_SoT_5a)
    trialArray_SoT_Practice5[0:16,:] = tmp_p_SoT_5a

    trialArray_CoT_Practice5 = np.zeros((trialArray_CoT.shape[0] * 2, trialArray_CoT.shape[1]))*np.nan
    tmp_p_CoT_5a = []
    tmp_p_CoT_5a = np.tile(trialArray_CoT[:,:],[2,1]) 
    np.random.shuffle(tmp_p_CoT_5a)
    trialArray_CoT_Practice5[0:16,:] = tmp_p_CoT_5a

    win.mouseVisible = False
    experimentStart = myOverallClock.getTime()

######################################
######### INSTRUCTIONS START #########
######################################

    ### Go through stimulus tutorial to present all stimuli that will be seen ###
    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = 'Welcome to the study. The goal is to press the correct button associated with each stimulus.\n\n\
On each trial you will see a single stimulus: the combination of a texture pattern in the form of a specific shape surrounded by a colored border.\n\n\n\n\n\n\n\
Here are 2 example stimuli you\n\
may see on 2 different trials:\n\n\n\n\n\n\
Press [ 1 ], [ 2 ], [ 3 ], or [ 4 ] to respond to the stimulus during the experiment.\n\n\
Please use your index, middle, ring, and pinky fingers on your right hand for [ 1 ], [ 2 ], [ 3 ], and [ 4 ], respectively.\n\n\
Press [ 4 ] to continue.').draw()
    tutShap, tutShapBrd = Shape_list_wTut[0], Shape_list_wTut2[0]
    tutImgStim = visual.ImageStim(win, units = 'deg', image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(1)))    
    tutShapBrd.setFillColor(tutorial_colors[0])
    tutAperture = visual.Aperture(win, size = size, shape = tutShap.vertices, pos = tutShap.pos)
    tutAperture.enabled = False
    Pres_stim(tutShapBrd, tutAperture, tutImgStim, washOut_Filter)

    tutShap2, tutShapBrd2 = Shape_list_wTut[1], Shape_list_wTut2[1]
    tutShap2.setPos([7.5, 0])
    tutShapBrd2.setPos([7.5,0])
    tutImgStim2 = visual.ImageStim(win=win, units = 'deg', pos = tutShap2.pos, image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(10)))    
    tutShapBrd2.setFillColor(tutorial_colors[1])
    tutAperture2 = visual.Aperture(win, size = size*.75, shape = vees,  pos = tutShap2.pos)
    tutAperture2.enabled = False
    Pres_stim(tutShapBrd2, tutAperture2, tutImgStim2, washOut_Filter)

    win.flip()
    if TESTMODE: core.wait(.5)
    else: core.wait(4)
    event.waitKeys(keyList = '4')

    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = 'On the following screen you will see the shapes, textures, and colors that will be used to make the stimuli during the experiment.\n\n\
There are 2 shapes, 2 textures, and 2 colors in total.\n\n\
[Please ignore the color of the subsequent shapes, and the shape of the colors and textures]\n\n\n\
Press [ 4 ] to reveal the shapes.').draw()
    win.flip()
    if TESTMODE: core.wait(.5)
    else: core.wait(4)
    event.waitKeys(keyList = '4')

    start_end_pos =[-2,2]
    height_val = [5,-5]
    for idx in np.arange(2):
        currShap = currShapeList3[int(idx)]
        currShap.setFillColor([-1,1,-1])
        currShap.pos = [start_end_pos[0]*3, height_val[idx]]
        currShap.draw()
    for idxI, tmp3 in enumerate(texIdx_array[CB_vals]):
        prevPos2 = [0, height_val[idxI]] 
        visual.ImageStim(win=win, size = [5, 5], units = 'deg', pos = prevPos2, image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(int(tmp3)))).draw()
    for idx2, tmp4 in enumerate(texIdx_array[CB_vals]):
        square3.pos = [start_end_pos[1]*3, height_val[idx2]] 
        square3.setFillColor(RGB_colors[CB_vals[idx2]])
        square3.draw()

    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'Press [ 4 ] to continue').draw()
    win.flip()
    if TESTMODE: core.wait(.5)
    event.waitKeys(keyList = '4')

    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = 'The experiment consists of multiple blocks, with breaks in between each block.\n\n\
All blocks will use stimuli created from the two shapes, two textures, and two colors you just saw, resulting in 8 unique stimuli.\n\n\
To reveal the stimuli you will see, press [ 4 ].').draw()
    win.flip()
    if TESTMODE: core.wait(.5)
    else: core.wait(4)
    event.waitKeys(keyList = '4')

    tmp = 0
    height_val = [5,-5]
    start_end_pos =[-10.666,10.666]
    xs = np.linspace(start_end_pos[0],start_end_pos[1],4)
    for idx, i in enumerate(np.unique(trialArray_SoT[:,2])): # Texture
        for j in np.unique(trialArray_SoT[:,0]): # Shape 
            for k in np.unique(trialArray_SoT[:,1]): # Color
                shape_val_pre = currShapeList1[int(j)] 
                shape_val_brd_pre = currShapeList2[int(j)]
                if idx == 0: 
                    shape_val_pre.pos = [xs[tmp], height_val[0]]
                    shape_val_brd_pre.pos = [xs[tmp], height_val[0]]
                elif idx ==1: 
                    shape_val_pre.pos = [xs[(tmp-4)], height_val[1]]
                    shape_val_brd_pre.pos = [xs[(tmp-4)], height_val[1]]
                ImgStim_pre = visual.ImageStim(win=win, units = 'deg', size = [10,10], pos = shape_val_pre.pos, image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(currTexList[int(i)])))
                shape_val_brd_pre.setFillColor(RGB_colors[CB_vals[int(k)]]) 
                aperture_pre = visual.Aperture(win, size = size, units = 'deg', shape = shape_val_pre.vertices, pos = shape_val_pre.pos)
                aperture_pre.enabled = False
                Pres_stim(shape_val_brd_pre, aperture_pre, ImgStim_pre, washOut_Filter)

                tmp += 1

    aperture_pre.enabled = False

    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'Press [ 4 ] to continue').draw()
    win.flip()
    if TESTMODE: core.wait(.5)
    else: core.wait(2)
    event.waitKeys(keyList = '4')

    if CounterBalanceNumber in [0,1]:
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = 'There are two rules that govern the way in which stimuli and buttons are paired.\n\n\
One rule is called "Shape-on-Top", while the other rule is called "Color-on-Top". These rules individually determine how the stimuli and button responses are paired together.\n\n\
Your job is to learn both sets of correct response pairings: one set for "Shape-on-Top" and another set for "Color-on-Top."\n\n\
You will practice these rules many times before starting the real task to make sure that you have fully learned them both.\n\n\
Press [ 4 ] to continue.').draw()
    elif CounterBalanceNumber in [2,3]:
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = 'There are two rules that govern the way in which stimuli and buttons are paired.\n\n\
One rule is called "Color-on-Top", while the other rule is called "Shape-on-Top". These rules individually determine how the stimuli and button responses are paired together.\n\n\
Your job is to learn both sets of correct response pairings: one set for "Color-on-Top" and another set for "Shape-on-Top."\n\n\
You will practice these rules many times before starting the real task to make sure that you have fully learned them both.\n\n\
Press [ 4 ] to continue.').draw()
    win.flip()
    if TESTMODE: core.wait(.5)
    else: core.wait(4)
    event.waitKeys(keyList = '4')


    text_SoT_1 = '\n\n\n\n\n\n\n\n\n\nFor the "Shape-on-Top" rule, the correct answers are determined first by the SHAPE of the stimulus.\n\n\
If the stimulus is a CIRCLE, then answers are determined by COLOR.\n\n\
Button [1] for blue                               Button [3] for yellow\n\n\n\n\
If the stimulus is a TRIANGLE, then answers are determined by the TEXTURE.\n\n\n\n\
Button [2] for                                     Button [4] for \n\n\n\n\
Press [ 4 ] to continue.'

    text_CoT_1 = '\n\n\n\n\n\n\n\n\n\nFor the "Color-on-Top" rule, the correct answers are determined first by the COLOR of the stimulus.\n\n\
If the stimulus is YELLOW, then answers are determined by SHAPE.\n\n\
Button [1] for triangles                         Button [4] for circles\n\n\n\n\
If the stimulus is BLUE, then answers are determined by the TEXTURE.\n\n\n\n\
Button [2] for                                     Button [3] for \n\n\n\n\
Press [ 4 ] to continue.'

    text_SoT_2 = '\n\n\n\n\n\n\n\n\n\nFor the "Shape-on-Top" rule, the correct answers are determined first by the SHAPE of the stimulus.\n\n\
If the stimulus is a SQUARE, then answers are determined by COLOR.\n\n\
Button [1] for red                               Button [3] for purple\n\n\n\n\
If the stimulus is a PENTAGON, then answers are determined by the TEXTURE.\n\n\n\n\
Button [2] for                                     Button [4] for \n\n\n\n\
Press [ 4 ] to continue.'

    text_CoT_2 = '\n\n\n\n\n\n\n\n\n\nFor the "Color-on-Top" rule, the correct answers are determined first by the COLOR of the stimulus.\n\n\
If the stimulus is PURPLE, then answers are determined by SHAPE.\n\n\
Button [1] for pentagons                         Button [4] for squares\n\n\n\n\
If the stimulus is RED, then answers are determined by the TEXTURE.\n\n\n\n\
Button [2] for                                     Button [3] for \n\n\n\n\
Press [ 4 ] to continue.'



    if CounterBalanceNumber == 0:
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_SoT_1).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D37.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D65.tif')).draw()
        visual.ImageStim(win,image = "Schematic_1_SoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_CoT_1).draw() 
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D65.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D37.tif')).draw()
        visual.ImageStim(win,image = "Schematic_1_CoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

    elif CounterBalanceNumber == 1:
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_SoT_2).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D11.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D87.tif')).draw()
        visual.ImageStim(win,image = "Schematic_2_SoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_CoT_2).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D87.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D11.tif')).draw()
        visual.ImageStim(win,image = "Schematic_2_CoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

    elif CounterBalanceNumber == 2:
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_CoT_1).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D65.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D37.tif')).draw()
        visual.ImageStim(win,image = "Schematic_1_CoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_SoT_1).draw() 
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D37.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D65.tif')).draw()
        visual.ImageStim(win,image = "Schematic_1_SoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

    elif CounterBalanceNumber == 3:
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_CoT_2).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D87.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D11.tif')).draw()
        visual.ImageStim(win,image = "Schematic_2_CoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')

        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, alignHoriz = 'center', text = text_SoT_2).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [-5.75,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D11.tif')).draw()
        visual.ImageStim(win=win, units = 'deg', size = [3,3], pos = [3.25,-5.5], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D87.tif')).draw()
        visual.ImageStim(win,image = "Schematic_2_SoT.tiff", pos = [0,6.6] ).draw()
        win.flip()
        if TESTMODE: core.wait(.5)
        else: core.wait(5)
        event.waitKeys(keyList = '4')        
   
    #########################################
    ### PRACTICE ROUND 1, 2, and 3 ##########
    ### [1] Hierarchy Schematic On Screen ###
    ### [1] Self Paced timing ###############
    ### [1, 2] Feedback provided ############
    #########################################
    if not skipP1:

        Chunk_1_Trial_Array = np.zeros((32, 5, 3, 2))*np.nan

        if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 1):
            Chunk_1_Trial_Array[:,:,0,0] =      trialArray_SoT_Practice1
            Chunk_1_Trial_Array[:,:,1,0] =      trialArray_SoT_Practice2
            Chunk_1_Trial_Array[0:16,:,2,0] =   trialArray_SoT_Practice3
            Chunk_1_Trial_Array[:,:,0,1] =      trialArray_CoT_Practice1
            Chunk_1_Trial_Array[:,:,1,1] =      trialArray_CoT_Practice2
            Chunk_1_Trial_Array[0:16,:,2,1] =   trialArray_CoT_Practice3

        elif np.logical_or(CounterBalanceNumber == 2, CounterBalanceNumber == 3):
            Chunk_1_Trial_Array[:,:,0,0] =      trialArray_CoT_Practice1
            Chunk_1_Trial_Array[:,:,1,0] =      trialArray_CoT_Practice2
            Chunk_1_Trial_Array[0:16,:,2,0] =   trialArray_CoT_Practice3
            Chunk_1_Trial_Array[:,:,0,1] =      trialArray_SoT_Practice1
            Chunk_1_Trial_Array[:,:,1,1] =      trialArray_SoT_Practice2
            Chunk_1_Trial_Array[0:16,:,2,1] =   trialArray_SoT_Practice3

        win.flip()

        ########################################################################################################################
        ### This is the first chunk of practice. This chunk includes Rounds 1, 2, and 3, which will be considered as blocks. ###
        ### In addition, there will be an additional block (n=2) that determines whether the current Rounds are Sot or Cot. ####
        ########################################################################################################################
        
        for Context in np.arange(2):
            if np.logical_and(Context == 0, order == 0):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 1 of practice. In this round, you will learn which button is paired with each stimulus.\n\n\
The correct mappings will be shown on every trial at the top of the screen.\n\n\
Unlike the real experiment, these trials are self-paced and you will not be forced to make a response within 2 seconds of the stimulus appearing on screen.\n\n\
In addition, you will be told if the button press you made was correct or incorrect following every trial.\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
The current Rule = "Shape on Top"\n\n\
Press Any Key to Begin').draw()
                win.flip()
                if TESTMODE: core.wait(.5)
                else: core.wait(4)
                event.waitKeys()
                if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 2):
                    schematic = "Schematic_1_SoT.tiff"
                else: 
                    schematic = "Schematic_2_SoT.tiff"

            if np.logical_and(Context == 0, order == 1):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 1 of practice. In this first round, you will have to press the correct button associated with each stimulus.\n\n\
The correct mappings will be shown on every trial at the top of the screen.\n\n\
Unlike the real experiment, these trials are self-paced and you will not be forced to make a response within 2 seconds of the stimulus appearing on screen.\n\n\
In addition, you will be told if the button press you made was correct or incorrect following every trial.\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
The current Rule = "Color on Top"\n\n\
Press Any Key to Begin').draw()
                win.flip()
                if TESTMODE: core.wait(.5)
                else: core.wait(4)
                event.waitKeys()
                if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 2):
                    schematic = "Schematic_1_CoT.tiff"
                else: 
                    schematic = "Schematic_2_CoT.tiff"

            if np.logical_and(Context == 1, order == 0):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'We are now going to practice a NEW rule, but still use the same stimuli as before.\n\n\
This is Round 1 of practice.\n\n\
The correct mappings will be shown on every trial at the top of the screen.\n\n\
Unlike the real experiment, these trials are self-paced and you will not be forced to make a response within 2 seconds of the stimulus appearing on screen.\n\n\
In addition, you will be told if the button press you made was correct or incorrect following every trial.\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
The NEW Rule = "Color on Top"\n\n\
Press Any Key to Begin').draw()
                win.flip()
                if TESTMODE: core.wait(.5)
                else: core.wait(4)
                event.waitKeys()
                if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 2):
                    schematic = "Schematic_1_CoT.tiff"
                else: 
                    schematic = "Schematic_2_CoT.tiff"

            if np.logical_and(Context == 1, order == 1):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'We are now going to practice a NEW rule, but still use the same stimuli as before.\n\n\
This is Round 1 of practice.\n\n\
The correct mappings will be shown on every trial at the top of the screen.\n\n\
Unlike the real experiment, these trials are self-paced and you will not be forced to make a response within 2 seconds of the stimulus appearing on screen.\n\n\
In addition, you will be told if the button press you made was correct or incorrect following every trial.\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
The NEW Rule = "Shape on Top"\n\n\
Press Any Key to Begin').draw()
                win.flip()
                if TESTMODE: core.wait(.5)
                else: core.wait(4)
                event.waitKeys()
                if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 2):
                    schematic = "Schematic_1_SoT.tiff"
                else: 
                    schematic = "Schematic_2_SoT.tiff"

            for Round in np.arange(3):
                crit_notPassed = True
                while crit_notPassed:         

                    if Round == 1:
                        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 2 of practice.\n\n\
The correct mappings WILL NOT be shown on every trial at the top of the screen anymore.\n\n\
In addition, the trials are NOT self-paced: you must make a response within 2 seconds of the stimulus appearing on screen.\n\n\
You will still be told if the button press you made was correct or incorrect following every trial.\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
Press Any Key to Begin').draw()
                        win.flip()
                        if TESTMODE: core.wait(.5)
                        else: core.wait(4)
                        event.waitKeys()

                    elif Round == 2:
                        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 3 of practice.\n\n\
You will NO LONGER be told if the button press you made was correct or incorrect following every trial.\n\n\
To progress past this round, you CANNOT get more than 3 incorrect or missed response trials. Failure to meet this criterion will result in performing this round again\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
Press Any Key to Begin').draw()
                        win.flip()
                        if TESTMODE: core.wait(.5)
                        else: core.wait(4)
                        event.waitKeys()
                    
                    if np.logical_or(Round == 0, Round == 1):
                        current_block_trial_matrix = Chunk_1_Trial_Array[:, :, Round, Context]
                    elif Round == 2:
                        current_block_trial_matrix = Chunk_1_Trial_Array[0:16, :, Round, Context]

                    win.flip()
    
                    tOUT_tmp = 0
                    for trial in np.arange(current_block_trial_matrix.shape[0]): 
                        
                        buttonPressed = None
                        resp, new_Resp, new_new_resp, Resp1Time, Resp2Time, ConfRelease, ConfReleaseRT, Response1_On = False, False, False, False, False, False, False, False
                        full_Ck = 0

                        ### Determine which shape will be drawn on this trial ###
                        shape_val = currShapeList1[current_block_trial_matrix[trial,0].astype(int)] 
                        shape_val_brd = currShapeList2[current_block_trial_matrix[trial,0].astype(int)] 
                        
                        shape_val.setPos([0,0]) 
                        shape_val_brd.setPos([0,0]) 
                        
                        ### Create the Texture Visual Patch ### 
                        imgstim = visual.ImageStim(win=win, pos = shape_val.pos, size = [10,10], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(currTexList[current_block_trial_matrix[trial,2].astype(int)]))) 
                        
                        ### Fill the to-be Border Shape with the current trial's color ### 
                        shape_val_brd.setFillColor(currColList[current_block_trial_matrix[trial,1].astype(int),:], 'rgb') 

                        ### Create the aperture so that the texture seen is only in the size and shape of the current shape ###
                        aperture = visual.Aperture(win, size = size, shape = shape_val.vertices, pos = shape_val.pos)
                        aperture.enabled = False
                        
                        ###############################
                        ####### Start Drawing  ########
                        ###############################
                        event.clearEvents()
                        Pres_stim(shape_val_brd, aperture, imgstim, washOut_Filter)

                        if Round == 0:
                            visual.ImageStim(win,image = schematic, pos = [0,6.6] ).draw()
                        win.flip()

                        timingClock.reset()
                        if Round == 0:
                            while not resp: 
                                if resp:
                                    break
                                if not resp:
                                    allKeys = event.getKeys()
                                    
                                    ### Check to see if the response made is one of the allowable responses
                                    for thisKey in allKeys:
                                        if thisKey in answer_keys_bBox: 
                                            Resp1Time = timingClock.getTime() # Within Trial time of response to the stimulus
                                            if thisKey == answer_keys_bBox[current_block_trial_matrix[trial,3].astype(int)]:
                                                resp, buttonPressed = 1, thisKey #Correct 
                                            else: 
                                                resp, buttonPressed = -1, thisKey #Incorrect
                                        if thisKey in ['escape']:
                                            win.close()
                                            core.quit()
                        elif Round > 0:
                            while timingClock.getTime() <= RespDurLimit: 
                                if resp:
                                    break
                                if not resp:
                                    allKeys = event.getKeys()
                                    
                                    ### Check to see if the response made is one of the allowable responses
                                    for thisKey in allKeys:
                                        if thisKey in answer_keys_bBox: 
                                            Resp1Time = timingClock.getTime() # Within Trial time of response to the stimulus
                                            if thisKey == answer_keys_bBox[current_block_trial_matrix[trial,3].astype(int)]: 
                                                resp, buttonPressed = 1, thisKey #Correct 
                                                if Round == 2:
                                                    tOUT_tmp += 1
                                            else: 
                                                resp, buttonPressed = -1, thisKey #Incorrect 
                                        if thisKey in ['escape']:
                                            win.close()
                                            core.quit()    
                        if Round == 0:
                            visual.ImageStim(win,image = schematic, pos = [0,6.6] ).draw()
                        
                        while timingClock.getTime() <= RespDurLimit:
                            pass
                        win.flip()

                        timingClock.reset()
                        while timingClock.getTime() < Feedback_Delay_Duration:
                            pass
                        
                        if Round < 2:
                            if Round == 0:
                                visual.ImageStim(win,image = schematic, pos = [0,6.6] ).draw()
                            
                            ## Present feedback for 333ms
                            if resp == 1:
                                Positive_Feedback.draw()
                                win.flip()
                                timingClock.reset()
                                while timingClock.getTime() < feedbackDur:
                                    pass
                            elif resp == -1:
                                Negative_Feedback.draw()
                                win.flip()
                                timingClock.reset()
                                while timingClock.getTime() < feedbackDur:
                                    pass
                            elif not resp:
                                MissTrialFeedback.draw()
                                win.flip()
                                timingClock.reset()
                                while timingClock.getTime() < feedbackDur:
                                    pass
                        print(resp)
                        
                        ### Intertrial Interval Start ###
                        if trial != current_block_trial_matrix.shape[0] - 1:
                            if Round == 0:
                                visual.ImageStim(win,image = schematic, pos = [0,6.6] ).draw()
                            fixation1w.draw(), fixation2w.draw()
                            win.flip()
                        core.wait(practice_ITI) 

                                 
                        if not resp:
                            Resp1Time, Response1_On = 'NaN', 'NaN'           
                        if not new_Resp:
                            Resp2Time = 'NaN'


                        trialDataArray = map(str, [ Date,
                                                    SubID,
                                                    Round,
                                                    current_block_trial_matrix[trial,3], 
                                                    resp, 
                                                    current_block_trial_matrix[trial,4],
                        ])
                        trialDataArray= ','.join(trialDataArray)
                        HRLDataFile.write(trialDataArray+'\n')
                        os.fsync(HRLDataFile)
                        HRLDataFile.flush()


                    if Round < 2:
                        crit_notPassed = False
                    else:
                        if tOUT_tmp < 13:
                            crit_notPassed = True
                        else:
                            crit_notPassed = False
            

    ############################
    ### PRACTICE ROUND 4, 5 #####
    ### [4] Feedback provided ###
    ############################

    Chunk_2_Trial_Array4 = np.zeros((96, 5))*np.nan

    Chunk_2_Trial_Array5 = np.zeros((32, 5))*np.nan

    if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 1):
        Chunk_2_Trial_Array4[0:16,:] =      trialArray_SoT_Practice4[0:16,:]
        Chunk_2_Trial_Array4[16:32,:] =     trialArray_CoT_Practice4[0:16,:]
        Chunk_2_Trial_Array4[32:48,:] =     trialArray_SoT_Practice4[16:32,:]
        Chunk_2_Trial_Array4[48:64,:] =     trialArray_CoT_Practice4[16:32,:]
        Chunk_2_Trial_Array4[64:80,:] =     trialArray_SoT_Practice4[32:48,:]
        Chunk_2_Trial_Array4[80:96,:] =     trialArray_CoT_Practice4[32:48,:]

        Chunk_2_Trial_Array5[0:16,:] =      trialArray_SoT_Practice5
        Chunk_2_Trial_Array5[16:32,:] =     trialArray_CoT_Practice5

    elif np.logical_or(CounterBalanceNumber == 2, CounterBalanceNumber == 3):
        Chunk_2_Trial_Array4[0:16,:] =      trialArray_CoT_Practice4[0:16,:]
        Chunk_2_Trial_Array4[16:32,:] =     trialArray_SoT_Practice4[0:16,:]
        Chunk_2_Trial_Array4[32:48,:] =     trialArray_CoT_Practice4[16:32,:]
        Chunk_2_Trial_Array4[48:64,:] =     trialArray_SoT_Practice4[16:32,:]
        Chunk_2_Trial_Array4[64:80,:] =     trialArray_CoT_Practice4[32:48,:]
        Chunk_2_Trial_Array4[80:96,:] =     trialArray_SoT_Practice4[32:48,:]

        Chunk_2_Trial_Array5[0:16,:] =      trialArray_CoT_Practice5
        Chunk_2_Trial_Array5[16:32,:] =     trialArray_SoT_Practice5

    win.flip()

    #####################################################################################################################
    ### This is the second chunk of practice. This chunk includes Rounds 4 and 5, which will be considered as blocks. ###
    ### Both Cot and Sot will be done within each round, so there is no need for an add'l layer like in Chunk 1 #########
    #####################################################################################################################

    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 4 and 5 of practice. In these rounds you are going to experience a very close approximation to what a run will be like in the real experiment.\n\n\
There will be 96 trials in Round 4, and 32 trials in Round 5. In both Rounds, the rule will switch after 16 trials. You will be notified of this switch.\n\n\
Just like in the real experiment, these trials require that you make a response within 2 seconds of the stimulus appearing on screen.\n\n\
In Round 4, you will be given feedback as to whether your response was correct or not. In Round 5, you will NOT be provided feedback after each trial.\n\n\
A " + " symbol will appear on screen during the period between trials to indicate the next trial will start soon.\n\n\n\n\
Press Any Key to Begin').draw()
    win.flip()
    if TESTMODE: core.wait(.5)
    else: core.wait(4)
    event.waitKeys()

    if np.logical_or(CounterBalanceNumber == 0, CounterBalanceNumber == 2):
        schematicSoT = "Schematic_1_SoT.tiff"
        schematicCoT = "Schematic_1_CoT.tiff"
    else: 
        schematicSoT = "Schematic_2_SoT.tiff"
        schematicCoT = "Schematic_2_CoT.tiff"


    if CounterBalanceNumber in [0,1]:
        if TESTMODE == True:
            for i in range(2):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE REMINDER       [%s] seconds remain' %(str(2-i))).draw()
                visual.ImageStim(win,image = schematicSoT, pos = [0,6] ).draw()
                visual.ImageStim(win,image = schematicCoT, pos = [0,-6] ).draw()
                win.flip()
                core.wait(1)
        elif TESTMODE == False: 
            for i in range(30):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE REMINDER       [%s] seconds remain' %(str(30-i))).draw()
                visual.ImageStim(win,image = schematicSoT, pos = [0,6] ).draw()
                visual.ImageStim(win,image = schematicCoT, pos = [0,-6] ).draw()
                win.flip()
                core.wait(1)

    elif CounterBalanceNumber in [2,3]:
        if TESTMODE == True:
            for i in range(2):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE REMINDER       [%s] seconds remain' %(str(2-i))).draw()
                visual.ImageStim(win,image = schematicCoT, pos = [0,6] ).draw()
                visual.ImageStim(win,image = schematicSoT, pos = [0,-6] ).draw()
                win.flip()
                core.wait(1)
        elif TESTMODE == False: 
            for i in range(30):
                visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE REMINDER       [%s] seconds remain' %(str(30-i))).draw()
                visual.ImageStim(win,image = schematicCoT, pos = [0,6] ).draw()
                visual.ImageStim(win,image = schematicSoT, pos = [0,-6] ).draw()
                win.flip()
                core.wait(1)

    for Round in np.arange(2):
        if order == 0:
            stringOrder = "Shape-on-Top followed by Color-on-Top"
            stringCurrRule1 = 'Shape-on-Top'
            stringCurrRule2 = 'Color-on-Top'

        elif order == 1:
            stringOrder = "Color-on-Top followed by Shape-on-Top"
            stringCurrRule1 = 'Color-on-Top'
            stringCurrRule2 = 'Shape-on-Top'

        if Round == 0:
            current_block_trial_matrix = Chunk_2_Trial_Array4

            visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 4 of practice.\n\n\
You will be provided feedback after each trial.\n\n\
The order of rules will be %s\n\n\
Press Any Key to Begin' %(stringOrder)).draw()
            win.flip()
            if TESTMODE: core.wait(.5)
            else: core.wait(2)
            event.waitKeys()

        elif Round == 1:
            current_block_trial_matrix = Chunk_2_Trial_Array5

            visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'This is Round 5 of practice.\n\n\
You will NOT be provided feedback after each trial.\n\n\
The order of rules will be %s\n\n\
Press Any Key to Begin' %(stringOrder)).draw()
            win.flip()
            if TESTMODE: core.wait(.5)
            else: core.wait(2)
            event.waitKeys()
        
        totalCorrect = 0        

        for trial in np.arange(current_block_trial_matrix.shape[0]): 

            if Round == 0:
                if trial == 0:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'CURRENT RULE\n\n\
%s' %(stringCurrRule1)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()
                
                if trial == 16:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE CHANGE\n\n\
%s' %(stringCurrRule2)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()

                if trial == 32:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'Prepare for Run #2').draw()
                    win.flip()
                    core.wait(10)

                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'CURRENT RULE\n\n\
%s' %(stringCurrRule1)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()
                
                if trial == 48:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE CHANGE\n\n\
%s' %(stringCurrRule2)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()

                if trial == 64:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'Prepare for Run #3').draw()
                    win.flip()
                    core.wait(10)

                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'CURRENT RULE\n\n\
%s' %(stringCurrRule1)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()
                
                if trial == 80:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE CHANGE\n\n\
%s' %(stringCurrRule2)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()


            if Round == 1:
                if trial == 0:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'CURRENT RULE\n\n\
%s' %(stringCurrRule1)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()
                    core.wait(7)
                
                if trial == 16:
                    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE CHANGE\n\n\
%s' %(stringCurrRule2)).draw()
                    win.flip()
                    core.wait(2)
                    win.flip()
                    core.wait(7)
            
            buttonPressed = None
            resp, new_Resp, new_new_resp, Resp1Time, Response1_On = False, False, False, False, False

            ### Determine which shape will be drawn on this trial ###
            
            shape_val = currShapeList1[current_block_trial_matrix[trial,0].astype(int)] 
            shape_val_brd = currShapeList2[current_block_trial_matrix[trial,0].astype(int)] 
            
            shape_val.setPos([0,0]) 
            shape_val_brd.setPos([0,0]) 
            
            ### Create the Texture Visual Patch ### 
            imgstim = visual.ImageStim(win=win, pos = shape_val.pos, size = [10,10], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(currTexList[current_block_trial_matrix[trial,2].astype(int)]))) 
            
            ### Fill the to-be Border Shape with the current trial's color ### 
            shape_val_brd.setFillColor(currColList[current_block_trial_matrix[trial,1].astype(int),:], 'rgb') 

            ### Create the aperture so that the texture seen is only in the size and shape of the current shape ###
            aperture = visual.Aperture(win, size = size, shape = shape_val.vertices, pos = shape_val.pos) 
            aperture.enabled = False
            
            ###############################
            ####### Start Drawing  ########
            ###############################
            event.clearEvents()
            Pres_stim(shape_val_brd, aperture, imgstim, washOut_Filter)

            win.flip()
            timingClock.reset()

            while timingClock.getTime() <= RespDurLimit: 
                if resp:
                    break
                if not resp:
                    allKeys = event.getKeys()
                    
                    ### Check to see if the response made is one of the allowable responses
                    for thisKey in allKeys:
                        if thisKey in answer_keys_bBox: #_bBox:
                            Resp1Time = timingClock.getTime() # Within Trial time of response to the stimulus
                            if thisKey == answer_keys_bBox[current_block_trial_matrix[trial,3].astype(int)]: 
                                resp, buttonPressed = 1, thisKey #Correct
                                if Round == 1:
                                    totalCorrect += 1 
                            else: 
                                resp, buttonPressed = -1, thisKey #Incorrect 
                        if thisKey in ['escape']:
                            win.close()
                            core.quit()    
            print(trial, 'resp = ', resp)
            
            while timingClock.getTime() <= RespDurLimit:
                pass
            win.flip()

            
            timingClock.reset()
            while timingClock.getTime() < Feedback_Delay_Duration: 
                pass
            
            if Round == 0:
                ## Present feedback for 333ms
                if resp == 1:
                    Positive_Feedback.draw()
                    win.flip()
                    timingClock.reset()
                    while timingClock.getTime() < feedbackDur:
                        pass
                elif resp == -1:
                    Negative_Feedback.draw()
                    win.flip()
                    timingClock.reset()
                    while timingClock.getTime() < feedbackDur:
                        pass
                elif not resp:
                    MissTrialFeedback.draw()
                    win.flip()
                    timingClock.reset()
                    while timingClock.getTime() < feedbackDur:
                        pass
            
            print(resp)
            ### Intertrial Interval Start ###
            if trial != current_block_trial_matrix.shape[0] - 1:
                fixation1w.draw(), fixation2w.draw()
                win.flip()
            core.wait(practice_ITI)




            trialDataArray = map(str, [Date,
            SubID,
            Round,
            current_block_trial_matrix[trial,3], 
            resp, 
            current_block_trial_matrix[trial,4],  
            ])
            trialDataArray= ','.join(trialDataArray)
            HRLDataFile.write(trialDataArray+'\n')
            os.fsync(HRLDataFile)
            HRLDataFile.flush()

    VALUE = str(np.round(np.divide(totalCorrect, 32) * 100,2))
    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'Your response accuracy was ' + VALUE + '%.' + ' Press Any Key to Close').draw()
    win.flip()
    event.waitKeys()

    experimentEnd = myOverallClock.getTime()
    print("Total Experiment Time was  %s" %(experimentEnd - experimentStart))
    HRLDataFile.close()
    win.mouseVisible = True
    win.close()
    core.quit()     

### MAIN SCRIPT ###
if __name__ == '__main__':
    main()