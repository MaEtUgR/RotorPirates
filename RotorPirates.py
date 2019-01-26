import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
mpl.rcParams['toolbar'] = 'None'

# defaults
# RF
rfrate_default = 400
rfexpo_default = 50
rfacrop_default = 140

# BF
bfrate_default=1.0
bfexpo_default=0.0
bfsuper_default=0.7

# KISS
ksrate_default=0.7
kscurve_default=0.4
ksrcrate_default=0.7

# PX4
px4ratemax_default=720
px4expo_default=0.69
px4superexpo_default=0.7


# KISS rate function
def kscalc(rcCommand, rate, rcCurve, rcRate):
    kissRpyUseRates = 1 - abs(rcCommand) * rate
    kissRxRaw = rcCommand * 1000
    kissTempCurve = (kissRxRaw * kissRxRaw / 1000000)
    rcCommand = ((rcCommand * kissTempCurve) * rcCurve + rcCommand * (1 - rcCurve)) * (rcRate / 10)
    kissAngle = ((2000.0 * (1.0 / kissRpyUseRates)) * rcCommand) #setpoint is calculated directly here
    return kissAngle


# RF rate function
def rfcalc(rcCommand, rate, expo, acrop):
    returnValue = ((1 + 0.01 * expo * (rcCommand * rcCommand - 1.0)) * rcCommand)
    returnValue = (returnValue * (rate + (abs(returnValue) * rate * acrop * 0.01)))
    return returnValue



# BF rate calculation function
def bfcalc(rcCommand, rcRate, expo, superRate):
    clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

    absRcCommand = abs(rcCommand)

    if rcRate > 2.0:
        rcRate = rcRate + (14.54 * (rcRate - 2.0))

    if expo != 0:
        rcCommand = rcCommand * abs(rcCommand)**3  * expo + rcCommand * (1.0 - expo)

    angleRate = 200.0 * rcRate * rcCommand
    if superRate != 0:
        rcSuperFactor = 1.0 / (clamp(1.0 - (absRcCommand * (superRate)), 0.01, 1.00))
        angleRate *= rcSuperFactor
    return angleRate


# PX4 rate function
def px4calc(rcCommand, ratemax, expo, superexpo):
    x = np.clip(rcCommand, -1, 1)
    ec = np.clip(expo, 0, 1)
    gc = np.clip(superexpo, 0, 0.99)

    xe = (1 - ec) * x + ec * x * x * x
    xg = xe * (1 - gc) / (1 - np.abs(x) * gc)
    return xg * ratemax

# set up graph
axis_color = 'lightgray'

fig = plt.figure(figsize=(8, 10))
fig.canvas.set_window_title('RotorPirates')
#ax = fig.add_subplot(111)
ax = fig.add_axes([0.15, 0.5, 0.75, 0.45], facecolor=axis_color)

# Adjust the subplots region to leave some space for the sliders and buttons
fig.subplots_adjust(left=0.25, bottom=0.55)

# Range for time (rcCommand)
t = np.arange(0.0, 1.0, 0.001)

# Set up arrays for initial plot
rfplot = [rfcalc(g, rfrate_default, rfexpo_default, rfacrop_default)   for g in t]
bfplot = [bfcalc(g, bfrate_default, bfexpo_default, bfsuper_default)   for g in t]
ksplot = [kscalc(g, ksrate_default, kscurve_default, ksrcrate_default) for g in t]
px4plot = [px4calc(g, px4ratemax_default, px4expo_default, px4superexpo_default) for g in t]

# Draw lines, save variables for later use
[rfline] = ax.plot(t, rfplot, linewidth=2, color='red')
[bfline] = ax.plot(t, bfplot, linewidth=2, color='blue')
[ksline] = ax.plot(t, ksplot, linewidth=2, color='green')
[px4line] = ax.plot(t, px4plot, linewidth=2, color='black')
ax.set_xlim([0, 1])

# Determin min/max for each plot to set graph range
rfmax = np.array(rfplot).max()
bfmax = np.array(bfplot).max()
ksmax = np.array(ksplot).max()
px4max = np.array(px4plot).max()

rfmin = np.array(rfplot).min()
bfmin = np.array(bfplot).min()
ksmin = np.array(ksplot).min()
px4min = np.array(px4plot).min()
ax.set_ylim([np.array([rfmin, bfmin, ksmin, px4min]).min(), np.array([rfmax, bfmax, ksmax, px4max]).max()])

# Set up sliders
slider_thickness = 0.02

rfrate_slider_ax = fig.add_axes([0.25, 0.41, 0.65, slider_thickness], facecolor=axis_color)
rfrate_slider = Slider(rfrate_slider_ax, 'RFRate', 0, 1000, valinit=rfrate_default, valfmt='%1.0f')
rfexpo_slider_ax = fig.add_axes([0.25, 0.38, 0.65, slider_thickness], facecolor=axis_color)
rfexpo_slider = Slider(rfexpo_slider_ax, 'RFExpo', 0, 100, valinit=rfexpo_default, valfmt='%1.0f')
rfacrop_slider_ax = fig.add_axes([0.25, 0.35, 0.65, slider_thickness], facecolor=axis_color)
rfacrop_slider = Slider(rfacrop_slider_ax, 'RFAcro+', 0, 1000, valinit=rfacrop_default, valfmt='%1.0f')

bfrate_slider_ax = fig.add_axes([0.25, 0.31, 0.65, slider_thickness], facecolor=axis_color)
bfrate_slider = Slider(bfrate_slider_ax, 'BFRate', 0, 3.0, valinit=bfrate_default, valfmt='%1.2f')
bfexpo_slider_ax = fig.add_axes([0.25, 0.28, 0.65, slider_thickness], facecolor=axis_color)
bfexpo_slider = Slider(bfexpo_slider_ax, 'BFExpo', 0, 1.0, valinit=bfexpo_default, valfmt='%1.2f')
bfsuper_slider_ax = fig.add_axes([0.25, 0.25, 0.65, slider_thickness], facecolor=axis_color)
bfsuper_slider = Slider(bfsuper_slider_ax, 'BFSuper', 0, 1.0, valinit=bfsuper_default, valfmt='%1.2f')

ksrate_slider_ax = fig.add_axes([0.25, 0.21, 0.65, slider_thickness], facecolor=axis_color)
ksrate_slider = Slider(ksrate_slider_ax, 'KISS Rate', 0, 1.0, valinit=ksrate_default, valfmt='%1.2f')
kscurve_slider_ax = fig.add_axes([0.25, 0.18, 0.65, slider_thickness], facecolor=axis_color)
kscurve_slider = Slider(kscurve_slider_ax, 'KISS RC Curve', 0, 1.0, valinit=kscurve_default, valfmt='%1.2f')
ksrcrate_slider_ax = fig.add_axes([0.25, 0.15, 0.65, slider_thickness], facecolor=axis_color)
ksrcrate_slider = Slider(ksrcrate_slider_ax, 'KISS RC rate', 0, 10.0, valinit=ksrcrate_default, valfmt='%1.2f')

px4ratemax_slider_ax = fig.add_axes([0.25, 0.11, 0.65, slider_thickness], facecolor=axis_color)
px4ratemax_slider = Slider(px4ratemax_slider_ax, 'PX4 maximum rate', 0, 1500.0, valinit=px4ratemax_default, valfmt='%1.0f')
px4expo_slider_ax = fig.add_axes([0.25, 0.08, 0.65, slider_thickness], facecolor=axis_color)
px4expo_slider = Slider(px4expo_slider_ax, 'PX4 expo', 0, 1.0, valinit=px4expo_default, valfmt='%1.2f')
px4superexpo_slider_ax = fig.add_axes([0.25, 0.05, 0.65, slider_thickness], facecolor=axis_color)
px4superexpo_slider = Slider(px4superexpo_slider_ax, 'PX4 superexpo', 0, 1.0, valinit=px4superexpo_default, valfmt='%1.2f')


# Slider change handler
def sliders_on_changed(val):
    # setup ararys for new plots
    rfplot = [rfcalc(g, rfrate_slider.val, rfexpo_slider.val,  rfacrop_slider.val)  for g in t]
    bfplot = [bfcalc(g, bfrate_slider.val, bfexpo_slider.val,  bfsuper_slider.val)  for g in t]
    ksplot = [kscalc(g, ksrate_slider.val, kscurve_slider.val, ksrcrate_slider.val) for g in t]
    px4plot = [px4calc(g, px4ratemax_slider.val, px4expo_slider.val, px4superexpo_slider.val) for g in t]

    # set lines to new plots
    rfline.set_ydata(rfplot)
    bfline.set_ydata(bfplot)
    ksline.set_ydata(ksplot)
    px4line.set_ydata(px4plot)
    # updte min/max values
    rfmax = np.array(rfplot).max()
    bfmax = np.array(bfplot).max()
    ksmax = np.array(ksplot).max()
    px4max = np.array(px4plot).max()
    rfmin = np.array(rfplot).min()
    bfmin = np.array(bfplot).min()
    ksmin = np.array(ksplot).min()
    px4min = np.array(px4plot).min()
    ax.set_ylim([np.array([rfmin, bfmin, ksmin, px4min]).min(), np.array([rfmax, bfmax, ksmax, px4max]).max()])

    # update canvas
    fig.canvas.draw_idle()


rfrate_slider.on_changed(sliders_on_changed)
rfexpo_slider.on_changed(sliders_on_changed)
rfacrop_slider.on_changed(sliders_on_changed)
bfrate_slider.on_changed(sliders_on_changed)
bfexpo_slider.on_changed(sliders_on_changed)
bfsuper_slider.on_changed(sliders_on_changed)
ksrate_slider.on_changed(sliders_on_changed)
kscurve_slider.on_changed(sliders_on_changed)
ksrcrate_slider.on_changed(sliders_on_changed)
px4ratemax_slider.on_changed(sliders_on_changed)
px4expo_slider.on_changed(sliders_on_changed)
px4superexpo_slider.on_changed(sliders_on_changed)

# Add a button for resetting the parameters
reset_button_ax = fig.add_axes([0.8, 0.01, 0.1, 0.02])
reset_button = Button(reset_button_ax, 'Reset', color=axis_color, hovercolor='0.975')
def reset_button_on_clicked(mouse_event):
    rfrate_slider.reset()
    rfexpo_slider.reset()
    rfacrop_slider.reset()
    bfrate_slider.reset()
    bfexpo_slider.reset()
    bfsuper_slider.reset()
    ksrate_slider.reset()
    kscurve_slider.reset()
    ksrcrate_slider.reset()
    px4ratemax_slider.reset()
    px4expo_slider.reset()
    px4superexpo_slider.reset()

reset_button.on_clicked(reset_button_on_clicked)


plt.show()
