import matplotlib.pyplot as plt


def make_figure(n_devices=1, n_channels=8, **kwargs):
    """ helper figure generation-function for custom DataMonitor below (one axis for each device)

    :param n_devices: number of devices whose data are plotted
    :param n_channels: number of devices whose data are plotted
    :param kwargs: keyword arguments passed to plt.subplots method
                   that generates the (fig, axes) matplotlib environment
    """
    f, axes = plt.subplots(n_channels, n_devices, **kwargs)
    return f, axes


def ax_plot(ax, data, channels):
    """ helper plot-function for custom DataMonitor below:
        all device-specific data is plotted in one device-specific axis

    :param ax: matplotlib axes array (here 1D) containing an axes per device
    :param data: list of data for each device, each device-data is a (n_samples x n_channels) array.
    :param channels: list of [channel-information] for each device,
                     each device specific channel-information is a list of [device-channel-info] dict.
                     Each channel specific device-channel-info dict contains
                     (i) key-value_dict pairs that are forwarded to the ax.plot function for each channel-data and
                     (ii) an element 'dt_slice', specifying the number of data that are shown, `data[-dt_slice:]`
    """
    for device_ax, device_data, device_channels in zip(ax.T, data, channels):
        for y, c, ax in zip(device_data, device_channels, device_ax):
            dt_slice = c.pop('dt_slice', len(y))
            ax.plot(y[-dt_slice::], **c)
            ax.set_ylabel(c.get('label', 'sensor'))
            c['dt_slice'] = dt_slice


def ax_legend(ax, channels):
    # [device_ax.legend(loc='center right') for device_ax in ax]
    pass
