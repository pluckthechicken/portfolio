"""Stopwatch object for easy time/performance debugging."""

import time


class Stopwatch:
    """Keep track of time as code runs."""

    def __init__(self):
        """Start timer."""
        self.t0 = time.time()
        self.laps = [self.t0]

    def total(self, round_to=3):
        """Return total time in seconds."""
        t = time.time()
        td = t - self.t0
        return round(td, round_to)

    def lap(self, round_to=3):
        """Return previous lap time and start new lap."""
        t = time.time()
        td = t - self.laps[-1]
        self.laps.append(t)
        return round(td, round_to)
