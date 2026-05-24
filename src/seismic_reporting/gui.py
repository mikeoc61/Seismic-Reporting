"""Tkinter GUI front end for the Seismic-Reporting tool.

Queries the USGS FDSN event service and displays earthquakes sorted by
magnitude, location, distance or time. Distances are measured from a
fixed home location (DEFAULT_ORIGIN); the command-line front end
(seismic_reporting.cli) exposes arbitrary coordinates and radial filtering.

FDSN event service: https://earthquake.usgs.gov/fdsnws/event/1/
"""

from __future__ import annotations

import datetime
import tkinter as tk
from timeit import default_timer as timer
from tkinter import ttk

from seismic_reporting.core import (
    DEFAULT_ORIGIN,
    build_fdsn_url,
    fetch_geojson,
    format_report,
    magnitude_summary,
    parse_quakes,
    sort_quakes,
)

__author__ = "Michael E. O'Connor"
__copyright__ = "Copyright 2026"

# Map each GUI period radio button to its display label and look-back days.
_PERIODS: dict[str, tuple[str, float]] = {
    'hour': ('Past Hour', 1.0 / 24.0),
    'day': ('Past Day', 1.0),
    'week': ('Past Week', 7.0),
    'month': ('Past Month', 30.0),
    'year': ('Past Year', 365.0),
}


class USGS_Gui:

    MASTER_WIDTH = 106     # Width of result text box, in characters
    MASTER_HEIGHT = 40     # Height of result text box, in characters
    SIDE_WIDTH = 100       # Width of the left control panel, in pixels
    WIDTH = 500            # Width of the result frame, in pixels
    HEIGHT = 300           # Height of the result frame, in pixels

    def __init__(self, master: tk.Tk) -> None:

        master.title('USGS Earthquake Data')
        frame0 = ttk.Panedwindow(master, orient=tk.HORIZONTAL)
        frame0.pack(fill=tk.BOTH, expand=True)

        # Two frames within the window: controls on the left, results right
        frame1 = ttk.Frame(frame0, width=self.SIDE_WIDTH, height=self.HEIGHT,
                            relief=tk.RAISED, padding=10)
        frame2 = ttk.Frame(frame0, width=self.WIDTH, height=self.HEIGHT,
                            relief=tk.SUNKEN)
        frame0.add(frame1, weight=1)
        frame0.add(frame2, weight=4)

        self.style = ttk.Style()
        if 'aqua' in self.style.theme_names():    # 'aqua' is macOS-only
            self.style.theme_use('aqua')
        self.style.configure('TButton', font='Arial 15', relief="flat")

        # Time period selector
        self.add_label(frame1, "Time Period")
        self.period = tk.StringVar()
        self.add_radiobutton(frame1, "Past Hour", self.period, "hour")
        self.add_radiobutton(frame1, "Past Day", self.period, "day")
        self.add_radiobutton(frame1, "Past Week", self.period, "week")
        self.add_radiobutton(frame1, "Past Month", self.period, "month")
        self.add_radiobutton(frame1, "Past Year", self.period, "year")
        self.period.set("day")

        # Minimum-magnitude selector (values are FDSN minmagnitude floats)
        self.add_label(frame1, "Magnitude")
        self.mag = tk.StringVar()
        self.add_radiobutton(frame1, "M6.0+", self.mag, '6.0')
        self.add_radiobutton(frame1, "M4.5+", self.mag, '4.5')
        self.add_radiobutton(frame1, "M2.5+", self.mag, '2.5')
        self.add_radiobutton(frame1, "M1.0+", self.mag, '1.0')
        self.add_radiobutton(frame1, "All", self.mag, '0.0')
        self.mag.set("1.0")

        # Sort field selector
        self.add_label(frame1, "Sort By")
        self.sortby = tk.IntVar()
        self.add_radiobutton(frame1, "Magnitude", self.sortby, 0)
        self.add_radiobutton(frame1, "Location", self.sortby, 1)
        self.add_radiobutton(frame1, "Distance", self.sortby, 2)
        self.add_radiobutton(frame1, "Time", self.sortby, 3)
        self.sortby.set(0)

        # Sort order selector
        self.add_label(frame1, "Sort Order")
        self.reverse = tk.BooleanVar()
        self.add_radiobutton(frame1, "Ascending", self.reverse, False)
        self.add_radiobutton(frame1, "Descending", self.reverse, True)
        self.reverse.set(False)

        self.add_line(frame1, 'white')

        result_button = tk.Button(frame1, text="Get Results",
                                  command=self.submit, bg='white', fg='blue',
                                  relief='sunken')
        result_button.pack(anchor='s', pady=3)

        # Result text box with vertical scrollbar
        self.result_box = tk.Text(frame2, width=self.MASTER_WIDTH,
                                  height=self.MASTER_HEIGHT)
        scrollbar = tk.Scrollbar(frame2, orient=tk.VERTICAL,
                                 command=self.result_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_box["yscrollcommand"] = scrollbar.set
        self.result_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

    # -- small widget-construction helpers ---------------------------------

    def add_label(self, frame: ttk.Frame, text: str) -> None:
        tk.Label(frame, text=text, bg="blue", fg="white", relief='ridge',
                 justify=tk.LEFT).pack(fill=tk.X, pady=5)

    def add_radiobutton(
        self,
        frame: ttk.Frame,
        text: str,
        variable: tk.Variable,
        value: object,
    ) -> None:
        ttk.Radiobutton(frame, text=text, variable=variable,
                        value=value).pack(anchor='w', pady=1)

    def add_line(self, frame: ttk.Frame, color: str) -> None:
        canvas = tk.Canvas(frame, width=self.SIDE_WIDTH, height=8)
        canvas.pack()
        canvas.create_line(0, 8, self.SIDE_WIDTH, 8, fill=color)

    # -- result handling ---------------------------------------------------

    def submit(self) -> None:
        """Fetch, process and display results for the current selections."""
        self.clear()

        period_label, days = _PERIODS[self.period.get()]
        starttime = (datetime.datetime.now(datetime.timezone.utc)
                     - datetime.timedelta(days=days)
                     ).strftime('%Y-%m-%dT%H:%M:%S')
        url = build_fdsn_url(float(self.mag.get()), starttime)

        try:
            data = fetch_geojson(url)
        except RuntimeError as err:
            self._show("Error retrieving data from:\n{}\n\n{}".format(url, err))
            return

        start = timer()
        quakes, meta = parse_quakes(data, DEFAULT_ORIGIN)
        stats = magnitude_summary(quakes)
        quakes = sort_quakes(quakes, self.sortby.get(), self.reverse.get())
        report = format_report(quakes, meta, period_label, DEFAULT_ORIGIN,
                               self.sortby.get(), stats, timer() - start,
                               self.MASTER_WIDTH)
        self._show(report)

    def clear(self) -> None:
        """Empty the result text box."""
        self.result_box.delete('1.0', tk.END)

    def _show(self, text: str) -> None:
        """Append text to the result text box."""
        self.result_box.insert(tk.END, text)


def main() -> None:
    """Launch the Tkinter GUI event loop."""
    root = tk.Tk()
    USGS_Gui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
