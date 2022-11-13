# fit a line to the economic data
from numpy import sin
from numpy import sqrt
from numpy import arange
from pandas import read_csv
from scipy.optimize import curve_fit
from matplotlib import pyplot


# define the true objective function
def objective(x, a, b, c, d):
    return a * x + b * x**2 + c
pyplot.gca().invert_yaxis()
# load the dataset
x=[217, 265, 272, 325, 336, 368, 328, 334, 348, 369, 368, 369, 267, 267, 216, 242, 354, 367, 246, 266, 293, 324]
y=[352, 412, 294, 323, 337, 409, 326, 336, 366, 406, 439, 407, 439, 416, 352, 384, 381, 400, 390, 414, 305, 321]


popt, _ =curve_fit(objective, x, y)
# summarize the parameter values
a, b, c, d=popt
print(popt)
# plot input vs output
pyplot.scatter(x, y)
# define a sequence of inputs between the smallest and largest known inputs
x_line=arange(min(x), max(x), 1)
# calculate the output for the range
y_line=objective(x_line, a, b, c, d)
# create a line plot for the mapping function
pyplot.plot(x_line, y_line, '--', color='red')
pyplot.show()