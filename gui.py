# import matplotlib
# matplotlib.use('WXAgg')

from lib.hkeplot import GraphApp
# from hkeplot import GraphApp

#calfolder = u'/Users/jlazear/Documents/HDD Documents/Misc Data/Cal Curves/'

# model = Model()
# #model.loadfile('hke_20130206_004.dat', calfolder + 'U03273.txt')

# plotter = HKEPlotter(model)
# plotter.makefigure()
# plotter.add_subplot(111)

# xs = np.linspace(0, 10, 200)
# ys = np.sin(xs)
# plotter.plot(xs, ys)

app = GraphApp(0)
#app = GraphApp(redirect='log.txt')
fgf = app.fGraphFrame
fmf = app.fMainFrame
# fmf.add_model(model)
app.MainLoop()
