import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from multiprocessing import Process, Queue, TimeoutError
from multiprocessing.connection import Connection
from numpy import ndim, ndarray
from queue import Empty


def default_fig(**kwargs):
    """ Generate plt.figure instance

    :return: matplotlib tuple of (figure, axes) of the current plt environment """

    fig = plt.figure(**kwargs)
    ax = plt.gca()

    return fig, ax


def default_ax_plot(ax, data, channels: (list, tuple) = ()):
    """ Plots the data

    :param data: the data to be plotted, assumed to be in the format of (x, *y)
    :param channels: list or tuple of channel information for each data-row in y

    - If `channels` information have been specified in the object construction (i.e., a list of dicts),
      each data-channel (`y[i]`) is plotted (`plt.plot`) with keywords `**self.channel[i]`.
    """
    x, *y = data

    if ndim(y) == 1:
        y = [y]

    for i in range(len(y)):
        c = {} if channels in ((), {}, None) else channels[i]
        ax.plot(x, y[i], **c)


def default_legend(ax, channels=None):
    """ Plot legend for each axis in ax """

    if channels is not None and any('label' in c for c in channels):
        if not hasattr(ax, '__iter__'):
            ax.legend()
        else:
            [ax_i.legend() for ax_i in ax]


class DataMonitor(object):
    """ Data Monitoring of externally manipulated data

        For custom configuration consider passing
        (i) `make_fig` and
        (ii) `ax_plot`
        callables to the DataMonitor during construction to
        (i) generate a custom (fig, axes) matplotlib environment and to
        (ii) specify, how the data is plotted.

        The data-monitor runs matplotlib in an extra multiprocessing.Process.
        For a clean subprocess handling it is recommended to use DataMonitor in the with environment:

        > with DataMonitor(channels=..., ...) as dm:
        >     while True:
        >         dm.data = <update data from external source>
        >         <do something else>
    """

    def __init__(self,
                 data: (list, ndarray) = None,
                 channels: (None, list) = None,
                 clear_axes=True,
                 update_rate=1.,
                 make_fig: callable = default_fig,
                 make_fig_kwargs: (dict, tuple) = (),
                 ax_plot: callable = default_ax_plot,
                 ax_kwargs: (dict, tuple) = (),
                 legend :callable = default_legend,
                 style: (str, None)='fivethirtyeight'
                 ):
        """ Constructs a DataMonitor instance

        :param data: initial array-like data object to be plotted, a data format of (x, *y) is assumed.
                     For custom use consider overriding the DataMonitor plot method.
        :param channels: channel objects hosting meta data for the plot method
                         (None or list of dictionaries, defaults to None).
                         If the channels argument is a list of dicts, the dict corresponding to each data-channel will
                         be forwarded to ax.plot method as kwargs.
                         For custom use consider overriding the DataMonitor plot method.
        :param clear_axes: Boolean controlling whether plt.cla() clears the axes in each animation update.
        :param update_rate: update rate of matplotlib animation in milliseconds
        :param make_fig: callable which takes `make_fig_kwargs` as keyword and returns a matplotlib (figure, axes) tuple
        :param make_fig_kwargs: Dict-like kwargs to be forwarded to `make_fig`.
        :param ax_plot: callable which takes (axes, data, channels) as arguments
                        to plot the data with
                        channel meta-info
                        on the specified axes.
        :param ax_kwargs: Dict-like kwargs (or list of dict-like kwargs for multi-axes plot) to control axes formatting:
                           (i) each **key** in `ax_kwargs` must correspond to an **attribute** of the
                           `matplotlib.pyplot.axes` module (e.g. 'set_xlim' or 'set_ylabel'; for a single axis,
                           `matplotlib.pyplot` module attributes can be used such as 'xlim' or 'ylabel') and
                           (ii) the **values** must be tuples of the form (args, kwargs), specifying the
                           **arguments** and **keyword arguments** of the respective `matplotlib.pyplot` module
                           attribute (e.g. ((0, 1), {}) or (('values', ), {}).
        :param style: plot style, can be None.
        """

        # data handling
        self._data = data

        # channel handling
        self.channels = channels
        self.clear_axes = clear_axes

        # matplotlib handling
        self.fig = None
        self.ax = None
        self.make_fig_kwargs = dict(make_fig_kwargs)

        try:
            self.ax_kwargs = dict(ax_kwargs)
        except TypeError:
            self.ax_kwargs = ax_kwargs
        except ValueError:
            self.ax_kwargs = ax_kwargs

        self.make_fig = make_fig
        self.ax_plot = ax_plot
        self.legend = legend

        # animation handling
        self._func_animation = None
        self.update_rate = update_rate

        # multiprocess handling
        self._show_process = None
        self._data_queue = None

        if style is not None:
            plt.style.use(style)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self._show_process is not None:
            if exc_type is not None:
                try:
                    self._show_process.terminate()
                except:
                    pass

            self._show_process.join()
            self._show_process = None

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
        self._show_process = Process(name='animate', target=self.show, args=(self._data_queue, ))
        self._show_process.start()

    def stop(self):
        """ Stop a potentially running matplotlib FuncAnimation as subprocess """
        if self._show_process is not None:
            self.__exit__(None, None, None)

    def show(self, data_queue: Connection):
        """ Creates the matplotlib FuncAnimation and creates the plot (blocking) """
        self._data_queue = data_queue
        self.fig, self.ax = self.make_fig(**self.make_fig_kwargs)

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
            if self._data is not None:
                data = self._data
                self._data = None

            else:
                data = self._data_queue.get(timeout=self.update_rate)

        except (TimeoutError, Empty):
            data = None

        return data

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
            for ax_rows in (self.ax if hasattr(self.ax, '__iter__') else [self.ax]):
                for ax_cols in (ax_rows if hasattr(ax_rows, '__iter__') else [ax_rows]):
                    ax_cols.cla()

        self.ax_plot(ax=self.ax, data=data, channels=self.channels)
        self.apply_plt_kwargs()
        self.legend(ax=self.ax, channels=self.channels)

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

        axes = [self.ax] if not hasattr(self.ax, '__iter__') else self.ax
        plt_kwargs = [self.ax_kwargs]*len(axes) if isinstance(self.ax_kwargs, dict) else self.ax_kwargs

        for ax_row, row_kwargs in zip(axes, plt_kwargs):

            ax_row = [ax_row] if not hasattr(ax_row, '__iter__') else ax_row
            row_kwargs = [row_kwargs] * len(ax_row) if isinstance(row_kwargs, dict) else row_kwargs

            for ax, ax_kwargs in zip(ax_row, row_kwargs):
                for attribute, (args, kwargs) in ax_kwargs.items():
                    try:
                        getattr(ax, attribute)(*args, **kwargs)

                    except AttributeError:
                        getattr(plt, attribute)(*args, **kwargs)
