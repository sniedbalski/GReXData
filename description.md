Description of data format for .npy files

data = np.load(file, allow_pickle = True)

data[0] gives the units of frequency
data[1] gives the names of the collected traces
data[2] gives the values on the frequency axis (NOTE: data[2] return 751 values, only take the first 700)
data[3] gives the collected intensity data for each trace

traces = data[3]

traces.shape --> (# samples, # traces, 700)
traces[:,i] gives ith trace in the format (# samples, 700)

For our data, we only use the 'WRITE' trace, so traces.shape --> (# samples, 1, 700)
