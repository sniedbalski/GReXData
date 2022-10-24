"""Spectrum analyzers.

# SSA3000X
Supports:
- SSA3000X Plus

and

- SSA3000X-R
- SVA1000X

in Spectrum Analyzer mode.

"""

from enum import Enum
from typing import List

from .common import MessageResource

# Fixed for every SA in this series
NUM_DATA_POINTS = 700


class Bandwidth(Enum):
    """The discrete bandwidth values for Resolution and Video Bandwidth."""

    HZ_1 = 1
    HZ_3 = 3
    HZ_10 = 10
    HZ_30 = 30
    HZ_100 = 100
    HZ_300 = 300
    KHZ_1 = 1e3
    KHZ_3 = 3e3
    KHZ_10 = 10e3
    KHZ_30 = 30e3
    KHZ_100 = 100e3
    KHZ_300 = 300e3
    MHZ_1 = 1e6


class AverageType(Enum):
    """Trace averaging type."""

    LOG_POWER = "LOGPower"
    POWER = "POWer"
    VOLTAGE = "VOLTage"


class TraceMode(Enum):
    """Trace display mode.

    Values
    ------
    * WRITE - Continuously update
    * MAX_HOLD - Store the maximum value of each point
    * MIN_HOLD - Store the minimum value of each point
    * VIEW - Display the last recorded point, don't update
    * AVERAGE - Turn on trace averaging
    """

    WRITE = "WRITe"
    MAX_HOLD = "MAXHold"
    MIN_HOLD = "MINHold"
    VIEW = "VIEW"
    AVERAGE = "AVERage"


class DetectionMode(Enum):
    """Trace detection mode.

    Values
    ------
    * NEGATIVE - Negative peak detection displays the lowest sample taken during
    the interval being displayed.
    * POSITIVE - Positive peak detection displays the highest sample taken during
    the interval being displayed.
    * SAMPLE - Sample detection displays the sample taken during the interval being
    displayed, and is used primarily to display noise or noise-like signals.
    In sample mode, the instantaneous signal value at the present display point is
    placed into memory. This detection should not be used to make the most accurate
    amplitude measurement of non noise-like signals.
    * AVERAGE - Average detection is used when measuring the average value of the
    amplitude across each trace interval (bucket). The averaging method used by the
    average detector is set to either video or power as appropriate when the average
    type is auto coupled.
    * NORMAL - Normal detection selects the maximum and minimum video signal values
    alternately. When selecting Normal detection,”Norm”appears in the upper-left corner.
    * QUASI - Quasipeak detection is a form of detection where a signal level is
    weighted based on the repetition frequency of the spectral components making up the
    signal. That is to say, the result of a quasi-peak measurement depends on the
    repetition rate of the signal.
    """

    NEGATIVE = "NEGative"
    POSITIVE = "POSitive"
    SAMPLE = "SAMPle"
    AVERAGE = "AVERage"
    NORMAL = "NORMAL"
    QUASI = "QUASi"


class SSA3000X(MessageResource):
    """The class to control a SSA3000X-Series spectrum analyzer."""

    @property
    def ref_level(self) -> float:
        """Get the reference level in dBm."""
        return float(self._resource.query(":DISP:WIND:TRAC:Y:RLEV?"))

    # ----- Display -----

    @ref_level.setter
    def ref_level(self, level_dbm: float):
        """Set the reference level to the specified value in dBm."""
        assert -100 <= level_dbm <= 30, "Level must be between -100 and 30 dBm"
        self._resource.write(f":DISP:WIND:TRAC:Y:RLEV {level_dbm} DBM")

    # ----- Frequency -----

    @property
    def span(self) -> float:
        """Get the current span in Hz."""
        return float(self._resource.query(":FREQ:SPAN?"))

    @span.setter
    def span(self, freq_hz: float):
        """Set the span in Hz."""
        assert (100 <= freq_hz <= 3.2e9) or (
            freq_hz == 0
        ), "Span must be between 100 Hz and 3.2 GHz or 0"
        self._resource.write(f":FREQ:SPAN {freq_hz} Hz")

    @property
    def freq_center(self) -> float:
        """Get the center frequency in Hz."""
        return float(self._resource.query(":FREQ:CENT?"))

    @freq_center.setter
    def freq_center(self, freq_hz: float):
        """Set the center frequency in Hz."""
        assert 0 <= freq_hz <= 3.2e9, "Center frequency must be between 0 and 3.2 GHz"
        self._resource.write(f":FREQ:CENT {freq_hz} Hz")

    @property
    def freq_start(self) -> float:
        """Get the start frequency in Hz."""
        return float(self._resource.query(":FREQ:STAR?"))

    @property
    def freq_stop(self) -> float:
        """Get the stop frequency in Hz."""
        return float(self._resource.query(":FREQ:STOP?"))

    @freq_stop.setter
    def freq_stop(self, freq_hz: float):
        """Set the stop frequency in Hz."""
        assert 0 <= freq_hz <= 3.2e9, "Stop frequency must be between 0 and 3.2 GHz"
        self._resource.write(f":FREQ:STOP {freq_hz} Hz")

    @property
    def freq_step(self) -> float:
        """Get the current frequency step size (controlled by span)."""
        return float(self._resource.query(":FREQ:CENT:STEP?"))

    # ----- Power -----

    @property
    def attenuation(self) -> float:
        """Get the current attenuation level in dB."""
        return float(self._resource.query(":POW:ATT?"))

    @attenuation.setter
    def attenuation(self, db: float):
        """Set the attenuation level between 0 and 51 dB."""
        assert 0 <= db <= 51, "Attenuation must be between 0 and 51 dB"
        self._resource.write(f":POW:ATT {db}")

    @property
    def preamp(self) -> bool:
        """Get the status of the internal preamp. Returns true if active."""
        return self._resource.query("POW:GAIN?").strip() == "1"

    @preamp.setter
    def preamp(self, enabled: bool):
        """Set the internal preamp state to `enabled`."""
        self._resource.write(f":POW:GAIN {'ON' if enabled else 'OFF'}")

    # ----- Bandwidth -----

    @property
    def rbw(self) -> Bandwidth:
        """Get the resolution bandwidth."""
        return Bandwidth(float(self._resource.query(":BWID?")))

    @rbw.setter
    def rbw(self, bw: Bandwidth):
        """Set the resolution bandwidth."""
        self._resource.write(f":BWID {bw.value}")

    @property
    def vbw(self) -> Bandwidth:
        """Get the video bandwidth."""
        return Bandwidth(float(self._resource.query(":BWID:VID?")))

    @vbw.setter
    def vbw(self, bw: Bandwidth):
        """Set the video bandwidth."""
        self._resource.write(f":BWID:VID {bw.value}")

    @property
    def average_type(self) -> AverageType:
        """Get the average type."""
        return AverageType(self._resource.query(":AVER:TYPE?").strip())

    @average_type.setter
    def average_type(self, type: AverageType):
        """Set the average type."""
        self._resource.write(f":AVER:TYPE {type.value}")

    # ----- Trace -----

    @property
    def sweep_time(self) -> float:
        """Get the current sweep time in seconds."""
        return float(self._resource.query(":SWE:TIME?"))

    @sweep_time.setter
    def sweep_time(self, time: float):
        """Set the sweep time to a value from 450us to 1.5ks."""
        assert 450e-6 <= time <= 1.5e3, "Time must be between 450us and 1.5ks"
        self._resource.write(f":SWE:TIME {time}s")

    def sweep_restart(self):
        """Retsart the current sweep."""
        self._resource.write(":INIT:REST")

    def trace(self, trace: int) -> "Trace":
        """Get the trace object from the SA."""
        assert 1 <= trace <= 4, "Trace is either 1,2,3, or 4"
        return self.Trace(self, trace)

    class Trace:
        """The trace object for one of the four available traces."""

        def __init__(self, parent: "SSA3000X", n: int):
            self._n = n
            self._parent = parent
            self._resource = parent._resource
            # Set the trace output to binary data (64-bit real values)
            self._resource.write(":FORM REAL")

        @property
        def mode(self) -> TraceMode:
            """Get the current trace mode."""
            return TraceMode(self._resource.query(f":TRAC{self._n}:MODE?").strip())

        @mode.setter
        def mode(self, mode: str):
            """Set the trace mode."""
            self._resource.write(f":TRAC{self._n}:MODE {mode}")

        @property
        def averages(self) -> int:
            """Get the number of averages."""
            return int(self._resource.query(f":AVER:TRAC{self._n}:COUN?"))

        @averages.setter
        def averages(self, n: int):
            """Set the number of averages (Between 1 and 999)."""
            assert 1 <= n <= 999, "n must be between 1 and 999"
            self._resource.write(f":AVER:TRAC{self._n}:COUN {n}")

        @property
        def current_averages(self) -> int:
            """Get the current number of averages."""
            return int(self._resource.query(f":AVER:TRAC{self._n}?"))

        def average_restart(self):
            """Restart trace averaging."""
            self._resource.write(f":AVER:TRAC{self._n}:CLE")

        @property
        def detection_mode(self) -> DetectionMode:
            """Get the current trace detection mode."""
            return DetectionMode(self._resource.query(f":DET:TRAC{self._n}?").strip())

        @detection_mode.setter
        def detection_mode(self, mode: DetectionMode):
            """Set the trace detection mode."""
            self.resource.write(f":DET:TRAC{self._n} {mode.value}")

        @property
        def data(self) -> List[float]:
            """
            Get a list of the data point of the *currently displayed* trace.

            The units of this data is dependent of the current configuration.
            This will force a retrigger of the measurement and wait the sweep time
            before returning a result.
            """
            #self._parent.sweep_restart()
            #self._parent.block_until_complete()
            # Siglent seems to be sending little endian, this is mysteriously
            # undocumented. Additionally, there is no header and we know
            # the number of points as this is fixed
            return self._resource.query_binary_values(
                f"TRAC:DATA? {self._n}",
                datatype="f",
                header_fmt="empty",
                data_points=NUM_DATA_POINTS,
            )
