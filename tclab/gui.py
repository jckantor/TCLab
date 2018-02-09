import datetime
import tornado

from .tclab import TCLab, TCLabModel
from .historian import Historian, Plotter
from .clock import setnow, setup

from ipywidgets import Button, Label, FloatSlider, HBox, VBox, Checkbox, IntText


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


def slider(label, action, minvalue=0, maxvalue=100, disabled=True):
    """Return slider widget for specified label and action callback."""
    sliderwidget = FloatSlider(description=label, min=minvalue, max=maxvalue)
    sliderwidget.disabled = disabled
    sliderwidget.observe(action, names='value')

    return sliderwidget


class NotebookUI:
    def __init__(self):
        self.timer = tornado.ioloop.PeriodicCallback(self.update, 1000)
        self.lab = None
        self.plotter = None
        self.seconds = 0
        self.firstsession = True

        # Model or real
        self.usemodel = Checkbox(value=False, description='Use model')
        speeduplabel = Label('Speedup')
        self.speedup = IntText(value=1)
        self.speedup.disabled = True
        modelbox = HBox([self.usemodel, speeduplabel, self.speedup])

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

        # Sliders for heaters
        self.Q1widget = slider('Q1', self.action_Q1)
        self.Q2widget = slider('Q2', self.action_Q2)

        heaters = VBox([self.Q1widget, self.Q2widget])

        # Temperature display
        self.T1widget, T1box = labelledvalue('T1:', 0, '°C')
        self.T2widget, T2box = labelledvalue('T2:', 0, '°C')

        temperatures = VBox([T1box, T2box])

        self.gui = VBox([modelbox,
                         buttons,
                         statusbox,
                         HBox([heaters, temperatures]),
                         ])

    def update(self):
        """Update GUI display."""
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')
        self.seconds += self.speedup.value
        if self.usemodel.value:
            setnow(self.seconds)
        self.timewidget.value = timestamp
        self.T1widget.value = '{:2.1f}'.format(self.lab.T1)
        self.T2widget.value = '{:2.1f}'.format(self.lab.T2)
        self.plotter.update(self.seconds)

    def action_start(self, widget):
        """Start TCLab operation."""
        self.seconds = 0
        if not self.firstsession:
            self.historian.new_session()
        self.firstsession = False
        self.sessionwidget.value = str(self.historian.session)

        self.start.disabled = True
        self.stop.disabled = False
        self.disconnect.disabled = True

        self.Q1widget.disabled = False
        self.Q2widget.disabled = False

        self.timer.start()

    def action_stop(self, widget):
        """Stop TCLab operation."""
        self.timer.stop()

        self.start.disabled = False
        self.stop.disabled = True
        self.disconnect.disabled = False
        self.Q1widget.disabled = True
        self.Q2widget.disabled = True

    def action_connect(self, widget):
        """Connect to TCLab."""
        if self.usemodel.value:
            self.lab = TCLabModel()
        else:
            self.lab = TCLab()
        self.historian = Historian(self.lab.sources)
        self.plotter = Plotter(self.historian,
                               layout=(('Q1', 'Q2'),
                                       ('T1', 'T2')))
        self.lab.connected = True

        self.usemodel.disabled = True
        self.connect.disabled = True
        self.start.disabled = False
        self.disconnect.disabled = False

    def action_disconnect(self, widget):
        """Disconnect TCLab."""
        self.lab.close()
        self.lab.connected = False

        self.usemodel.disabled = False
        self.connect.disabled = False
        self.disconnect.disabled = True
        self.start.disabled = True

    def action_Q1(self, change):
        """Change heater 1 power."""
        self.lab.Q1(change['new'])

    def action_Q2(self, change):
        """Change heater 2 power."""
        self.lab.Q2(change['new'])
