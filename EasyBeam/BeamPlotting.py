import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.collections as mplcollect
import pyvista

# import matplotlib.colors as colors
import numpy as np


def _plotting(self, val, disp, title, colormap):
    fig, ax = plt.subplots()
    ax.axis("off")
    ax.set_aspect("equal")

    c = np.linspace(val.min(), val.max(), 5)
    norm = MidpointNormalizeNew(vmin=-np.abs(val).max(), vmax=np.abs(val).max())
    lcAll = colorline(
        disp[:, 0, :], disp[:, 1, :], val, cmap=colormap, plot=False, norm=norm
    )

    for i in range(self.nEl):
        xEl = self.Nodes[self.El[i, 0] - 1, 0], self.Nodes[self.El[i, 1] - 1, 0]
        yEl = self.Nodes[self.El[i, 0] - 1, 1], self.Nodes[self.El[i, 1] - 1, 1]
        plt.plot(xEl, yEl, c="gray", lw=0.5, ls=self.lineStyleUndeformed, clip_on=False)
    for i in range(self.nEl):
        lc = colorline(
            disp[i, 0, :], disp[i, 1, :], val[i, :], cmap=colormap, norm=lcAll.norm
        )

    cb = plt.colorbar(
        lcAll,
        ticks=c,
        shrink=0.5,
        ax=[ax],
        location="left",
        aspect=10,
        boundaries=np.linspace(val.min(), val.max(), 100),
    )
    cb.outline.set_visible(False)
    cb.set_label(title, labelpad=0, y=1.1, rotation=0, ha="left")
    # cb = plt.colorbar(lcAll, ticks=c, shrink=0.4, orientation="horizontal")
    xmin = disp[:, 0, :].min() - 1
    xmax = disp[:, 0, :].max() + 1
    ymin = disp[:, 1, :].min() - 1
    ymax = disp[:, 1, :].max() + 1
    xdelta = xmax - xmin
    ydelta = ymax - ymin
    buff = 0.1
    plt.xlim(xmin - xdelta * buff, xmax + xdelta * buff)
    plt.ylim(ymin - ydelta * buff, ymax + ydelta * buff)
    # cb.ax.set_title(title)
    plt.show()


def PlotStress(self, stress="all", scale=1):
    if not self.ComputedStress:
        self.ComputeStress()
    self.rS = self.r0S + self.uS * scale
    if stress.lower() in ["all", "upper"]:
        self._plotting(
            np.sum(self.sigmaU, 2),
            self.rS,
            "upper fiber stress\n$\\sigma_U$ [MPa]",
            self.colormap,
        )

    if stress.lower() in ["all", "lower"]:
        self._plotting(
            np.sum(self.sigmaL, 2),
            self.rS,
            "lower fiber stress\n$\\sigma_L$ [MPa]",
            self.colormap,
        )

    if stress.lower() in ["all", "max"]:
        self._plotting(
            self.sigmaMax,
            self.rS,
            "maximum stress\n$|\\sigma_{max}|$ [MPa]",
            self.colormap,
        )

    if stress.lower() in ["all", "bending"]:
        self._plotting(
            self.sigmaU[:, :, 1],
            self.rS,
            "bending stress\n(upper fiber)\n$\\sigma_{bending}$ [MPa]",
            self.colormap,
        )

    if stress.lower() in ["all", "axial"]:
        self._plotting(
            self.sigmaU[:, :, 0],
            self.rS,
            "axial stress\n$\\sigma_{axial}$ [MPa]",
            self.colormap,
        )


def PlotDisplacement(self, component="all", scale=1):
    if not self.ComputedDisplacement:
        self.ComputeDisplacement()
    self.rS = self.r0S + self.uS * scale
    if component.lower() in ["mag", "all"]:
        self.dS = np.sqrt(self.uS[:, 0, :] ** 2 + self.uS[:, 1, :] ** 2)
        self._plotting(
            self.dS, self.rS, "deformation\nmagnitude\n$|u|$ [mm]", self.colormap
        )
    if component.lower() in ["x", "all"]:
        self._plotting(
            self.uS[:, 0, :], self.rS, "$x$-deformation\n$u_x$ [mm]", self.colormap
        )
    if component.lower() in ["y", "all"]:
        self._plotting(
            self.uS[:, 1, :], self.rS, "$y$-deformation\n$u_y$ [mm]", self.colormap
        )


def PlotMode(self, scale=1):
    Phii = np.zeros([3 * self.nN])
    for ii in range(len(self.omega)):
        Phii[self.DoF] = self.Phi[:, ii]
        uE_Phi = np.zeros([self.nEl, 6])
        uS_Phi = np.zeros([self.nEl, 2, self.nSeg + 1])
        for i in range(self.nEl):
            uE_Phi[i, :] = self.L[i] @ Phii
            for j in range(self.nSeg + 1):
                ?? = j / (self.nSeg)
                S = self.ShapeMat(??, self.ell[i])
                uS_Phi[i, :, j] = self.TX[i] @ S @ self.T[i] @ uE_Phi[i, :]
        # deformation
        rPhi = self.r0S + uS_Phi * scale
        dPhi = np.sqrt(uS_Phi[:, 0, :] ** 2 + uS_Phi[:, 1, :] ** 2)
        self._plotting(
            dPhi,
            rPhi,
            ("mode " + str(ii + 1) + "\n" + str(round(self.f0[ii], 4)) + " Hz"),
            self.colormap,
        )


def PlotMesh(self, NodeNumber=True, ElementNumber=True, Loads=True, BC=True, FontMag=1):
    if not self.Initialized:
        self.Initialize()
    fig, ax = plt.subplots()
    ax.axis("off")
    ax.set_aspect("equal")
    deltaMax = max(
        self.Nodes[:, 0].max() - self.Nodes[:, 0].min(),
        self.Nodes[:, 1].max() - self.Nodes[:, 1].min(),
    )
    p = deltaMax * 0.0075
    for i in range(self.nEl):
        xEl = self.Nodes[self.El[i, 0] - 1, 0], self.Nodes[self.El[i, 1] - 1, 0]
        yEl = self.Nodes[self.El[i, 0] - 1, 1], self.Nodes[self.El[i, 1] - 1, 1]
        plt.plot(xEl, yEl, c="gray", lw=self.A[i] / np.max(self.A), ls="-")
    plt.plot(self.Nodes[:, 0], self.Nodes[:, 1], ".k", clip_on=False)
    if NodeNumber:
        for i in range(self.nN):
            ax.annotate(
                "N" + str(i + 1),
                (self.Nodes[i, 0] + p, self.Nodes[i, 1] + p),
                fontsize=5 * FontMag,
                clip_on=False,
            )
    if ElementNumber:
        for i in range(self.nEl):
            posx = (
                self.Nodes[self.El[i, 0] - 1, 0] + self.Nodes[self.El[i, 1] - 1, 0]
            ) / 2
            posy = (
                self.Nodes[self.El[i, 0] - 1, 1] + self.Nodes[self.El[i, 1] - 1, 1]
            ) / 2
            ax.annotate(
                "E" + str(i + 1),
                (posx + p, posy + p),
                fontsize=5 * FontMag,
                c="gray",
                clip_on=False,
            )
    if Loads:
        note = [r"$F_x$", r"$F_y$", r"$M$"]
        for i in range(len(self.Load)):
            comment = ""
            for ii in range(3):
                if isinstance(self.Load[i][1][ii], int) or isinstance(
                    self.Load[i][1][ii], float
                ):
                    if self.Load[i][1][ii] != 0:
                        comment += note[ii]
            ax.annotate(
                comment,
                (
                    self.Nodes[self.Load[i][0] - 1, 0] + p,
                    self.Nodes[self.Load[i][0] - 1, 1] - p,
                ),
                fontsize=5 * FontMag,
                c="red",
                clip_on=False,
                ha="left",
                va="top",
            )
    if BC:
        noteBC = [r"$x_f$", r"$y_f$", r"$\theta_f$"]
        noteDL = [r"$x_d$", r"$y_d$", r"$\theta_d$"]
        for i in range(len(self.Disp)):
            commentBC = ""
            commentDL = ""
            for ii in range(3):
                if isinstance(self.Disp[i][1][ii], int) or isinstance(
                    self.Disp[i][1][ii], float
                ):
                    if self.Disp[i][1][ii] == 0:
                        commentBC += noteBC[ii]
                    else:
                        commentDL += noteDL[ii]
            ax.annotate(
                commentBC,
                (
                    self.Nodes[self.Disp[i][0] - 1, 0] - p,
                    self.Nodes[self.Disp[i][0] - 1, 1] - p,
                ),
                fontsize=5 * FontMag,
                c="green",
                clip_on=False,
                ha="right",
                va="top",
            )
            ax.annotate(
                commentDL,
                (
                    self.Nodes[self.Disp[i][0] - 1, 0] - p,
                    self.Nodes[self.Disp[i][0] - 1, 1] + p,
                ),
                fontsize=5 * FontMag,
                c="blue",
                clip_on=False,
                ha="right",
                va="bottom",
            )
    xmin = self.Nodes[:, 0].min()
    xmax = self.Nodes[:, 0].max()
    if self.Nodes[:, 1].max() - self.Nodes[:, 1].min() < 0.1:
        ymin = -10
        ymax = 10
    else:
        ymin = self.Nodes[:, 1].min()
        ymax = self.Nodes[:, 1].max()
    xdelta = xmax - xmin
    ydelta = ymax - ymin
    buff = 0.1
    plt.xlim(xmin - xdelta * buff, xmax + xdelta * buff)
    plt.ylim(ymin - ydelta * buff, ymax + ydelta * buff)
    plt.show()


class MidpointNormalizeNew(mpl.colors.Normalize):
    def __init__(self, vmin, vmax, midpoint=0, clip=False):
        self.midpoint = midpoint
        mpl.colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        if self.vmax == 0:
            normalized_min = self.vmin
        else:
            normalized_min = max(
                0,
                1
                / 2
                * (1 - abs((self.midpoint - self.vmin) / (self.midpoint - self.vmax))),
            )
        if self.vmin == 0:
            normalized_max = self.vmax
        else:
            normalized_max = min(
                1,
                1
                / 2
                * (1 + abs((self.vmax - self.midpoint) / (self.midpoint - self.vmin))),
            )
        if self.vmax == 0 and self.vmin == 0:
            normalized_mid = 0
        else:
            normalized_mid = 0.5
        x, y = [self.vmin, self.midpoint, self.vmax], [
            normalized_min,
            normalized_mid,
            normalized_max,
        ]
        return np.ma.masked_array(np.interp(value, x, y))


# class MidpointNormalize(colors.Normalize):
#     def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
#         self.midpoint = midpoint
#         colors.Normalize.__init__(self, vmin, vmax, clip)

#     def __call__(self, value, clip=None):
#         # I'm ignoring masked values and all kinds of edge cases to make a
#         # simple example...
#         x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
#         return np.ma.masked_array(np.interp(value, x, y))

def _plotting3D(self):    #, val, disp, title, colormap):
    pyvista.global_theme.axes.box = False
    pyvista.global_theme.axes.x_color = 'black'
    pyvista.global_theme.axes.y_color = 'black'
    pyvista.global_theme.axes.z_color = 'black'
    pyvista.global_theme.font.color = 'black'
    #colors = np.random.random(self.El.shape[0])
    #colors = np.zeros(self.El.shape[0])

def PlotMesh3D(self, NodeNumber=True, ElementNumber=True, Loads=True, BC=True, FontMag=1):
    _plotting3D(self)
    mesh = pyvista.PolyData(self.Nodes, np.vstack((np.ones(np.array(self.El).shape[0], int)*2, (np.array(self.El)-1).T)).T)
    mesh.plot(off_screen=False,
              full_screen=False,
              interactive=True,
              parallel_projection=True,
             # show_axes=False,
              #scalars=colors,
              render_lines_as_tubes=True,
              style='wireframe',
              line_width=10,
              cmap="turbo",
              lighting='three lights',
              color="#1f77b4",
              show_scalar_bar=False,
              background='w')




def colorline(x, y, z, cmap="jet", linewidth=2, alpha=1.0, plot=True, norm=None):
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()
    segments = make_segments(x, y)
    lc = mplcollect.LineCollection(
        segments, array=z, cmap=cmap, norm=norm, linewidth=linewidth, alpha=alpha
    )
    if plot:
        ax = plt.gca()
        ax.add_collection(lc)
    return lc


def make_segments(x, y):
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    return segments
