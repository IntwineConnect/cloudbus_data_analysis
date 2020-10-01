from cloudbus import cbDevice
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from matplotlib.backends.backend_pdf import PdfPages

"""
This script will generate a PDF report based on provided device ID values.
It is primarily setup for monitoring temperature coming from temperature sesnors
but can be easily adapted to nearly any device type/data type.

The input file is sensor_report.txt.  It is a CSV formatted file with the
following columns:
device id, address, name, customer

You can also create subtitle pages by adding rows formatted as:
title, Desired SubTitle

The pdf report generated in placed in a subfolder called pdf.  The filename is
sensor_report.pdf
"""


def create_title_page(text, subtitle=''):
    plt.figure()
    plt.clf()
    plt.text(0.5, 0.9, text, horizontalalignment='center', fontsize=14)
    plt.text(0.5, 0.6, subtitle, horizontalalignment='center', fontsize=10)
    plt.axis('off')


def load_agents():
    agents = []
    with open('sensor_report.txt', 'r') as fin:
        lines = fin.readlines()
        for line in lines:
            agents.append(tuple(line.strip().split(',')))
    return agents


sensor_agents = load_agents()

tend = datetime.utcnow()
tstart = tend - timedelta(days=7)

# Create the pdf file
pdf_folder = r'pdf'
output_pdf_file = os.path.join(pdf_folder, 'sensor_report.pdf')
pp = PdfPages(output_pdf_file)

# Generate Title Page
create_title_page('Sensor Report',subtitle=(datetime.isoformat(datetime.now())))
pp.savefig()

# Generate the details for each device
for device in sensor_agents:
    if device[0] == 'title':
        create_title_page(device[1])
        pp.savefig(plt.gcf())
        plt.close()
        continue

    print device

    myDevice = cbDevice(device[0])

    attr_list = ['temperature', 'humidity', 'rssi', 'battery_remaining']

    fig, axs = plt.subplots(len(attr_list), sharex=True)
    fig.suptitle("%s - %s" % (device[3], device[2]))

    i = 0
    for attr in attr_list:

        xlist, ylist = myDevice.getData(attr, tstart, tend)
        y = [float(y) for y in ylist]
        axs[i].plot(xlist, y, "-", alpha=0.5)
        axs[i].set(ylabel=attr)
        if attr == 'battery_remaining':
            if len(y) > 0:
                # call out the actual battery remaining value
                plt.annotate(y[-1], (xlist[-1],y[-1]))
        i += 1

    axs[-1].set(xlabel='Date')
    fig.autofmt_xdate()     # cleans up the x-axis tick marks

    pp.savefig(plt.gcf())  # This generates pdf page and appends it to the file

    plt.close()  # Close the plot - pyplot doesn't like having lots open

pp.close()  # close and finalize the pdf file
