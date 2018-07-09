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
    print(5)
    # self.recognizer = sr.Recognizer()
    # self.microphone = sr.Microphone()
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

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
    self.microphoneSelector.currentIndexChanged.connect(self.microphone_changed)
    parametersFormLayout.addRow("Choose microphone: ", self.microphoneSelector)

    self.recognizer = sr.Recognizer()
    self.microphone = sr.Microphone()


    
    #self.microphone = sr.Microphone()


    # Sound energy level threshold value
    self.energyLevelThreshold = ctk.ctkSliderWidget()
    self.energyLevelThreshold.singleStep = 1 
    self.energyLevelThreshold.minimum = 0
    self.energyLevelThreshold.maximum = 5000
    self.energyLevelThreshold.value = 300
    self.energyLevelThreshold.valueChanged.connect(self.threshold_changed)
    self.energyLevelThreshold.tracking = False
    self.energyLevelThreshold.setToolTip("Sets the threshold value for sounds. Value below this threshold is considered silence. Silent rooms are from 0-100, values for speaking 150-3500. Adjust if necessary")
    

    parametersFormLayout.addRow("Sound Energy Threshold: ", self.energyLevelThreshold)
    #
    # threshold value
    #
    # self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    # self.imageThresholdSliderWidget.singleStep = 0.1
    # self.imageThresholdSliderWidget.minimum = -100
    # self.imageThresholdSliderWidget.maximum = 100
    # self.imageThresholdSliderWidget.value = 0.5
    # self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    # parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

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

    self.displayLabel = qt.QLabel("Press to begin listening:")
    self.displayLabel.setTextFormat(0) # plain text
    parametersFormLayout.addRow(self.displayLabel)

    self.textBox = qt.QLabel(" ")
    self.textBox.toolTip = "User input"
    self.textBox.setTextFormat(0) #plain text 
    parametersFormLayout.addRow("Speech: ", self.textBox)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    

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

  def onApplyButton(self):
    #print("testing")
    #elf.displayLabel.setText("Listening for speech....")
    slicer.util.delayDisplay("Listening for speech....")
    self.startLogic()
    #logic = VoiceRecognitionLogic()
    #self.textBox.setText(logic.initMicrophone())
    #print(logic.initMicrophone())

    #self.displayLabel.setText("Press to begin listening:")

    
  def startLogic(self):
    logic = VoiceRecognitionLogic()
    self.textBox.setText(logic.interpreter(self.recognizer, self.microphone))
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

    except sr.RequestError: 
      return "There was an issue in handling the request, please try again"
    except sr.UnknownValueError:
      return "Unable to Recognize speech"
    #return recognizer.recognize_google(audio)




  #def initMicrophone(self):


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
