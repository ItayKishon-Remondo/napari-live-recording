from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QPushButton
from superqt import QLabeledSlider
from PyQt5.QtWidgets import QFormLayout, QGridLayout
from abc import ABC, abstractmethod
from dataclasses import replace
from napari_live_recording_rework.common import ROI

class LocalWidget(ABC):
    def __init__(self, internalWidget : QWidget, name: str, unit: str = "", orientation: str = "left") -> None:
        """Common widget constructor.

        Args:
            internalWidget (QWidget): widget to construct the form layout.
            name (str): parameter label description.
            unit (str, optional): parameter unit measure. Defaults to "".
            orientation (str, optional): label orientation on the layout. Defaults to "left".
        """
        self.__name = name
        self.__unit = unit
        labelStr = (self.__name + " (" + self.__unit + ")" if self.__unit != "" else self.__name)
        self.__label = QLabel(labelStr)
        self.__label.setAlignment(Qt.AlignRight)
        self.__layout = QFormLayout()
        self.__widget = internalWidget
        self._buildLayout(orientation)
    
    def _buildLayout(self, orientation: str) -> None:
        """Builds the QFormLayout depending on the input orientation.

        Args:
            orientation (str): specifies the label orientation of the widget: either "left" or "righ" of the internal widget.
        """
        if orientation == "right":
            self.__layout.addRow(self.__widget, self.__label)
        else: # default layout
            self.__layout.addRow(self.__label, self.__widget)

    @property
    def layout(self) -> QFormLayout:
        """ QFormLayout structured as |<Text label>|<Specific widget>| (this must be built in the specific class constructor).
        """
        return self.__layout

    @abstractmethod
    def changeWidgetSettings(self, newParam) -> None:
        """Common widget update parameter abstract method.
        """
        pass

    @property
    @abstractmethod
    def value(self) -> None:
        """Widget current value.
        """
        pass

    @property
    @abstractmethod
    def isEnabled(self) -> bool:
        """Widget is enabled for editing (True) or not (False).
        """
        pass
    
    @isEnabled.setter
    @abstractmethod
    def isEnabled(self, enable : bool) -> None:
        """Sets widget enabled for editing (True) or not (False).
        """
        pass
    
    @property
    @abstractmethod
    def signals(self) -> dict[str, pyqtSignal]:
        """Common widget method to expose signals to the device.
        """
        pass

class ComboBox(LocalWidget):
    def __init__(self, param : list[str], name : str, unit : str = "", orientation: str = "left") -> None:
        """ComboBox widget.

        Args:
            param (list[str]): list of parameters added to the ComboBox.
            name (str): parameter label description.
            unit (str, optional): parameter unit measure. Defaults to "".
            orientation (str, optional): label orientation on the layout. Defaults to "left".
        """
        self.__combobox = QComboBox()
        self.__combobox.addItems(param)
        super().__init__(self.__combobox, name, unit, orientation)
    
    def changeWidgetSettings(self, newParam: list[str]) -> None:
        """ComboBox update widget parameter method. Old list of items is deleted.

        Args:
            newParam (list[str]): new list of parameters to add to the ComboBox.
        """
        self.__combobox.clear()
        self.__combobox.addItems(newParam)
    
    @property
    def value(self) -> tuple[str, int]:
        """Returns a tuple containing the ComboBox current text and index.
        """
        return (self.__combobox.currentText(), self.__combobox.currentIndex())
    
    @property
    def isEnabled(self) -> bool:
        """ComboBox is enabled for editing (True) or not (False).
        """
        return self.__combobox.isEnabled()
    
    @isEnabled.setter
    def isEnabled(self, enable : bool) -> None:
        """Sets the ComboBox enabled for editing (True) or disabled (False).
        """
        self.__combobox.setEnabled(enable)
    
    @property
    def signals(self) -> dict[str, pyqtSignal]:
        """Returns a list of signals available for the ComboBox widget.
        Exposed signals are:
        
        - currentIndexChanged,
        - currentTextChanged

        Returns:
            dict: dict of signals (key: function name, value: function objects).
        """
        return {
            "currentIndexChanged" : self.__combobox.currentIndexChanged,
            "currentTextChanged" : self.__combobox.currentTextChanged
        }
        

class SpinBox(LocalWidget):
    def __init__(self, param: tuple[int, int, int], name: str, unit: str = "", orientation: str = "left") -> None:
        """SpinBox widget.

        Args:
            param (tuple[int, int, int]): parameters for SpinBox settings: (<minimum_value>, <maximum_value>, <starting_value>)
            name (str): parameter label description.
            unit (str, optional): parameter unit measure. Defaults to "".
            orientation (str, optional): label orientation on the layout. Defaults to "left".
        """
        self.__spinbox = QSpinBox(self)
        self.__spinbox.setRange(param[0], param[1])
        self.__spinbox.setValue(param[2])
        super().__init__(self.__spinbox, name, unit, orientation)
    
    def changeWidgetSettings(self, newParam : tuple(int, int, int)) -> None:
        """SpinBox update widget parameter method.

        Args:
            newParam (tuple(int, int, int)): new parameters for SpinBox settings: (<minimum_value>, <maximum_value>, <starting_value>)
        """
        self.__spinbox.setRange(newParam[0], newParam[1])
        self.__spinbox.setValue(newParam[2])
    
    @property
    def value(self) -> int:
        """Returns the SpinBox current value.
        """
        return self.__spinbox.value()
    
    @property
    def isEnabled(self) -> bool:
        """SpinBox is enabled for editing (True) or not (False).
        """
        return self.__spinbox.isEnabled()
    
    @isEnabled.setter
    def isEnabled(self, enable : bool) -> None:
        """Sets the SpinBox enabled for editing (True) or disabled (False).
        """
        self.__spinbox.setEnabled(enable)
    
    @property
    def signals(self) -> dict[str, pyqtSignal]:
        """Returns a list of signals available for the SpinBox widget.
        Exposed signals are:
        
        - valueChanged,
        - textChanged

        Returns:
            dict: dict of signals (key: function name, value: function objects).
        """
        return {
            "valueChanged" : self.__spinbox.valueChanged,
            "textChanged" : self.__spinbox.textChanged
        }

class DoubleSpinBox(LocalWidget):
    def __init__(self, param: tuple[float, float, float], name: str, unit: str = "", orientation: str = "left") -> None:
        """DoubleSpinBox widget.

        Args:
            param (tuple[float, float, float]): parameters for spinbox settings: (<minimum_value>, <maximum_value>, <starting_value>)
            name (str): parameter label description.
            unit (str, optional): parameter unit measure. Defaults to "".
            orientation (str, optional): label orientation on the layout. Defaults to "left".
        """
        self.__spinbox = QDoubleSpinBox()
        self.__spinbox.setRange(param[0], param[1])
        self.__spinbox.setValue(param[2])
        super().__init__(self.__spinbox, name, unit, orientation)

    def changeWidgetSettings(self, newParam : tuple[float, float, float]) -> None:
        """DoubleSpinBox update widget parameter method.

        Args:
            newParam (tuple[float, float, float]): new parameters for SpinBox settings: (<minimum_value>, <maximum_value>, <starting_value>)
        """
        self.__spinbox.setRange(newParam[0], newParam[1])
        self.__spinbox.setValue(newParam[2])
    
    @property
    def value(self) -> float:
        """Returns the DoubleSpinBox current value.
        """
        return self.__spinbox.value()
    
    @property
    def isEnabled(self) -> bool:
        """DoubleSpinBox is enabled for editing (True) or not (False).
        """
        return self.__spinbox.isEnabled()
    
    @isEnabled.setter
    def isEnabled(self, enable : bool) -> None:
        """Sets the DoubleSpinBox enabled for editing (True) or disabled (False).
        """
        self.__spinbox.setEnabled(enable)

    @property
    def signals(self) -> dict[str, pyqtSignal]:
        """Returns a list of signals available for the SpinBox widget.
        Exposed signals are:
        
        - valueChanged,
        - textChanged

        Returns:
            dict: dict of signals (key: function name, value: function objects).
        """
        return {
            "valueChanged" : self.__spinbox.valueChanged,
            "textChanged" : self.__spinbox.textChanged
        }

class LabeledSlider(LocalWidget):
    def __init__(self, param: tuple[int, int, int], name: str, unit: str = "", orientation: str = "left") -> None:
        """Slider widget.

        Args:
            param (tuple[int, int, int])): parameters for spinbox settings: (<minimum_value>, <maximum_value>, <starting_value>)
            name (str): parameter label description.
            unit (str, optional): parameter unit measure. Defaults to "".
            orientation (str, optional): label orientation on the layout. Defaults to "left".
        """
        super().__init__(name, unit)
        self.__slider = QLabeledSlider(Qt.Horizontal)
        self.__slider.setRange(param[0], param[1])
        self.__slider.setValue(param[2])
        super().__init__(self.__slider, name, unit, orientation)
    
    def changeWidgetSettings(self, newParam : tuple[int, int, int]) -> None:
        """Slider update widget parameter method.

        Args:
            newParam (tuple[int, int, int]): new parameters for SpinBox settings: (<minimum_value>, <maximum_value>, <starting_value>)
        """
        self.__slider.setRange(newParam[0], newParam[1])
        self.__slider.setValue(newParam[2])
    
    @property
    def value(self) -> int:
        """Returns the Slider current value.
        """
        return self.__slider.value()
        
    @property
    def isEnabled(self) -> bool:
        """LabeledSlider is enabled for editing (True) or not (False).
        """
        return self.__slider.isEnabled()
    
    @isEnabled.setter
    def isEnabled(self, enable: bool) -> None:
        """Sets the DoubleSpinBox enabled for editing (True) or disabled (False).
        """
        self.__slider.setEnabled(enable)

    @property
    def signals(self) -> dict[str, pyqtSignal]:
        """Returns a list of signals available for the SpinBox widget.
        Exposed signals are:
        
        - valueChanged

        Returns:
            dict: dict of signals (key: function name, value: function objects).
        """
        return {
            "valueChanged" : self.__slider.valueChanged
        }

class LineEdit(LocalWidget):
    
    def __init__(self, param: str, name: str, unit: str = "", orientation: str = "left", editable = False) -> None:
        """LineEdit widget. Editing disabled by default.

        Args:
            param (str): line edit contents
            name (str): parameter label description.
            unit (str, optional): parameter unit measure. Defaults to "".
            orientation (str, optional): label orientation on the layout. Defaults to "left".
            editable (bool, optional): sets the LineEdit to be editable. Defaults to False.
        """
        super().__init__(name, unit)
        self.__lineEdit = QLineEdit(self, param)
        self.__lineEdit.setEnabled(editable)
        super().__init__(self.__lineEdit, name, unit, orientation)
    
    def changeWidgetSettings(self, newParam : str) -> None:
        """Updates LineEdit text contents.

        Args:
            newParam (str): new string for LineEdit.
        """
        self.__lineEdit.setText(newParam)

    @property
    def value(self) -> str:
        """Returns the LineEdit current text.
        """
        return self.__lineEdit.text()
    
    @property
    def isEnabled(self) -> bool:
        """LineEdit is enabled for editing (True) or not (False).
        """
        return self.__lineEdit.isEnabled()
    
    @property
    @isEnabled.setter
    def isEnabled(self, enable: bool) -> None:
        """Sets the LineEdit enabled for editing (True) or disabled (False).
        """
        self.__lineEdit.setEnabled(enable)
    
    @property
    def signals(self) -> dict[str, pyqtSignal]:
        """Returns a list of signals available for the LineEdit widget.
        Exposed signals are:
        
        - textChanged,
        - textEdited

        Returns:
            dict: dict of signals (key: function name, value: function objects).
        """
        return {
            "textChanged" : self.__lineEdit.textChanged,
            "textEdited" : self.__lineEdit.textEdited
        }

class CameraSelection(QWidget):
    def __init__(self) -> None:
        """Camera selection widget. It includes the following widgets:

        - a ComboBox for camera selection based on strings to identify each camera type;
        - a LineEdit for camera ID or serial number input
        - a QPushButton to add the camera

        Widget layout:
        |(0,0) ComboBox|(0,1) QPushButton|
        |(1,0) LineEdit|(1,1)            |

        The QPushButton remains disabled as long as no camera is selected (first index is highlited). 
        """
        super(CameraSelection, self).__init__()
        self.camerasComboBox = ComboBox([], "Camera")
        self.idLineEdit = LineEdit(param="", name="Camera ID/SN", editable=True)
        self.addButton = QPushButton("Add camera", self)
        self.addButton.setEnabled(False)

        # create widget layout
        self.widgetLayout = QGridLayout(self)
        self.widgetLayout.addLayout(self.camerasComboBox.layout, 0, 0, 1, 1)
        self.widgetLayout.addWidget(self.addButton, 0, 1, 1, 1)
        self.widgetLayout.addLayout(self.idLineEdit.layout, 1, 0, 1, 1)
    
    def setAvailableCameras(self, cameras: list[str]) -> None:
        """Sets the ComboBox with the list of available camera devices.

        Args:
            cameras (list[str]): list of available camera devices.
        """
        # we need to extend the list of available cameras with a selection text
        cameras.insert(0, "Select device")
        self.camerasComboBox.changeWidgetSettings(cameras)

class ROIHandling(QWidget):
    def __init__(self, cameraROI : ROI) -> None:
        super(ROIHandling, self).__init__()
        self.__changeROIRequested = pyqtSignal(ROI)
        self.__fullROIRequested = pyqtSignal(ROI)

        # todo: maybe this is inefficient...
        # in previous implementation
        # copying the reference would cause
        # issues when changing the ROI
        # so we'll create a local copy
        # and discard the input
        self.__sensorFullROI = replace(cameraROI)

        # todo: these widgets are not
        # our custom LocalWidgets
        # but since they are common
        # for all types of cameras
        # it is not worth to customize them...
        # ... right?
        self.__offsetXLabel = QLabel("Offset X (px)", self)
        self.__offsetXLabel.setAlignment(Qt.AlignCenter)

        self.__offsetXSpinBox = QSpinBox(self)
        self.__offsetXSpinBox.setRange(0, self.__sensorFullROI.offset_x)
        self.__offsetXSpinBox.setSingleStep(self.__sensorFullROI.ofs_x_step)
        self.__offsetXSpinBox.setValue(0)

        self.__offsetYLabel = QLabel("Offset Y (px)", self)
        self.__offsetYLabel.setAlignment(Qt.AlignCenter)

        self.__offsetYSpinBox = QSpinBox()
        self.__offsetYSpinBox.setRange(0, self.__sensorFullROI.offset_y)
        self.__offsetYSpinBox.setSingleStep(self.__sensorFullROI.ofs_y_step)
        self.__offsetYSpinBox.setValue(0)

        self.__widthLabel = QLabel("Width (px)", self)
        self.__widthLabel.setAlignment(Qt.AlignCenter)

        self.__widthSpinBox = QSpinBox(self)
        self.__widthSpinBox.setRange(0, self.__sensorFullROI.width)
        self.__widthSpinBox.setSingleStep(self.__sensorFullROI.width_step)
        self.__widthSpinBox.setValue(self.__sensorFullROI.width)

        self.__heightLabel = QLabel("Height (px)", self)
        self.__heightLabel.setAlignment(Qt.AlignCenter)

        self.__heightSpinBox = QSpinBox(self)
        self.__heightSpinBox.setRange(0, self.__sensorFullROI.height)
        self.__heightSpinBox.setSingleStep(self.__sensorFullROI.height_step)
        self.__heightSpinBox.setValue(self.__sensorFullROI.height)

        self.__changeROIButton = QPushButton("Set ROI", self)
        self.__changeROIButton.setEnabled(False)

        self.__fullROIButton = QPushButton("Full frame", self)
        self.__fullROIButton.setEnabled(False)

        self.__layout = QGridLayout(self)
        self.__layout.addWidget(self.__offsetXLabel, 0, 0)
        self.__layout.addWidget(self.__offsetXSpinBox, 0, 1)
        self.__layout.addWidget(self.__offsetYSpinBox, 0, 2)
        self.__layout.addWidget(self.__offsetYLabel, 0, 3)
        
        self.__layout.addWidget(self.__widthLabel, 1, 0)
        self.__layout.addWidget(self.__widthSpinBox, 1, 1)
        self.__layout.addWidget(self.__heightSpinBox, 1, 2)
        self.__layout.addWidget(self.__heightLabel, 1, 3)
        self.__layout.addWidget(self.__changeROIButton, 2, 0, 1, 4)
        self.__layout.addWidget(self.__fullROIButton, 3, 0, 1, 4)

        # "clicked" signals are connected to private slots.
        # These slots expose the signals available to the user
        # to process the new ROI information if necessary.
        self.__changeROIButton.clicked.connect(self._onROIChanged)
        self.__fullROIButton.clicked.connect(self._onFullROI)
    
    def changeWidgetSettings(self, settings : ROI):
        """ROI handling update widget settings method.
        This method is useful whenever the ROI values are changed based
        on some device requirements and adapted.

        Args:
            settings (ROI): new ROI settings to change the widget values and steps.
        """
        self.__offsetXSpinBox.setSingleStep(settings.ofs_x_step)
        self.__offsetXSpinBox.setValue(settings.offset_x)

        self.__offsetYSpinBox.setSingleStep(settings.ofs_y_step)
        self.__offsetYSpinBox.setValue(settings.offset_y)

        self.__widthSpinBox.setSingleStep(settings.width_step)
        self.__widthSpinBox.setValue(settings.width)
        
        self.__heightSpinBox.setSingleStep(settings.height_step)
        self.__heightSpinBox.setValue(settings.height)
        
    
    def _onROIChanged(self) -> None:
        """Private slot for ROI changed button pressed. Exposes a signal with the updated ROI settings.
        """
        # read the current SpinBoxes status
        newRoi = ROI(
            offset_x=self.__offsetXSpinBox.value(),
            ofs_x_step=self.__offsetXSpinBox.singleStep(),
            offset_y=self.__offsetYSpinBox.value(),
            ofs_y_step=self.__offsetXSpinBox.singleStep(),            
            width=self.__widthSpinBox.value(),
            width_step=self.__widthSpinBox.singleStep(),
            height=self.__heightSpinBox.value(),
            height_step=self.__heightSpinBox.singleStep()
        )
        self.__changeROIRequested.emit(newRoi)

    def _onFullROI(self) -> None:
        """Private slot for full ROI button pressed. Exposes a signal with the full ROI settings.
        It also returns the widget settings to their original value.
        """
        self.changeWidgetSettings(self.__sensorFullROI)
        self.__fullROIRequested.emit(replace(self.__sensorFullROI))
    
    @property
    def layout(self) -> QGridLayout:
        """The ROI handling grid layout to add to the camera widgets.
        """
        return self.__layout
    
    @property
    def signals(self) -> dict[str, pyqtSignal]:
        """Returns a list of signals available for the ROIHandling widget.
        Exposed signals are:
        
        - changeROIRequested,
        - fullROIRequested,

        Returns:
            dict: dict of signals (key: function name, value: function objects).
        """
        return {
            "changeROIRequested" : self.__changeROIRequested,
            "fullROIRequested" : self.__fullROIRequested,
        }