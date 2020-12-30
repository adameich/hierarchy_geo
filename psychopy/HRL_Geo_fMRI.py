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

    data_dir_root = '/Users/Eichenbaum/HWNI/Experiments/HRL_Geometry/scripts/psychopy' #'/Users/despolabtesting1/Desktop/Experiments/eichenbaum/HRL_Geo_Barker135' # '/Users/StimulusMac/Desktop/Experiments/DespoLab/adameich/HRL'

    d = 57 # Distance between monitor and participant in cm  ## This scales everything that is coded in degrees!
    my_monitor = monitors.Monitor(name='DesktopLab')
    my_monitor.setSizePix((1920,1080)) # (2560,1440) (1024, 768) (1920,1080)## This scales everything that is coded in degrees!
    my_monitor.setDistance(d)  ## This scales everything that is coded in degrees!
    my_monitor.setWidth(50.88)  ## This scales everything that is coded in degrees!
    my_monitor.saveMon()
    
    monitor = 'DesktopLab'
    res = [1024, 768] # [1920,1080] [1024, 768]

    ####################
    ### Subject Info ###
    ####################
    SubID = str(sys.argv[1]) 
    Age = int(sys.argv[2]) 
    Gen = str(sys.argv[3]) 
    Run = int(sys.argv[4]) 
    Date = str(data.getDateStr()) 
    
    CounterBalanceNumber = int(SubID) % 4
    if Run % 2 == 1:
        flipOrder = False #(AB)
        flipOrderStr = 'AB'
    elif Run % 2 == 0:
        flipOrder = True #(BA)
        flipOrderStr = 'BA'
    print(flipOrder, flipOrderStr)
    win = visual.Window(res, fullscr = False, monitor = monitor, color = [-.375, -.375, -.375], units = 'deg', allowStencil = True)
    
    # Shared Parameter Values#
    h = 28.62 # 34.544#3.6221171854 # Monitor height in cm
    r = win.size[1] # Vertical resolution of the monitor
    deg_per_px = degrees(atan2(.5*h, d)) / (.5*r) # Calculate the number of degrees that correspond to a single pixel. This will generally be a very small value, something like 0.03.    
    
    #########################################################################
    ######## Data file creation for trial info and user response info #######
    #########################################################################    
    file_name = SubID + '_HRL_Geo_Run_' + str(Run)
    complete_file_name = os.path.join(data_dir_root, 'data', file_name + '.csv')
    HRLDataFile = open(complete_file_name,'w')
    firstLine =['DateTime',         ### The Date and Time at the start of the session.
                'SubID',            ### The 3-digit numeric code given to the participant
                'Gen',              ### One of three options: M = 'Male', F = 'Female', O = 'Other'
                'Age',              ### The age of the participant
                'Run',              ### The current block of the expt (currently set to 5 blocks)
                'CntrBalNum',       ### CounterBalanceNumber
                'StimSet',          ### Which of the two stimulus sets are they seeing?
                'RuleOrder',        ### OVERALL SoT-CoT or CoT-SoT
                'FlipRunOrder',     ### Within this run, is the RuleOrder going to be normal (AB) or flipped (BA)?
                'RunOrderStr',      ### The actual string of "AB" or "BA"
                'Trial',            ### Trial number 
                'ShapeName',        ### The shape stimulus that was shown on the current trial. Will be a string.
                'ShapeNumber',      ### The 0 or 1 in the design matrix
                'ColorName',        ### The color of the border that was shown on the current trial. Will be a string. 
                'ColorNumber',      ### The 0 or 1 in the design matrix
                'TextureName',      ### The texture image that was shown on the current trial. Will be an integer.
                'TextureNumber',    ### The 0 or 1 in the design matrix
                'Rule',             ### Shape-on-Top or Color-on-Top
                'StimIdx',          ### The number associated with that stimulus conjunction. This will be a good cross check to make sure that everything is coding appropriately for e.g. numSince
                'Iter',             ### Provides how many times the stimulus conjuction has been previously seen this block. 
                'Response',         ### The keyboard input provided by the Pp for the current trial. Will be a string of either '1', '2', '3', or '4', or 'NaN' if no input detected.
                'tAns',             ### The correct answer for the current trial. Will be a string of either 'v', 'b', 'n', or 'm'.
                'tOut',             ### Whether the response was Correct (1), Incorrect (-1), or No Response provided ('Nan') 
                'TrialRT',          ### Reaction time from Stimulus onset to response. Will be a float. If no response provided, will be a "NaN" string. 
                'PlannedITI',
                'StimDur', 
                'StimOnset',        ### The time when the stimulus is presented on screen, relative the the first TTL pulse. 
                'RespOnset',        ### The time when the first button press response to the stimulus occured, relative to the first TTL pulse received. 
                'StimOffset',       ### The time when the stimulus goes off screen (should be identical to "confOff")
                'ITIOn'      
                ]
    firstLine = ','.join(firstLine)
    HRLDataFile.write(firstLine+'\n')

    ########################
    ## Drawing Parameters ##
    ########################
    wrapWidth =         22.5
    line_width_val =    0.0
    stim_rad =          5.0 *.8
    opa_val =           1.0
    rect_width =        10.0 *.8 
    rect_height =       10.0 *.8  
    size =              .4 # How large everything will be from the aperture perspective
    border_size_boost = 1.3 
    text_win_size =     .55 
    
    ### Colors ###
    RGB_colors =        (np.array([(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]) - 127.5) / 127.5 
    tutorial_colors =   (np.array([(0,255,0), (0,0,128)]) - 127.5 ) / 127.5
    rgbNames =          np.array(['red', 'blue', 'yellow', 'magenta']) 

    ### Texture Images used ###
    texIdx_array =      np.array((11, 37, 65, 87))  

    ###############################
    ## Block Creation Parameters ##
    ###############################
    nDims =             3
    nTrials =           32

    #######################
    ## Timing Parameters ##
    #######################
    fmri_wait_time =    5
    schematicViewTime = 15
    RespDurLimit =      2.0 # 120 frames will allow the subject to respond within a 2000ms window.
    
    myOverallClock =    core.Clock() # clock used for overal stimulus timing throughout the experiment
    TTL_start_clock =   core.Clock()
    timingClock =       core.Clock()

    StimOnset =         np.ones(nTrials)*np.nan
    ITIOn =             np.ones(nTrials)*np.nan

    ITI_base = [5,6,6,7]
    ITIs_tmp_a = []
    ITIs_tmp_b = []
    ITIs_tmp_a = np.tile(ITI_base,[4])
    ITIs_tmp_b = np.tile(ITI_base,[4]) 
    np.random.shuffle(ITIs_tmp_a)
    np.random.shuffle(ITIs_tmp_b)
    ITIs = np.hstack((ITIs_tmp_a, ITIs_tmp_b))

    #########################
    ## Response Parameters ##
    #########################
    keyState=key.KeyStateHandler() 
    win.winHandle.push_handlers(keyState) 
    answer_keys_bBox = ['1', '2', '3', '4']
    answer_keys = ['v','b','n','m']
    totalCorrect = 0

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
    shape_list =        [circle, square, triangle, pentagon]
    shape_list2 =       [circle2, square2, triangle2, pentagon2] 
    shape_list3 =       [circle3, square3, triangle3, pentagon3] 
    Shape_list_wTut =   [octagon, diamond]
    Shape_list_wTut2 =  [octagon2, diamond2]

    if CounterBalanceNumber in [0,2]:
        StimSet = 1 # Circle-Triangle, Blue-Yellow
    else:
        StimSet = 2 # Square-Pentagon, Red-Pink

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
    currColNameList = rgbNames[CB_vals]

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

    ###########################
    ## Construct Trial Array ##
    ###########################
    trialArray_SoT_Total = np.zeros((trialArray_SoT.shape[0] * 2, trialArray_SoT.shape[1]))*np.nan
    tmp_SoT_a = []
    tmp_SoT_a = np.tile(trialArray_SoT[:,:],[2,1]) 
    np.random.shuffle(tmp_SoT_a)
    trialArray_SoT_Total[0:16,:] = tmp_SoT_a

    trialArray_CoT_Total = np.zeros((trialArray_CoT.shape[0] * 2, trialArray_CoT.shape[1]))*np.nan
    tmp_CoT_a = []
    tmp_CoT_a = np.tile(trialArray_CoT[:,:],[2,1]) 
    np.random.shuffle(tmp_CoT_a)
    trialArray_CoT_Total[0:16,:] = tmp_CoT_a

    Full_Trial_Array = np.zeros((nTrials, 5))*np.nan

    if CounterBalanceNumber in [0,1]:
        if flipOrder:
            Full_Trial_Array[0:16,:] =   trialArray_CoT_Total
            Full_Trial_Array[16:32,:] =   trialArray_SoT_Total
            stringCurrRule1 = 'Color-on-Top'
            stringCurrRule2 = 'Shape-on-Top'
        else:
            Full_Trial_Array[0:16,:] =   trialArray_SoT_Total
            Full_Trial_Array[16:32,:] =   trialArray_CoT_Total
            stringCurrRule1 = 'Shape-on-Top'
            stringCurrRule2 = 'Color-on-Top'

    elif CounterBalanceNumber in [2,3]:
        if flipOrder:
            Full_Trial_Array[0:16,:] =   trialArray_SoT_Total
            Full_Trial_Array[16:32,:] =   trialArray_CoT_Total
            stringCurrRule1 = 'Shape-on-Top'
            stringCurrRule2 = 'Color-on-Top'
        else:
            Full_Trial_Array[0:16,:] =   trialArray_CoT_Total
            Full_Trial_Array[16:32,:] =   trialArray_SoT_Total
            stringCurrRule1 = 'Color-on-Top'
            stringCurrRule2 = 'Shape-on-Top'
    
    #######################################################
    ### Build Trial Duration and Trial Start-Time Array ###
    #######################################################
    trial_durations = (np.ones(nTrials)*RespDurLimit) + ITIs
    trial_starts_matrix = np.ones((nTrials))*np.nan 


    for i in range(nTrials):
        if i == 0:
            trial_starts_matrix[i] = 0
        else:
            trial_starts_matrix[i] = (trial_starts_matrix[i-1] + trial_durations[i-1])
            
    trial_starts_matrix += fmri_wait_time
    trial_starts_matrix += 2 # The amount of time the 1st rule is on screen
    trial_starts_matrix += 7 # The ITI between the 1st Rule going off screen and Trial #1 starting
    trial_starts_matrix[16:32] += 2 # The amount of time the 2nd rule is on screen
    trial_starts_matrix[16:32] += 7 # The ITI between the 2nd Rule going off screen and Trial #33 starting

    print(trial_starts_matrix)
    win.mouseVisible = False
    experimentStart = myOverallClock.getTime()

    ######################################
    ######### INSTRUCTIONS START #########
    ######################################
    if CounterBalanceNumber in [0,2]:
        schematicSoT = "Schematic_1_SoT.tiff"
        schematicCoT = "Schematic_1_CoT.tiff"
    else: 
        schematicSoT = "Schematic_2_SoT.tiff"
        schematicCoT = "Schematic_2_CoT.tiff"

    for i in range(schematicViewTime):
        visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE REMINDER       [%s] seconds remain' %(str(schematicViewTime-i))).draw()
        visual.ImageStim(win,image = schematicSoT, pos = [0,6] ).draw()
        visual.ImageStim(win,image = schematicCoT, pos = [0,-6] ).draw()
        win.flip()
        core.wait(1)

    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'We are now starting the task.\n\n\
No feedback will be provided after each response. Instead you will be told of your overall accuracy at the end of each run.\n\n\
Press Any Key to Begin').draw()
    win.flip()
    core.wait(1)
    event.waitKeys()
               
    #######################
    ### Waiting for TTL ###
    #######################
    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'Scanner is warming up and making adjustments. It is crucial that you stay as still as you can.').draw()
    win.flip()
    
    event.waitKeys(keyList='5') 
    
    fixation1w.draw(), fixation2w.draw()
    win.flip()
    
    TTL_start_clock.reset()
    
    core.wait(fmri_wait_time)

    #################################
    ### Display text for 1st Rule ###
    #################################
    currentRule = stringCurrRule1
    visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'CURRENT RULE\n\n\
%s' %(stringCurrRule1)).draw()
    win.flip()
    core.wait(2)
    win.flip()
    core.wait(7)

    ########################
    ### START TRIAL LOOP ###
    ########################    
    for trial in np.arange(Full_Trial_Array.shape[0]): 
        buttonPressed = None
        resp, Resp1Time, Response1_On = False, False, False

        ####################################
        ### Display text for Rule Change ###
        ####################################      
        if trial == 16:
            currentRule = stringCurrRule2
            visual.TextStim(win, height = text_win_size, wrapWidth = wrapWidth, text = 'RULE CHANGE\n\n\
%s' %(stringCurrRule2)).draw()
            win.flip()
            core.wait(2)
            win.flip()
            core.wait(7)

        #########################################################################
        ### Determine which shape, color, texture will be drawn on this trial ###
        #########################################################################
        shape_val = currShapeList1[Full_Trial_Array[trial,0].astype(int)] 
        shape_val_brd = currShapeList2[Full_Trial_Array[trial,0].astype(int)] 
        
        shape_val.setPos([0,0]) 
        shape_val_brd.setPos([0,0]) 
        
        ### Create the Texture Visual Patch ### 
        imgstim = visual.ImageStim(win=win, pos = shape_val.pos, size = [10,10], image = os.path.join(data_dir_root, 'Normalized_Brodatz/D%s.tif' %(currTexList[Full_Trial_Array[trial,2].astype(int)]))) 
        
        ### Fill the to-be Border Shape with the current trial's color ### 
        shape_val_brd.setFillColor(currColList[Full_Trial_Array[trial,1].astype(int),:], 'rgb') 

        ### Create the aperture so that the texture seen is only in the size and shape of the current shape ###
        aperture = visual.Aperture(win, size = size, shape = shape_val.vertices, pos = shape_val.pos) 
        aperture.enabled = False

        ###############################################
        ### Waiting for previous trial's ITI to end ###
        ###############################################
        while TTL_start_clock.getTime() < trial_starts_matrix[trial]: 
            pass 

        ##############################
        ### Start Drawing Stimulus ###
        ##############################
        event.clearEvents()
        Pres_stim(shape_val_brd, aperture, imgstim, washOut_Filter)
        win.flip()
        StimOnset[trial] = TTL_start_clock.getTime() #The stimulus has just been shown. Onset time is measured as the first moment after the window was flipped
        
        timingClock.reset()
        while timingClock.getTime() <= RespDurLimit: 
            if resp:
                break
            if not resp:
                allKeys = event.getKeys()
                
                ### Check to see if the response made is one of the allowable responses
                for thisKey in allKeys:
                    if thisKey in answer_keys_bBox:
                        Resp1Time = timingClock.getTime() # Within Trial time of response to the stimulus
                        Response1_On = TTL_start_clock.getTime() # Time of response to the stimulus relative to the start of the 1st TTL pulse
                        if thisKey == answer_keys_bBox[Full_Trial_Array[trial,3].astype(int)]: 
                            resp, buttonPressed = 1, thisKey #Correct 
                            totalCorrect += 1
                        else: 
                            resp, buttonPressed = -1, thisKey #Incorrect 
                    if thisKey in ['escape']:
                        win.close()
                        core.quit()    
        
        ##########################################################
        ### Remove Stimulus from Screen after full 2s duration ###
        ##########################################################
        while timingClock.getTime() <= RespDurLimit:
            pass
        win.flip()
        stimOffset = TTL_start_clock.getTime() # This stimulus has just left the screen. The ITI has begun.
     
        #################################
        ### Intertrial Interval Start ###
        #################################
        ITIOn[trial] = TTL_start_clock.getTime()
        if trial != Full_Trial_Array.shape[0] - 1:
            fixation1w.draw(), fixation2w.draw()
            win.flip()

        iteration = list(Full_Trial_Array[:trial, 4]).count(Full_Trial_Array[trial, 4]) + 1
        stimDur = stimOffset - StimOnset[trial]

        ##########################################################################
        ### Data file update for trial & user response info: Saved every trial ###
        ##########################################################################
        trialDataArray = map(str, [
        Date, # DateTime
        SubID, # SubID
        Gen, # Gen
        Age, # Age
        Run, # Run
        CounterBalanceNumber, # CntrBalNum
        StimSet, # StimSet: Which of the two stim sets are being used for this Pp?
        order, # RuleOrder: What is the overall SoT-CoT v CoT-SoT order
        flipOrder, # RunOrder: AB or BA, i.e. is the RuleOrder flipped for this run?
        flipOrderStr, # The actual string of either AB or BA
        trial+1, # Trial number
        shape_val.name, # Shape name
        int(Full_Trial_Array[trial,0]), # Shape Number
        currColNameList[int(Full_Trial_Array[trial,1])], # Color name
        int(Full_Trial_Array[trial,1]), # Color Number
        currTexList[int(Full_Trial_Array[trial,2])], # Texture name
        int(Full_Trial_Array[trial,2]), # Texture number
        currentRule, 
        Full_Trial_Array[trial,4], # Stim Idx 
        iteration, 
        buttonPressed, 
        answer_keys_bBox[Full_Trial_Array[trial,3].astype(int)], 
        resp, 
        Resp1Time, #RT
        ITIs[trial],
        stimDur,
        StimOnset[trial], # Relative to the TTL pulse (the 1st one)
        Response1_On,
        stimOffset, 
        ITIOn[trial]
        ])

        trialDataArray= ','.join(trialDataArray)
        HRLDataFile.write(trialDataArray+'\n')
        os.fsync(HRLDataFile)
        HRLDataFile.flush()
        #################################################################

    #################
    ### Final ITI ###
    #################
    core.wait(ITIs[trial]) ### 133 TRs 

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