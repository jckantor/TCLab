import datetime
import tornado

from .tclab import TCLab

from ipywidgets import Button, Label, FloatSlider, HBox, VBox


def actionbutton(description, action, disabled=True):
    button = Button(description=description, disabled=disabled)
    button.on_click(action)

    return button


def labelledvalue(label, value, units=''):
    labelwidget = Label(value=label)
    valuewidget = Label(value=str(value))
    unitwidget = Label(value=units)
    box = HBox([labelwidget, valuewidget, unitwidget])

    return valuewidget, box


def slider(label, action, minvalue=0, maxvalue=100, disabled=True):
    sliderwidget = FloatSlider(description=label, min=minvalue, max=maxvalue)
    sliderwidget.disabled = disabled
    sliderwidget.observe(action, names='value')

    return sliderwidget


class NotebookUI:
    def __init__(self):
        self.timer = tornado.ioloop.PeriodicCallback(self.update, 1000)
        self.lab = None

        # Buttons
        self.connect = actionbutton('Connect', self.action_connect, False)
        self.start = actionbutton('Start', self.action_start)
        self.stop = actionbutton('Stop', self.action_stop)
        self.disconnect = actionbutton('Disconnect', self.action_disconnect)

        buttons = HBox([self.connect, self.start, self.stop, self.disconnect])

        # time
        self.timewidget, timebox = labelledvalue('Timestamp:', 'No data')

        # Sliders for heaters
        self.Q1widget = slider('Q1', self.action_Q1)
        self.Q2widget = slider('Q2', self.action_Q2)

        heaters = VBox([self.Q1widget, self.Q2widget])

        # Temperature display
        self.T1widget, T1box = labelledvalue('T1:', 0, '°C')
        self.T2widget, T2box = labelledvalue('T2:', 0, '°C')

        temperatures = VBox([T1box, T2box])

        self.gui = VBox([buttons,
                    timebox,
                    HBox([heaters, temperatures]),
                    ])

    def update(self):
        timestamp = datetime.datetime.now().isoformat(timespec='seconds')
        self.timewidget.value = timestamp
        self.T1widget.value = '{:2.1f}'.format(self.lab.T1)
        self.T2widget.value = '{:2.1f}'.format(self.lab.T2)

    def action_start(self, widget):
        self.timer.start()
        self.start.disabled = True
        self.stop.disabled = False
        self.disconnect.disabled = True

        self.Q1widget.disabled = False
        self.Q2widget.disabled = False

    def action_stop(self, widget):
        self.timer.stop()
        self.start.disabled = False
        self.stop.disabled = True
        self.disconnect.disabled = False
        self.Q1widget.disabled = True
        self.Q2widget.disabled = True

    def action_connect(self, widget):
        self.lab = TCLab()
        self.lab.connected = True

        self.connect.disabled = True
        self.start.disabled = False
        self.disconnect.disabled = False

    def action_disconnect(self, widget):
        self.lab.close()
        self.lab.connected = False

        self.connect.disabled = False
        self.disconnect.disabled = True
        self.start.disabled = True

    def action_Q1(self, change):
        self.lab.Q1(change['new'])

    def action_Q2(self, change):
        self.lab.Q2(change['new'])
