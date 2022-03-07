import os.path as op
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from mne.datasets import sample
from mne import read_evokeds
def app():
    # Data visualisation part
    st.title("Physician View")
    path = sample.data_path()
    fname = path + '/MEG/sample/sample_audvis-ave.fif'

    # load evoked corresponding to a specific condition
    # from the fif file and subtract baseline
    condition = 'Left Auditory'
    evoked = read_evokeds(fname, condition=condition, baseline=(None, 0))


    times = np.arange(0.05, 0.151, 0.02)

    all_times = np.arange(-0.2, 0.5, 0.03)

    extrapolations = ['local', 'head', 'box']
    fig, axes = plt.subplots(figsize=(7.5, 4.5), nrows=2, ncols=3)

    # Here we look at EEG channels, and use a custom head sphere to get all the
    # sensors to be well within the drawn head surface
    for axes_row, ch_type in zip(axes, ('mag', 'eeg')):
        for ax, extr in zip(axes_row, extrapolations):
            evoked.plot_topomap(0.1, ch_type=ch_type, size=2, extrapolate=extr,
                                axes=ax, show=False, colorbar=False,
                                sphere=(0., 0., 0., 0.09))
            ax.set_title('%s %s' % (ch_type.upper(), extr), fontsize=14)
    fig.tight_layout()
    st.pyplot(fig)
