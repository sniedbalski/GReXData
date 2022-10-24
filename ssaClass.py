from siglent.spectrum_analyzers import SSA3000X, Bandwidth
import math
import time
import numpy as np
from pyvisa import ResourceManager
import matplotlib.pyplot as plt

class SSA:
    def __init__(self, span = None, freq_center = None, rbw = None, vbw = None, trace1 = None, trace2 = None, trace3 = None, trace4 = None):
        self.span = span
        self.freq_center = freq_center

        self.trace1 = trace1
        self.trace2 = trace2
        self.trace3 = trace3
        self.trace4 = trace4

        # Define rm and see list of devices
        self.rm = ResourceManager()

        # Define sa
        self.sa = SSA3000X('USB0::62700::4864::SSA3XMDD5R0893::0::INSTR', self.rm)

        # Reset sa
        self.sa.reset()

        if self.span: self.sa.span = self.span
        if self.freq_center: self.sa.freq_center = self.freq_center
        if rbw: self.sa.rbw = Bandwidth(rbw)
        if vbw: self.sa.vbw = Bandwidth(vbw)

        #self.sa.attenuation = 40
        #self.sa.preamp = True

        self.trace_nbr = []
        for i in range(4):
            if self.__dict__[f'trace{i+1}'] is not None:
                self.sa.Trace(n=i+1, parent = self.sa).mode = self.__dict__[f'trace{i+1}']
                self.trace_nbr.append(i+1)

    def pullTraces(self):
        traces_temp = []

        for m in self.trace_nbr:
            self.sa = SSA3000X('USB0::62700::4864::SSA3XMDD5R0893::0::INSTR', self.rm)
            traces_temp.append(self.sa.Trace(n=m, parent = self.sa).data)

        self.traces = np.array(traces_temp)

    def pullLabels(self):
        labels_temp = []

        for m in self.trace_nbr:
            self.sa = SSA3000X('USB0::62700::4864::SSA3XMDD5R0893::0::INSTR', self.rm)
            labels_temp.append(str(self.sa.Trace(n=m, parent = self.sa).mode).split(".")[1])

        self.labels = np.array(labels_temp)

    def pullOthers(self):
        # Get labels and tick marks
        OoM = math.floor(math.log(self.freq_center, 10))
        OoMDict = {1:"Hz", 3:"kHz", 6:"MHz", 9:"GHz"}
        self.xLabel = OoMDict[OoM]

        Ndata = 751
        Npoint = 700
        self.xAxis = np.linspace((self.freq_center - 0.5*self.span) / 10**OoM, (self.freq_center + 0.5*self.span) / 10**OoM, Ndata)

    def collect(self, duration, period = 10):
        data_temp = []
        duration *= 3600

        for i in range(int(duration / period)):
            self.pullTraces()
            data_temp.append(self.traces)
            time.sleep(period)

        self.data = np.array(data_temp)

    def save(self, name):
        self.filename = name
        self.pullOthers()
        self.pullLabels()
        save_data = np.array([self.xLabel, self.labels, self.xAxis, self.data], dtype = 'object')
        np.save(name, save_data, allow_pickle = True)