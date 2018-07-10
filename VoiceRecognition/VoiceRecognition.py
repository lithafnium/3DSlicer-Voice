import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

import speech_recognition as sr
#
# VoiceRecognition
#

class VoiceRecognition(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "VoiceRecognition" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Steve Li (BWH)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
Voice control software for basic commands
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

    # Initializes layout manager: 

    self.lm = slicer.app.layoutManager()
    self.threeDView = self.lm.threeDWidget(0).threeDView()

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
    parametersFormLayout.addRow("Choose microphone: ", self.microphoneSelector)

    # Sound energy level threshold value
    self.energyLevelThreshold = ctk.ctkSliderWidget()
    self.energyLevelThreshold.singleStep = 1 
    self.energyLevelThreshold.minimum = 0
    self.energyLevelThreshold.maximum = 5000
    self.energyLevelThreshold.value = 300
    self.energyLevelThreshold.tracking = False
    self.energyLevelThreshold.setToolTip("Sets the threshold value for sounds. Value below this threshold is considered silence. Silent rooms are from 0-100, values for speaking 150-3500. Adjust if necessary")
    

    parametersFormLayout.addRow("Sound Energy Threshold: ", self.energyLevelThreshold)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    # self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    # self.enableScreenshotsFlagCheckBox.checked = 0
    # self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    # parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Begin Listneing")
    self.applyButton.toolTip = "Listens for voice."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # self.roll = qt.QPushButton("Roll")
    # self.roll.toolTip = "Listens for voice."
    # self.roll.enabled = True
    # parametersFormLayout.addRow(self.roll)

    # self.pitch = qt.QPushButton("Pitch")
    # self.pitch.toolTip = "Listens for voice."
    # self.pitch.enabled = True
    # parametersFormLayout.addRow(self.pitch)

    # self.yaw = qt.QPushButton("Yaw")
    # self.yaw.toolTip = "Listens for voice."
    # self.yaw.enabled = True
    # parametersFormLayout.addRow(self.yaw)

    # self.displayLabel = qt.QLabel("Press to begin listening:")
    # self.displayLabel.setTextFormat(0) # plain text
    # parametersFormLayout.addRow(self.displayLabel)

    self.textBox = qt.QLabel(" ")
    self.textBox.toolTip = "User input"
    self.textBox.setTextFormat(0) #plain text 
    parametersFormLayout.addRow("Speech: ", self.textBox)

    self.errors = qt.QLabel(" ")
    self.errors.setTextFormat(0)
    parametersFormLayout.addRow("Errors: ", self.errors)



    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    # self.pitch.connect('clicked(bool)', self.Pitch)
    # self.roll.connect('clicked(bool)', self.Roll)
    # self.yaw.connect('clicked(bool)', self.Yaw)


    self.microphoneSelector.currentIndexChanged.connect(self.microphone_changed)
    self.energyLevelThreshold.valueChanged.connect(self.threshold_changed)


    

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

    self.recognizer = sr.Recognizer()
    try: 
      self.microphone = sr.Microphone()

    except(IOError):
      print("ERROR: No default microphone. Check if microphone is plugged in")
      self.errors.setText("ERROR: No default microphone. Check if microphone is plugged in")

  def cleanup(self):
    pass

  def onSelect(self):
    print(5)

  # logic when threshold is changed 
  def threshold_changed(self):
    print(self.energyLevelThreshold.value)
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

  # def Roll(self): 
  #   self.threeDView.roll()

  # def Pitch(self): 
  #   self.threeDView.pitch()

  # def Yaw(self):
  #   self.threeDView.yaw()

  def onApplyButton(self):
    #elf.displayLabel.setText("Listening for speech....")
    slicer.util.delayDisplay("Wait...", 2000)
    self.startLogic()
    #logic = VoiceRecognitionLogic()
    #self.textBox.setText(logic.initMicrophone())
    #print(logic.initMicrophone())

    #self.displayLabel.setText("Press to begin listening:")

    
  def startLogic(self):
    logic = VoiceRecognitionLogic()
    text = logic.interpreter(self.recognizer, self.microphone)
    self.textBox.setText(text)
    logic.parse(self.lm, text)

#
# VoiceRecognitionLogic
#

class VoiceRecognitionLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  """
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
    25 -  Four Up Quantitative View             36  -  Conventional Plot View 
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

  def representsInt(self, s): 
    try: 
      int(s)
      return True
    except ValueError: 
      return False 

  def pitch(self, threeDView, increment):
    threeDView.setPitchRollYawIncrement(increment)
    threeDView.pitch()

  def roll(self, threeDView, increment): 
    threeDView.setPitchRollYawIncrement(increment)
    threeDView.roll()

  def yaw(self, threeDView, increment): 
    threeDView.setPitchRollYawIncrement(increment)
    threeDView.yaw()

  def zoomIn(self, threeDView, increment):
    threeDView.setZoomFactor(increment)
    threeDView.zoomIn()

  def zoomOut(self, threeDView, increment): 
    threeDView.setZoomFactor(increment)
    threeDView.zoomOut()


  def parse(self, layoutManager, text):
    words = text.split()
    threeDView = layoutManager.threeDWidget(0).threeDView()

    red = layoutManager.sliceWidget('Red')
    yellow = layoutManager.sliceWidget('Yellow')
    green = layoutManager.sliceWidget('Green')

    redController = red.sliceController()
    yellowController = yellow.sliceController()
    greenController = green.sliceController()

    redLogic = red.sliceLogic()
    yellowLogic = yellow.sliceLogic()
    greenLogic = green.sliceLogic()

    redNode = redLogic.GetSliceNode()
    yellowNode = yellowLogic.GetSliceNode()
    greenNode = greenLogic.GetSliceNode()

    [word.lower() for word in words]

    # prase the words and execute commands 
    for word in words: 
      if(word == "pitch"): 
        for secondWord in words: 
          if(self.representsInt(secondWord)):
            self.pitch(threeDView, int(secondWord))

      if(word == "yaw"): 
        for secondWord in words: 
          if(self.representsInt(secondWord)):
            self.yaw(threeDView, int(secondWord))

      if(word == "roll"): 
        for secondWord in words: 
          if(self.representsInt(secondWord)):
            self.roll(threeDView, int(secondWord))


  def interpreter(self, recognizer, microphone):
    # maybe move to testing 
    if not isinstance(recognizer, sr.Recognizer):
      raise TypeError("recognizer must be Recognizer instance")

    if not isinstance(microphone, sr.Microphone):
      raise TypeError("microphone must be Mcirophone instance")

    with microphone as source:
      recognizer.adjust_for_ambient_noise(source)
      audio = recognizer.listen(source)
    
    try: 
      return recognizer.recognize_google(audio)
    # handles any api/voice errors  errors 
    except sr.RequestError: 
      return "There was an issue in handling the request, please try again"
    except sr.UnknownValueError:
      return "Unable to Recognize speech"



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
    logic = VoiceRecognitionLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
