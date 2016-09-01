

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.ticker import MaxNLocator

try:
    data_table

except NameError:
    from rave_io import (get_cannon_dr1, get_ges_idr4)

    from astropy.table import join
    dr1 = get_cannon_dr1()
    #dr1["TEFF"] = dr1["EPIC_TEFF"]
    #dr1["LOGG"] = dr1["EPIC_LOGG"]
    #dr1["FE_H"] = dr1["EPIC_FEH"]

    data_table = join(dr1, get_ges_idr4(), keys=("Name", ))

else:
    print("Warning: Using pre-loaded data!")


# Plot labels against literature.

label_names = ("TEFF_1", "LOGG_1", "FE_H")
ges_label_names = {
    "TEFF_1": "TEFF_2",
    "LOGG_1": "LOGG_2",
    "FE_H": "FEH",
}

label_limits = {
    "TEFF_1": (3500, 7000),
    "LOGG_1": (0, 5),
    "FE_H": (-2, 0.75)
}

latex_labels = {
    "TEFF_1": r"$T_{\rm eff}$",
    "LOGG_1": r"$\log{g}$",
    "FE_H": r"$[{\rm Fe/H}]$"
}


# Exclude ones we think are bad.
#ok = data_table["OK"] 
ok = (data_table["r_chi_sq"] < 3) * (data_table["snr"] > 15)

#ok *= np.isfinite(data_table["TEFF_1"] * data_table["TEFF_2"] * data_table["LOGG_1"] * data_table["LOGG_2"] * data_table["FE_H"] * data_table["FEH"])

data_table = data_table[ok]

K = len(label_names)
factor = 3.5
lbdim = 0.2 * factor
trdim = 0.1 * factor
whspace = 0.05
yspace = factor
xspace = factor * K + factor * (K - 1) * whspace + lbdim * (K - 1)
xdim = lbdim + xspace + trdim
ydim = lbdim + yspace + trdim

fig, axes = plt.subplots(1, K, figsize=(xdim, ydim))
fig.subplots_adjust(
    left=lbdim/xdim, bottom=lbdim/ydim, right=(xspace + lbdim)/xdim,
    top=(yspace + lbdim)/ydim, wspace=whspace, hspace=whspace)


for i, (ax, label_name) in enumerate(zip(axes, label_names)):

    y = data_table[label_name]
    #xerr
    x = data_table[ges_label_names[label_name]]
    # yerr
    c = data_table["snr"]


    scat = ax.scatter(x, y, c=data_table["snr"], s=75, cmap="plasma") 

    limits = label_limits[label_name]
    ax.plot(limits, limits, c="#666666", linestyle=":", zorder=-1)

    Nstars = np.isfinite(x*y).sum()
    ax.text(0.05, 0.90, r"${:.0f}$".format(Nstars) + r" ${\rm stars}$",
        transform=ax.transAxes)

    if label_name.startswith("TEFF"):
        ax.text(0.05, 0.82, r"${\rm Bias:}$ " + r"${:.0f}$".format(np.nanmean(y-x)) + r" ${\rm K}$",
            transform=ax.transAxes)
        ax.text(0.05, 0.74, r"${\rm RMS:}$ " + r"${0:.0f}$".format(np.nanstd(y-x)) + r" ${\rm K}$",
            transform=ax.transAxes)
    else:
        ax.text(0.05, 0.82, r"${\rm Bias:}$ " + r"${0:.2f}$".format(np.nanmean(y-x)) + r" ${\rm dex}$",
            transform=ax.transAxes)
        ax.text(0.05, 0.74, r"${\rm RMS:}$ " + r"${0:.2f}$".format(np.nanstd(y-x)) + r" ${\rm dex}$",
            transform=ax.transAxes)

    ax.set_xlim(limits)
    ax.set_ylim(limits)
    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))
    ax.set_ylabel(" ".join([latex_labels[label_name], r"$({\rm unRAVE})$"]))
    ax.set_xlabel(" ".join([latex_labels[label_name], r"$({\rm GES})$"]))

    [_.set_rotation(30) for _ in ax.get_xticklabels()]
    [_.set_rotation(30) for _ in ax.get_yticklabels()]

    diff = y - x
    print(label_name, np.nanmean(diff), np.nanstd(diff))

#cbar = plt.colorbar(scat)
#cbar.set_label(r"$S/N$")

fig.tight_layout()


cbar = plt.colorbar(scat, cax=fig.add_axes([0.93,fig.subplotpars.bottom,0.02,0.9 - fig.subplotpars.bottom]))
cbar.set_label(r"${\rm RAVE}$ $S/N$ $[{\rm pixel}^{-1}]$")

fig.subplots_adjust(top=0.90, right=0.91)

fig.savefig("ges-comparison.pdf", dpi=300)
fig.savefig("ges-comparison.png")
