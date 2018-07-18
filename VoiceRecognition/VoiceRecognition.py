import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import speech_recognition as sr
import time 
import ScreenCapture
import random 
import os

#
# VoiceRecognition
#

class VoiceRecognition(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Voice Recognition" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Utilities"]
    self.parent.dependencies = []
    self.parent.contributors = ["Steve Li (BU RISE)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This module allows you to manipulate the slices and the 3D viewer using voice commands. 
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
Developed with the aid of Dr. Junichi Tokuda 
""" # replace with organization, grant and thanks.

#
# VoiceRecognitionWidget
#

class VoiceRecognitionWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    
    #Initializes recognizer and microphone 
    self.recognizer = sr.Recognizer()
    try: 
      self.microphone = sr.Microphone()

    except(IOError):
      print("ERROR: No default microphone. Check if microphone is plugged in or if you have a default microphone set in your sound settings.")
      self.errors.setText("ERROR: No default microphone. Check if your microphone is plugged in or if you have a default microphone set in your sound settings.")


    # Initializes layout manager: 

    self.lm = slicer.app.layoutManager()
    self.threeDView = self.lm.threeDWidget(0).threeDView()
    self.logic = VoiceRecognitionLogic(self.lm)


    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    # microphone selector 
    self.microphoneSelector = qt.QComboBox()
    self.microphoneList = sr.Microphone.list_microphone_names()
    self.microphoneSelector.addItem("Default")
    self.microphoneSelector.addItems(self.microphoneList)
    parametersFormLayout.addRow("Select Microphone: ", self.microphoneSelector)

    # Sound energy level threshold value
    self.energyLevelThreshold = ctk.ctkSliderWidget()
    #self.energyLevelThreshold.disable = True
    self.energyLevelThreshold.singleStep = 1 
    self.energyLevelThreshold.setDisabled(True)
    self.energyLevelThreshold.minimum = 0
    self.energyLevelThreshold.maximum = 5000
    self.energyLevelThreshold.value = self.recognizer.energy_threshold
    self.energyLevelThreshold.tracking = False
    self.energyLevelThreshold.setToolTip("Sets the threshold value for sounds. Value below this threshold is considered silence. Silent rooms are from 0-100, values for speaking 150-3500. Louder rooms are 3500 and above. Adjust if necessary. Uncheck the box to enable")
    
    parametersFormLayout.addRow("Sound Energy Threshold: ", self.energyLevelThreshold)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.dynamicEnergyThreshold = qt.QCheckBox()
    self.dynamicEnergyThreshold.checked = 1
    self.dynamicEnergyThreshold.setToolTip("Check the box if the ambient noise in the room is not controlled, i.e. in a noisy room ")
    parametersFormLayout.addRow("Enable Dynamic Energy Threshold: ", self.dynamicEnergyThreshold)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Begin Listneing")
    self.applyButton.toolTip = "Listens for voice."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)


    self.repeatButton = qt.QPushButton("Repeat last command")
    self.repeatButton.toolTip = "Listens for voice."
    self.repeatButton.enabled = True
    parametersFormLayout.addRow(self.repeatButton)

    # speech to text label 
    self.textBox = qt.QLabel(" ")
    self.textBox.toolTip = "User input"
    self.textBox.setTextFormat(0) #plain text 
    parametersFormLayout.addRow("Speech: ", self.textBox)

    # Error label 
    self.errors = qt.QLabel(" ")
    self.errors.setTextFormat(0)
    self.errors.setWordWrap(True)
    parametersFormLayout.addRow("Errors: ", self.errors)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.repeatButton.connect('clicked(bool)', self.onRepeatButton)
    self.microphoneSelector.currentIndexChanged.connect(self.microphone_changed)
    self.energyLevelThreshold.valueChanged.connect(self.threshold_changed)
    self.dynamicEnergyThreshold.clicked.connect(self.dynamicThreshold)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()
    
  def cleanup(self):
    pass

  
  def onSelect(self):
    print(5)

  
  # logic when threshold is changed 
  def threshold_changed(self):
    
    self.recognizer.energy_threshold = self.energyLevelThreshold.value

  
  # logic when microphone is selected 
  def microphone_changed(self):
    print(self.microphoneSelector.currentIndex)

    # gets the index of the selected microphone
    index = self.microphoneSelector.currentIndex
    print("index: ", index)

    if(index == 0): 
      self.microphone = sr.Microphone()    
    else: 
      self.microphone = sr.Microphone(device_index = index - 1)

  
  def dynamicThreshold(self):
    print(self.dynamicEnergyThreshold.checked)

    # setDisabled(True) = slider is disabled 
    self.energyLevelThreshold.setDisabled(self.dynamicEnergyThreshold.checked)

    self.recognizer.dynamic_energy_threshold = self.dynamicEnergyThreshold.checked

  
  def onRepeatButton(self):
    self.logic.parse("repeat")

  
  def onApplyButton(self):
    #self.displayLabel.setText("Listening for speech....")
    slicer.util.delayDisplay("Wait...", 2250)

    # TODO: Background listening stuff --> not working will try once I get a response 
    # self.recognizer = sr.Recognizer()
    # try: 
    #   self.microphone = sr.Microphone()

    # except(IOError):
    #   print("ERROR: No default microphone. Check if microphone is plugged in or if you have a default microphone set in your sound settings.")
    #   self.errors.setText("ERROR: No default microphone. Check if your microphone is plugged in or if you have a default microphone set in your sound settings.")

    # with self.microphone as source:
    #   self.recognizer.adjust_for_ambient_noise(source)

    # stop_listening = self.recognizer.listen_in_background(self.microphone, self.callback)

    self.startLogic()


  def startLogic(self):
    #text = self.logic.interpreter(self.recognizer, self.microphone)
    # listens in the background 
    #stop_listening = r.listen_in_background(self.microphone, logic.interpreter)

    #self.textBox.setText(text)
    self.logic.parse("zoom out 0.8")

#
# VoiceRecognitionLogic
#
# def callback(self, recognizer, audio):
#     try: 
#       print(recognizer.recognize_google(audio))
#     # handles any api/voice errors  errors 
#     except sr.RequestError: 
#       print( "There was an issue in handling the request, please try again")
#     except sr.UnknownValueError:
#       print("Unable to Recognize speech")

class VoiceRecognitionLogic(ScriptedLoadableModuleLogic):
  """
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  """
      |                                                       |
      |  yaw
      |
      |
      |
      |______________  pitch
     /
    / roll
   /
  /
      


  Setting layout: 
    0  -  Initial View                  11  -  Lightbox View
    1  -  Default View                  12  -  Compare View 
    2  -  Coventional View              13  -  Side by Side Lightbox View 
    3  -  Four Up View                  14  -  None
    4  -  One Up 3D View                15  -  Dual 3D View   
    5  -  One Up Slice View             16  -  Conventional Widescreen View 
    6  -  One Up Red Slice View         17  -  Comp;are Widescreen View 
    7  -  One Up Yellow Slice View      18  -  Single Lightbox view 
    8  -  One Up Green Slice View       19  -  Triple 3D Endoscopy View 
    9  -  Tabbed 3D View                20  -  3D Plus Lightbox view 
    10 -  Tabbed Slice View             21  -  Three Over Three View 

    22  -  Four Over Four View                  33  -  Three By Three Slice View 
    23  -  Compare Grid View                    34  -  Four Up Table View  
    24  -  Conventional Quantitative View       35  -  3D Table eView  
    25  -  Four Up Quantitative View            36  -  Conventional Plot View 
    26  -  One Up Quantitative View             37  -  Four Up Plot View   
    27  -  Two Over Two view                    38  -  Four Up Plot Table View 
    28  -  Three Over Three Quantitative View   39  -  One Up Plot View  
    29  -  side by side view                    40  -  Three Over Three Plot View  
    30  -  Four by Three Slice View           
    31  -  Four by Two Slice View              
    32 -   Five by Two Slice View   

  View from Axis: 
    0 - None 
    1 - Right 
    2 - Left 
    3 - superior 
    4 - inferior 
    5 - anterior 
    6 - posterior             
  """
  # Parameters array is used to store function parameters when user asks to repaet a function 
  parameters = []
  pitch_terms = ["pitch", "catch", "touch", "patch"]
  yaw_terms = ["yaw", "yeah"]
  

  # constructor, initializes everything
  def __init__(self, layoutManager):
    self.layoutManager = layoutManager
    self.threeDView = layoutManager.threeDWidget(0).threeDView()

    self.red = layoutManager.sliceWidget('Red')
    self.yellow = layoutManager.sliceWidget('Yellow')
    self.green = layoutManager.sliceWidget('Green')

    self.redController = self.red.sliceController()
    self.yellowController = self.yellow.sliceController()
    self.greenController = self.green.sliceController()

    self.redLogic = self.red.sliceLogic()
    self.yellowLogic = self.yellow.sliceLogic()
    self.greenLogic = self.green.sliceLogic()

    self.redNode = self.redLogic.GetSliceNode()
    self.yellowNode = self.yellowLogic.GetSliceNode()
    self.greenNode = self.greenLogic.GetSliceNode()

    self.redCompositeNode = self.redLogic.GetSliceCompositeNode()
    self.yellowCompositeNode = self.yellowLogic.GetSliceCompositeNode()
    self.greenCompositeNode = self.greenLogic.GetSliceCompositeNode()


    # logic for taking a screenshot 
    self.cap = ScreenCapture.ScreenCaptureLogic() 

    # sets last function as the previous command 
    self.previous_command = self.conventional

    # dictionary for functions that manipulate the red/yellow/green slices 
    self.colorSwitcher = {"red" : {"show" : self.showRed, "hide" : self.hideRed , "view" : self.redView, "link" : self.linkRed, "unlink" : self.unlinkRed, "offset" : self.manipulateRed} ,
                     "yellow" : {"show" : self.showYellow, "hide" : self.hideYellow, "view" : self.yellowView, "link" : self.linkYellow, "unlink" : self.unlinkYellow, "offset" : self.manipulateYellow},
                     "green" : {"show" : self.showGreen, "hide" : self.hideGreen, "view" : self.greenView, "link" : self.linkGreen, "unlink" : self.unlinkGreen, "offset" : self.manipulateGreen }
    }
    # all other functions that don't have parameters

    # TODO: try and implement dictionary with parameters 
    self.functionSwitcher = {"conventional" : self.conventional, "screenshot" : self.captureView, "save scene" : self.saveScene, "repeat" : self.repeat,
                            "right" : self.rightAxis, "left" : self.leftAxis, "superior" : self.superiorAxis, "inferior" : self.inferiorAxis, 
                            "anterior" : self.anteriorAxis, "posterior" : self.posteriorAxis, "reset axis" : self.resetFocalPoint,
                            "zoom in" : self.zoomIn, "zoom out" : self.zoomOut

    }
    self.sliceOffset = 10
    self.zoom_factor = 0.5

  def pitch(self, threeDView, increment):
    threeDView.setPitchRollYawIncrement(increment)
    threeDView.pitch()

  def roll(self, threeDView, increment): 
    threeDView.setPitchRollYawIncrement(increment)
    threeDView.roll()

  def yaw(self, threeDView, increment): 
    threeDView.setPitchRollYawIncrement(increment)
    threeDView.yaw()

  # checks if a string is an int 
  def representsInt(self, s): 
    try: 
      int(s)
      return True
    except ValueError: 
      return False 

  # checks if a string is a float 
  def representsFloat(self, s):
    try:
      float(s)
      return True
    except ValueError:
      return False

  def setLayout(self, lm, layoutNumber):
    lm.setLayout(layoutNumber)


# ============================== TRYING OUT DICTIONARY METHOD =============================

  def zoomHelper(self): 
    for word in self.words:
      if(self.representsFloat(word)):
        self.zoom_factor = float(word)
        break


  def zoomIn(self): 
    self.zoomHelper()
    self.threeDView.setZoomFactor(self.zoom_factor)
    self.threeDView.zoomIn()
    self.previous_command = self.zoomIn
  
  def zoomOut(self): 
    self.zoomHelper()
    self.threeDView.setZoomFactor(self.zoom_factor)
    self.threeDView.zoomOut()
    self.previous_command = self.zoomOut


  def redView(self): 
    self.layoutManager.setLayout(6)

  def yellowView(self): 
    self.layoutManager.setLayout(7)

  def greenView(self): 
    self.layoutManager.setLayout(8)

  def showRed(self): 
    self.redNode.SetSliceVisible(1)

  def showYellow(self): 
    self.yellowNode.SetSliceVisible(1)

  def showGreen(self): 
    self.greenNode.SetSliceVisible(1)

  def hideRed(self): 
    self.redNode.SetSliceVisible(0)

  def hideYellow(self): 
    self.yellowNode.SetSliceVisible(0)

  def hideGreen(self): 
    self.greenNode.SetSliceVisible(0)

  def linkRed(self): 
    self.redCompositeNode.LinkedControlOn()

  def linkYellow(self): 
    self.yellowCompositeNode.LinkedControlOn()

  def linkGreen(self): 
    self.greenCompositeNode.LinkedControlOn()

  def unlinkRed(self): 
    self.redCompositeNode.LinkedControlOff()

  def unlinkYellow(self): 
    self.yellowCompositeNode.LinkedControlOff()

  def unlinkGreen(self): 
    self.greenCompositeNode.LinkedControlOff()

  def conventional(self): 
    self.layoutManager.setLayout(2)

  def resetFocalPoint(self): 
    self.threeDView.resetFocalPoint()

  def rightAxis(self): 
    self.threeDView.lookFromAxis(1)

  def leftAxis(self): 
    self.threeDView.lookFromAxis(2)

  def superiorAxis(self): 
    self.threeDView.lookFromAxis(3)

  def inferiorAxis(self): 
    self.threeDView.lookFromAxis(4)

  def anteriorAxis(self): 
    self.threeDView.lookFromAxis(5)

  def posteriorAxis(self): 
    self.threeDView.lookFromAxis(6)

  def manipulateSliceHelper(self, sliceController):
    for word in self.words: 
      if(self.representsFloat(word)):
        self.offset = float(word)
        break

    sliceController.setSliceOffsetValue(self.offset)

  def manipulateRed(self): 
    self.previous_command = self.manipulateRed

    self.manipulateSliceHelper(self.redController)

  def manipulateYellow(self): 
    self.previous_command = self.manipulateYellow

    self.manipulateSliceHelper(self.yellowController)

  def manipulateGreen(self): 
    self.previous_command = self.manipulateGreen

    self.manipulateSliceHelper(self.greenController)

  # repeats the previous command 
  def repeat(self): 
    function = self.previous_command
    try: 
      if(len(VoiceRecognitionLogic.parameters) == 1):
        function(VoiceRecognitionLogic.parameters[0])
      if(len(VoiceRecognitionLogic.parameters) == 2):
        function(VoiceRecognitionLogic.parameters[0], VoiceRecognitionLogic.parameters[1])
      else: 
        function()
    except NameError: 
      print("No previous command")
      slicer.util.delayDisplay("No previous command to execute", 0)

  # takes a screen shot of the views 
  def captureView(self):
    id = random.randint(1111, 9999)
    self.cap.showViewControllers(False)
    print(id)
    path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path += "\\" + str(id) + ".png"

    print(path)
    self.cap.captureImageFromView(None, path)
    slicer.util.delayDisplay("Screenshot saved to " + path, 0)

    self.cap.showViewControllers(True)

  # saves the scene 
  def saveScene(self): 
    sceneSaveDirectory = slicer.app.temporaryPath + "/saved-scene-" + time.strftime("%Y%m%d-%H%M%S")
    if not os.access(sceneSaveDirectory, os.F_OK):
      os.makedirs(sceneSaveDirectory)

    # Save the scene
    if slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(sceneSaveDirectory, None):
      slicer.util.delayDisplay("Scene saved to: {0}".format(sceneSaveDirectory), 0)
      logging.info("Scene saved to: {0}".format(sceneSaveDirectory))
    else:
      logging.error("Scene saving failed") 
      slicer.util.delayDisplay("Scene saving failed", 0)

  # pitch yaw and roll 
  def traversePitchYawRoll(self, word, function): 
    if(word in self.textLower):
        for secondWord in self.words: 
          if(self.representsInt(secondWord)):
            VoiceRecognitionLogic.parameters = []

            function(self.threeDView, int(secondWord))
            VoiceRecognitionLogic.parameters.append(self.threeDView)
            VoiceRecognitionLogic.parameters.append(int(secondWord))
            self.previous_command = function
            break


# ============================== END OF DICTIONARY METHOD =============================

  # toggle visibility 
  def toggle(self, node):
    node.SetSliceVisible(not node.GetSliceVisible())

  # change view axis 
  def changeAxis(self, threeDView, viewNumber):
    threeDView.lookFromAxis(viewNumber)

  # scroll through slice 
  def manipulateSlice(self, sliceController, offset):
    sliceController.setSliceOffsetValue(offset)


  def link(self, compositeNode): 
    compositeNode.LinkedControllOn()

  def unlink(self, compositeNode): 
    compositeNode.LinkedControlOff()

  # link/unlink 
  def toggleLink(self, compositeNode):
    compositeNode.SetLinkedControl(not compositeNode.GetLinkedControl())


  # input: takes speech-to-text and parses to execute commands 
  def parse(self, text):
    self.textLower = text.lower()
    self.words = text.split()
    #print(self.textLower)
    

    [word.lower() for word in self.words]

    # prase the words and execute commands 
    # TODO: put in more phrases/words in case speech recognition api thinks it's another word i.e. pitch and yaw 
    functions = {}


    # gets the functions for : show, hide, view, link, offset, and unlink 
    if("red" in self.textLower):
      functions = self.colorSwitcher.get("red")
      print(functions)

    elif("yellow" in self.textLower): 
      functions = self.colorSwitcher.get("yellow") 
      print(functions)

    elif("green" in self.textLower): 
      functions = self.colorSwitcher.get("green") 
      print(functions)

    for key in functions: 
      #print(key)
      if(key in self.textLower): 
        #print("key is in text")
        self.previous_command = functions.get(key)
        functions.get(key)()
        break

    # gets the rest of the functions 
    for key in self.functionSwitcher: 
      if(key in self.textLower): 
        print(key) 

        self.functionSwitcher.get(key)() 

        if(key != "repeat"): 
          print("NOT REPEAT")
          self.previous_command = self.functionSwitcher.get(key)
          print(self.previous_command) 

    # ================ PITCH YAW ROLL ================
    # pitch using different words 
    for word in VoiceRecognitionLogic.pitch_terms:
      self.traversePitchYawRoll(word, self.pitch)
    
    # yaw using different words 
    for word in VoiceRecognitionLogic.yaw_terms:
      self.traversePitchYawRoll(word, self.yaw)

    self.traversePitchYawRoll("roll", self.roll)


  # listens to the audio and returns the speech api output 
  def interpreter(self, recognizer, microphone):
    # maybe move to testing 
    if not isinstance(recognizer, sr.Recognizer):
      raise TypeError("recognizer must be Recognizer instance")

    if not isinstance(microphone, sr.Microphone):
      raise TypeError("microphone must be Mcirophone instance")

    with microphone as source:
      recognizer.adjust_for_ambient_noise(source)
      audio = recognizer.listen(source)
    #stop_listening = recognizer.listen_in_background(microphone, callback)
    try: 
      print(recognizer.recognize_google(audio))
      #self.parse(recognizer.recognize_google())
      return recognizer.recognize_google(audio)
    # handles any api/voice errors  errors 
    except sr.RequestError: 
      return "There was an issue in handling the request, please try again"
    except sr.UnknownValueError:
      return "Unable to Recognize speech"


# TODO: think of ways to test the module 
class VoiceRecognitionTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_VoiceRecognition1()

  def test_VoiceRecognition1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.lm = slicer.app.layoutManager()


    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = VoiceRecognitionLogic(self.lm)

    self.threeDView = self.lm.threeDWidget(0).threeDView()

    self.red = self.lm.sliceWidget('Red')
    self.yellow = self.lm.sliceWidget('Yellow')
    self.green = self.lm.sliceWidget('Green')

    self.redController = self.red.sliceController()
    self.yellowController = self.yellow.sliceController()
    self.greenController = self.green.sliceController()

    self.redLogic = self.red.sliceLogic()
    self.yellowLogic = self.yellow.sliceLogic()
    self.greenLogic = self.green.sliceLogic()

    self.redNode = self.redLogic.GetSliceNode()
    self.yellowNode = self.yellowLogic.GetSliceNode()
    self.greenNode = self.greenLogic.GetSliceNode()

    self.delayDisplay('Toggling slides')

    logic.toggle(self.redNode)
    logic.toggle(self.yellowNode)
    logic.toggle(self.greenNode)

    self.timer = qt.QTimer()


    self.delayDisplay('testing rotation')
    for i in range(10):
      self.delayDisplay("rotating", 250)
      logic.pitch(self.threeDView, 36)


    for i in range(10):
      self.delayDisplay("rotating", 250)
      logic.yaw(self.threeDView, 36)

    for i in range(10):
      self.delayDisplay("rotating", 250)
      logic.roll(self.threeDView, 36)

    self.delayDisplay("Testing Zoom")

    self.delayDisplay("Zoom in")
    logic.zoomIn(self.threeDView, 0.2)
    # time.sleep(1.0)

    self.delayDisplay("Zoom out")
    logic.zoomOut(self.threeDView, 0.2)

    self.delayDisplay("Red view")
    logic.setLayout(self.lm, 6)

    self.delayDisplay("Yellow View")
    logic.setLayout(self.lm, 7)

    self.delayDisplay("Green View")
    logic.setLayout(self.lm, 8)

    self.delayDisplay("Conventional")
    logic.setLayout(self.lm, 2)

    self.delayDisplay("View axis")
    for i in range(6):
      self.delayDisplay("view")
      logic.changeAxis(self.threeDView, i)

    # self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

