import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Queue, TimeoutError
from multiprocessing.connection import Connection
import numpy as np
from queue import Empty


plt.style.use('fivethirtyeight')


class DataMonitor(object):
    """ Data Monitoring of externally manipulated data

        For custom configuration consider overwriting the DataMonitor plot method.

        The data-monitor runs matplotlib in an extra multiprocessing.Process.
        For a clean subprocess handling it is recommended to use DataMonitor in the with environment:

        > with DataMonitor(channels=..., ...) as dm:
        >     while True:
        >         dm.data = <update data from external source>
        >         <do something else>
    """

    def __init__(self, data: list = None, channels: (None, list) = None, update_rate: (int, float) = 1, fig_ax: tuple = (), plt_kwargs={}, clear_axes=True, x_offset=True, **fig_kwargs):
        """
        :param data: initial array-like data object to be plotted, a data format of (x, *y) is assumed.
                     For custom use consider overwriting the DataMonitor plot method.
        :param channels: channel objects hosting meta data for the plot method (None or list of dictionaries, defaults to None).
                         If the channels argument is a list of dicts, the dict corresponding to each data-channel will
                         be forwarded to ax.plot method as kwargs.
                         For custom use consider overwriting the DataMonitor plot method.
        :param update_rate: update rate of matplotlib animation in milliseconds
        :param fig_ax: A tuple specifying whether an existing figure or axes objects are used or if a new one should be generated (per default `if fig_ax is ()`).
        :param plt_kwargs: Dictionary to control plot formatting:
                           (i) each **key** in `plt_kwargs` must correspond to an **attribute** of the
                           `matplotlib.pyplot` module (e.g. 'xlim' or 'ylabel') and
                           (ii) the **values** must be tuples of the form (args, kwargs), specifying the
                           **arguments** and **keyword arguments** of the respective `matplotlib.pyplot` module
                           attribute (e.g. ((0, 1), {}) or (('values', ), {}).
        :param clear_axes: Boolean controlling whether plt.cla() clears the axes in each animation update.
        :param fig_kwargs: kwargs to be forwarded to `plt.figure` if `fig_ax` is not provided.
        """

        # data handling
        self._data = data

        # channel handling
        self.channels = channels
        self.clear_axes = clear_axes
        self._x_offset = x_offset

        if fig_ax in ((), None):
            self.fig = plt.figure(**fig_kwargs)
            self.ax = plt.gca()
        else:
            self.fig, self.ax = fig_ax

        self.fig_kwargs = fig_kwargs
        self.plt_kwargs = plt_kwargs

        # animation handling
        self._func_animation = None
        self.update_rate = update_rate

        # multiprocess handling
        self._show_process = None
        self._data_queue = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self._show_process is not None:
            if exc_type is not None:
                self._show_process.terminate()

            try:
                self._show_process.join()
                self._show_process = None
            except AssertionError:
                pass

        if self._data_queue is not None:
            while not self._data_queue.empty():
                try:
                    self._data_queue.get(timeout=0.001)
                except (TimeoutError, Empty):
                    pass

            self._data_queue.close()
            self._data_queue = None

    def start(self):
        """ Starts the matplotlib FuncAnimation as subprocess (non-blocking, queue communication) """
        self._data_queue = Queue()
        self._show_process = Process(name='animate',
                                     target=self.show,
                                     args=(self._data_queue, ))
        self._show_process.start()

    def show(self, data_queue):
        """ Creates the matplotlib FuncAnimation and creates the plot (blocking)"""
        self._data_queue = data_queue

        self._func_animation = FuncAnimation(
            self.fig,                   # figure to animate
            self.animate,               # function to run the animation
            interval=self.update_rate,  # interval to run the function in millisecond
        )

        self.apply_plt_kwargs()
        plt.tight_layout()
        plt.show()

    @property
    def data(self):
        """ Data property (getter) which tries to read from a
            multiprocessing queue and returns the current data array
            on default.
        """
        try:
            self._data = self._data_queue.get(timeout=self.update_rate)
        except (TimeoutError, Empty):
            pass

        return self._data

    @data.setter
    def data(self, value):
        """ Puts data to the multiprocessing data queue
            which is then received by the function animation.
        """
        self._data_queue.put(value)

    def animate(self, i):
        """ The update method of the matplotlib function animation """
        data = self.data

        if data is None:
            return

        if self.clear_axes:
            plt.cla()  # clear axes

        self.plot(data)
        self.apply_plt_kwargs()

    def plot(self, data):
        """ Plots the data

        :param data: the data to be plotted, assumed to be in the format of (x, *y)

        - If `channels` information have been specified in the object construction (i.e., a list of dicts),
          each data-channel (`y[i]`) is plotted (`plt.plot`) with keywords `**self.channel[i]`.
        """
        x, *y = data

        if np.ndim(y) == 1:
            y = [y]

        if self._x_offset:
            x = np.asarray(x) - x[0]

        for i in range(len(y)):
            c = {} if self.channels is None else self.channels[i]
            plt.plot(x, y[i], **c)

    def apply_plt_kwargs(self):
        """ apply plt_kwargs instructions and shows the legend if labels have been defined in
        the channels information during construction

        Dictionary to control plot formatting:
       (i) each **key** in `plt_kwargs` must correspond to an **attribute** of the
       `matplotlib.pyplot` module (e.g. 'xlim' or 'ylabel') and
       (ii) the **values** must be tuples of the form (args, kwargs), specifying the
       **arguments** and **keyword arguments** of the respective `matplotlib.pyplot` module
       attribute (e.g. ((0, 1), {}) or (('values', ), {}).
        """
        for attribute, (args, kwargs) in self.plt_kwargs.items():
            getattr(plt, attribute)(*args, **kwargs)

        if self.channels is not None and any('label' in c for c in self.channels):
            plt.legend()


if __name__ == '__main__':
    from itertools import count
    import random
    import time

    index = count()
    data = [[], [], []]

    def get_data_from_elsewhere():
        data[0].append(next(index))
        data[1].append(np.cos(data[0][-1] * np.pi * 1.5 / 50) + 1 + random.random()*0.25 - 0.125)
        data[2].append(np.sin(data[0][-1] * np.pi * 1.5 / 50) - 1 + random.random()*0.25 - 0.125)
        return data

    channels = [
        {'label': 'Channel 1'},
        {'label': 'Channel 2', 'color': 'tab:orange'},
    ]

    plt_kwargs = dict(
        xlim=((0, 50), {}),
        ylim=((-2.5, 2.5), {}),
        xlabel=(('steps', ), {}),
        ylabel=(('values',), {}),
    )

    with DataMonitor(data=data, channels=channels, plt_kwargs=plt_kwargs, update_rate=1) as dm:
        for i in range(50):
            dm.data = get_data_from_elsewhere()
            time.sleep(0.05)

    print('done')
