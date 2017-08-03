from cloudbus import cbDevice
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

"""
A script that uses cbDevice to generate a plot of data for a given guid and
attribute.

example usage:
python plot_attribute.py "YOURGUID" "power"
"""

guid = sys.argv[1]
attribute = sys.argv[2]
myDevice = cbDevice()
myDevice.setGUID(guid)
tend   = datetime.utcnow()
tstart = tend - timedelta(weeks=2)
xlist, ylist = myDevice.getData(attribute, tstart, tend)
plt.plot(xlist,ylist, "o", alpha=0.5, label=guid)
plt.xlabel('date')
plt.ylabel(attribute)
plt.gcf().autofmt_xdate()
plt.legend()
plt.show()
