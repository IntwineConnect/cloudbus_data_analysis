################################################################################
# Copyright (c) 2017                                                           #
# Intwine Connect, LLC.                                                        #
################################################################################

"""A simple example that will plot and/or save to a csv file the historical
   data use from a given Intwine Gateway or list of systems
"""

from cloudbus import cbDevice
import matplotlib.pyplot as plt

SAVE_TO_CSV = True
CREATE_PLOT = True

guid_list = ['']  # GUID(s) of interest goes here...

for guid in guid_list:
    d = cbDevice(guid)
    a = d.getData('4gdata-use')
    mb = [x/1024.0/1024 for x in a[1]]  # convert into MB

    plt.plot(a[0], mb, "o-", alpha=0.5, label=guid[0:4])

    if SAVE_TO_CSV:
        fout = 'data_use_%s.csv' % guid[0:4]
        with open(fout, 'w') as fid:
            for i in range(0, len(mb)):
                s = "%s,%s\n" % (a[0][i], mb[i])
                fid.write(s)

if CREATE_PLOT:
    plt.xlabel('Date')
    plt.ylabel('Data Use [MB]')
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.show()
