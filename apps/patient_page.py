import os.path as op
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.datasets import somato
from mne.baseline import rescale
from mne.stats import bootstrap_confidence_interval
def app():
    # Data visualisation part

    st.title("Patient View")
    data_path = somato.data_path()
    subject = '01'
    task = 'somato'
    raw_fname = op.join(data_path, 'sub-{}'.format(subject), 'meg',
                        'sub-{}_task-{}_meg.fif'.format(subject, task))

    # let's explore some frequency bands
    iter_freqs = [
        ('Theta', 4, 7),
        ('Alpha', 8, 12),
        ('Beta', 13, 25),
        ('Gamma', 30, 45)
    ]
    # set epoching parameters
    event_id, tmin, tmax = 1, -1., 3.
    baseline = None

    # get the header to extract events
    raw = mne.io.read_raw_fif(raw_fname)
    events = mne.find_events(raw, stim_channel='STI 014')

    frequency_map = list()

    for band, fmin, fmax in iter_freqs:
        # (re)load the data to save memory
        raw = mne.io.read_raw_fif(raw_fname)
        raw.pick_types(meg='grad', eog=True)  # we just look at gradiometers
        raw.load_data()

        # bandpass filter
        raw.filter(fmin, fmax, n_jobs=1,  # use more jobs to speed up.
                   l_trans_bandwidth=1,  # make sure filter params are the same
                   h_trans_bandwidth=1)  # in each band and skip "auto" option.

        # epoch
        epochs = mne.Epochs(raw, events, event_id, tmin, tmax, baseline=baseline,
                            reject=dict(grad=4000e-13, eog=350e-6),
                            preload=True)
        # remove evoked response
        epochs.subtract_evoked()

        # get analytic signal (envelope)
        epochs.apply_hilbert(envelope=True)
        frequency_map.append(((band, fmin, fmax), epochs.average()))
        del epochs
    del raw
    # Helper function for plotting spread
    def stat_fun(x):
        """Return sum of squares."""
        return np.sum(x ** 2, axis=0)


    # Plot
    fig, axes = plt.subplots(4, 1, figsize=(10, 7), sharex=True, sharey=True)
    colors = plt.get_cmap('winter_r')(np.linspace(0, 1, 4))
    for ((freq_name, fmin, fmax), average), color, ax in zip(
            frequency_map, colors, axes.ravel()[::-1]):
        times = average.times * 1e3
        gfp = np.sum(average.data ** 2, axis=0)
        gfp = mne.baseline.rescale(gfp, times, baseline=(None, 0))
        ax.plot(times, gfp, label=freq_name, color=color, linewidth=2.5)
        ax.axhline(0, linestyle='--', color='grey', linewidth=2)
        ci_low, ci_up = bootstrap_confidence_interval(average.data, random_state=0,
                                                      stat_fun=stat_fun)
        ci_low = rescale(ci_low, average.times, baseline=(None, 0))
        ci_up = rescale(ci_up, average.times, baseline=(None, 0))
        ax.fill_between(times, gfp + ci_up, gfp - ci_low, color=color, alpha=0.3)
        ax.grid(True)
        ax.set_ylabel('GFP')
        ax.annotate('%s (%d-%dHz)' % (freq_name, fmin, fmax),
                    xy=(0.95, 0.8),
                    horizontalalignment='right',
                    xycoords='axes fraction')
        ax.set_xlim(-1000, 3000)

    axes.ravel()[-1].set_xlabel('Time [ms]')
    st.pyplot(fig)
