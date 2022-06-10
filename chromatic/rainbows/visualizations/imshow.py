from ...imports import *

__all__ = ["imshow"]


def imshow(
    self,
    ax=None,
    quantity="flux",
    w_unit="micron",
    t_unit="day",
    colorbar=True,
    aspect="auto",
    **kw,
):
    """
    imshow flux as a function of time (x = time, y = wavelength, color = flux).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes into which to make this plot.
    quantity : str
        The fluxlike quantity to imshow.
        (Must be a key of `rainbow.fluxlike`).
    w_unit : str, astropy.unit.Unit
        The unit for plotting wavelengths.
    t_unit : str, astropy.unit.Unit
        The unit for plotting times.
    colorbar : bool
        Should we include a colorbar?
    aspect : str
        What aspect ratio should be used for the imshow?
    kw : dict
        All other keywords will be passed on to `plt.imshow`,
        so you can have more detailed control over the plot
        appearance. Common keyword arguments might include:
        `[cmap, norm, interpolation, alpha, vmin, vmax]` (and more)
        More details are available at
        https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.imshow.html
    """

    # self.speak(f'imshowing')
    if ax is None:
        ax = plt.subplot()

    w_unit, t_unit = u.Unit(w_unit), u.Unit(t_unit)

    # make sure some wavelength and time edges are defined
    self._make_sure_wavelength_edges_are_defined()
    self._make_sure_time_edges_are_defined()

    # set up the wavelength extent
    try:
        wmin = self.wavelength_lower[0].to_value(w_unit)
        wmax = self.wavelength_upper[-1].to_value(w_unit)
    except AttributeError:
        wmin, wmax = None, None
    if (self.wscale == "linear") and (wmin is not None) and (wmax is not None):
        bottom, top = wmax, wmin
        ylabel = f"{self._wave_label} ({w_unit.to_string('latex_inline')})"
    elif self.wscale == "log" and (wmin is not None) and (wmax is not None):
        bottom, top = np.log10(wmax), np.log10(wmin)
        ylabel = (
            r"log$_{10}$" + f"[{self._wave_label}/({w_unit.to_string('latex_inline')})]"
        )
    else:
        message = f"""
        The wavelength scale for this rainbow is '{self.wscale}',
        and there are {self.nwave} wavelength centers and
        {len(self.wavelike.get('wavelength_lower', []))} wavelength edges defined.

        It's hard to imshow something with a wavelength axis
        that isn't linearly or logarithmically uniform, or doesn't
        at least have its wavelength edges defined. We're giving up
        and just using the wavelength index as the wavelength axis.

        If you want a real wavelength axis, one solution would
        be to bin your wavelengths to a more uniform grid with
        `rainbow.bin(R=...)` (for logarithmic wavelengths) or
        `rainbow.bin(dw=...)` (for linear wavelengths)
        """
        warnings.warn(message)
        bottom, top = self.nwave - 0.5, -0.5
        ylabel = "Wavelength Index"

    # set up the time extent
    try:
        tmin = self.time_lower[0].to_value(t_unit)
        tmax = self.time_upper[-1].to_value(t_unit)
    except AttributeError:
        tmin, tmax = None, None
    if (self.tscale == "linear") and (tmin is not None) and (tmax is not None):
        right, left = tmax, tmin
        xlabel = f"{self._time_label} ({t_unit.to_string('latex_inline')})"
    elif self.tscale == "log" and (tmin is not None) and (tmax is not None):
        right, left = np.log10(tmax), np.log10(tmin)
        xlabel = (
            r"log$_{10}$" + f"[{self._time_label}/({t_unit.to_string('latex_inline')})]"
        )
    else:
        message = f"""
        The time scale for this rainbow is '{self.tscale}',
        and there are {self.ntime} time centers and
        {len(self.timelike.get('time_lower', []))} time edges defined.

        It's hard to imshow something with a time axis
        that isn't linearly or logarithmically uniform, or doesn't
        at least have its time edges defined. We're giving up
        and just using the time index as the time axis.

        If you want a real time axis, one solution would
        be to bin your times to a more uniform grid with
        `rainbow.bin(dt=...)` (for linear times).
        """
        warnings.warn(message)
        right, left = self.ntime - 0.5, -0.5
        xlabel = "Time Index"

    self._imshow_extent = [left, right, bottom, top]

    # define some default keywords
    imshow_kw = dict(interpolation="nearest")
    imshow_kw.update(**kw)
    with quantity_support():
        plt.sca(ax)
        z = self.get(quantity)
        plt.imshow(
            z,
            extent=self._imshow_extent,
            aspect=aspect,
            origin="upper",
            **imshow_kw,
        )
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        if colorbar:
            plt.colorbar(
                ax=ax,
                label=u.Quantity(z).unit.to_string("latex_inline"),
            )
    return ax
