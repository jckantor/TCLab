

import datetime
import tornado

from .tclab import TCLab, TCLabModel
from .historian import Historian, Plotter
from .labtime import labtime, clock

from ipywidgets import Button, Label, FloatSlider, HBox, VBox, Checkbox,\
    IntText


def actionbutton(description, action, disabled=True):
    """Return button widget with specified label and callback action."""
    button = Button(description=description, disabled=disabled)
    button.on_click(action)

    return button


def labelledvalue(label, value, units=''):
    """Return widget and HBox for label, value, units display."""
    labelwidget = Label(value=label)
    valuewidget = Label(value=str(value))
    unitwidget = Label(value=units)
    box = HBox([labelwidget, valuewidget, unitwidget])

    return valuewidget, box


def slider(label, action=None, minvalue=0, maxvalue=100, disabled=True):
    """Return slider widget for specified label and action callback."""
    sliderwidget = FloatSlider(description=label, min=minvalue, max=maxvalue)
    sliderwidget.disabled = disabled
    if action:
        sliderwidget.observe(action, names='value')

    return sliderwidget


class NotebookInteraction():
    """Base class for Notebook UI interaction controllers.

    You should inherit from this class to build new interactions.
    """
    def __init__(self):
        self.lab = None
        self.ui = None

    def update(self, t):
        """Called on a timer to update the interaction.

        t is the current simulation time. """
        raise NotImplementedError

    def connect(self, lab):
        """This is called when the interface connects to a lab

        lab is an instance of TCLab or TCLabModel
        """
        self.lab = lab
        self.lab.connected = True

    def start(self):
        """Called when the Start button is pressed"""
        raise NotImplementedError

    def stop(self):
        """Called when the Stop button is pressed"""
        raise NotImplementedError

    def disconnect(self):
        """Called when the interface disconnects from a lab"""
        self.lab.connected = False


class SimpleInteraction(NotebookInteraction):
    """Simple interaction with the TCLab

    Provides a ui with two sliders for the heaters and text boxes showing
    the temperatures.

    Notice that the class must define a "layout" property suitable to pass as
    thelayout argument to Plotter. It must also define a "sources" property
    suitable to pass to Historian. This is typically only possible after
    connecting, so in this class we define sources in .connect()

    """
    def __init__(self):
        super().__init__()

        self.layout = (('Q1', 'Q2'),
                       ('T1', 'T2'))

        # Sliders for heaters
        self.Q1widget = slider('Q1', self.action_Q1)
        self.Q2widget = slider('Q2', self.action_Q2)

        heaters = VBox([self.Q1widget, self.Q2widget])

        # Temperature display
        self.T1widget, T1box = labelledvalue('T1:', 0, '°C')
        self.T2widget, T2box = labelledvalue('T2:', 0, '°C')

        temperatures = VBox([T1box, T2box])

        self.ui = HBox([heaters, temperatures])

    def update(self, t):
        self.T1widget.value = '{:2.1f}'.format(self.lab.T1)
        self.T2widget.value = '{:2.1f}'.format(self.lab.T2)

    def connect(self, lab):
        super().connect(lab)
        self.sources = self.lab.sources

    def start(self):
        self.Q1widget.disabled = False
        self.Q2widget.disabled = False

    def stop(self):
        self.Q1widget.disabled = True
        self.Q2widget.disabled = True

    def action_Q1(self, change):
        """Change heater 1 power."""
        self.lab.Q1(change['new'])

    def action_Q2(self, change):
        """Change heater 2 power."""
        self.lab.Q2(change['new'])


class NotebookUI:
    def __init__(self, Controller=SimpleInteraction):
        self.timer = tornado.ioloop.PeriodicCallback(self.update, 1000)
        self.lab = None
        self.plotter = None
        self.historian = None
        self.seconds = 0
        self.firstsession = True

        # Model or real
        self.usemodel = Checkbox(value=False, description='Use model')
        self.usemodel.observe(self.togglemodel, names='value')
        self.speedup = slider('Speedup', minvalue=1, maxvalue=10)
        modelbox = HBox([self.usemodel, self.speedup])

        # Buttons
        self.connect = actionbutton('Connect', self.action_connect, False)
        self.start = actionbutton('Start', self.action_start)
        self.stop = actionbutton('Stop', self.action_stop)
        self.disconnect = actionbutton('Disconnect', self.action_disconnect)

        buttons = HBox([self.connect, self.start, self.stop, self.disconnect])

        # status
        self.timewidget, timebox = labelledvalue('Timestamp:', 'No data')
        self.sessionwidget, sessionbox = labelledvalue('Session:', 'No data')
        statusbox = HBox([timebox, sessionbox])

        self.controller = Controller()

        self.gui = VBox([HBox([modelbox, buttons]),
                         statusbox,
                         self.controller.ui,
                         ])

    def update(self):
        """Update GUI display."""
        self.timer.callback_time = 1000/self.speedup.value
        labtime.set_rate(self.speedup.value)

        self.timewidget.value = '{:.2f}'.format(labtime.time())
        self.controller.update(labtime.time())
        self.plotter.update(labtime.time())

    def togglemodel(self, change):
        """Speedup can only be enabled when working with the model"""
        self.speedup.disabled = not change['new']
        self.speedup.value = 1

    def action_start(self, widget):
        """Start TCLab operation."""
        if not self.firstsession:
            self.historian.new_session()
        self.firstsession = False
        self.sessionwidget.value = str(self.historian.session)

        self.start.disabled = True
        self.stop.disabled = False
        self.disconnect.disabled = True

        self.controller.start()
        self.timer.start()
        labtime.reset()
        labtime.start()

    def action_stop(self, widget):
        """Stop TCLab operation."""
        self.timer.stop()
        labtime.stop()

        self.start.disabled = False
        self.stop.disabled = True
        self.disconnect.disabled = False
        self.controller.stop()

    def action_connect(self, widget):
        """Connect to TCLab."""
        if self.usemodel.value:
            self.lab = TCLabModel()
        else:
            self.lab = TCLab()
        labtime.stop()
        labtime.reset()

        self.controller.connect(self.lab)
        self.historian = Historian(self.controller.sources)
        self.plotter = Plotter(self.historian,
                               twindow=500,
                               layout=self.controller.layout)

        self.usemodel.disabled = True
        self.connect.disabled = True
        self.start.disabled = False
        self.disconnect.disabled = False

    def action_disconnect(self, widget):
        """Disconnect TCLab."""
        self.lab.close()

        self.controller.disconnect()

        self.usemodel.disabled = False
        self.connect.disabled = False
        self.disconnect.disabled = True
        self.start.disabled = True
