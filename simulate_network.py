import numpy as np
import pylab as plt

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def run_simulation(t_sim=1000, stim_strength=0., stim_start=100, stim_dur=100, population=0, seed=55):
    """
    Run a simulation to obtain data

    Parameters
    ----------
    t_sim           -- simulation time
    stim_strength   -- external stimulation strength [Hz]
    stim_start      -- external stimulation start [ms]
    stim_dur        -- external stimulation duration [ms]
    population      -- index of population for stimulation
    seed            -- random seed

    Returns
    -------
    data       -- average membrane voltage per population
    """

    print('Run spiking neural network...')
    from stimulus_params import stim_dict
    from network_params import net_dict
    from sim_params import sim_dict
    import network
    import numpy as np
    import os

    sim_dict['rng_seed'] = seed
    sim_dict['data_path'] = os.path.join(os.getcwd(), 'data/')

    if stim_strength != 0:
        stim_dict['thalamic_input'] = True
    stim_dict['conn_probs_th'] = np.zeros(8)
    stim_dict['conn_probs_th'][population] = 0.05
    stim_dict['th_rate'] = stim_strength
    stim_dict['th_start'] = sim_dict['t_presim'] + stim_start
    stim_dict['th_duration'] = stim_dur

    net = network.Network(sim_dict, net_dict, stim_dict)
    net.create()
    net.connect()
    net.simulate(sim_dict['t_presim'])
    net.simulate(t_sim)

    print('Collect data from file...')
    data = []
    plt.figure()
    for i in range(8):
        print('\tPopulation {}/8'.format(i+1))
        datContent = [i.strip().split() for i in open("data/voltmeter-{}-0.dat".format(7718+i)).readlines()]
        dat_ = np.array(datContent[3:]).astype(float)

        min_t = np.min(dat_[:,1])
        max_t = np.max(dat_[:,1])

        V_m = np.zeros(int(max_t-min_t)+1)   # if resolution (dt) = 1 ms
        times = np.arange(min_t, max_t+1)

        for i in range(np.shape(dat_)[0]):
            t_idx = int(dat_[i,1] - min_t)
            V_m[t_idx] += dat_[i, 2]
        N = len(np.unique(dat_[:,0]))
        V_m /= N

        # low-pass filter from 1.0 ms to 3.0 ms (LFP is the low-pass filtered signal cutoff at 300 Hz)
        V_m = running_mean(V_m, 3)

        data.append(V_m)

    return np.array(data)

def plot_LFP(data):
    plt.figure(figsize=(4, 4))
    for i in range(len(data)):
        mean = np.mean(data[i])
        plt.plot(running_mean(data[i], 3) - mean + 10 * i, color='black')
    plt.xlim(left=0, right=1000)
    plt.ylabel(r'$V_m$ [mV]')
    plt.xlabel(r'$Time$ [ms]')
    plt.yticks([])
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    data = run_simulation(t_sim=1000, stim_strength=10, stim_start=100, stim_dur=10, population=0)

    plot_LFP(data)