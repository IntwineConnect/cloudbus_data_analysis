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


def create_fig():
    # NOTE: matplotlib retains a global reference to the current figure
    # this means we don't need to pass the resulting object around
    plt.figure()
    fig = plt.gcf()
    fig.set_size_inches(8.5, 11)
    plt.clf()


def create_title_page(pdf, text, subtitle=''):
    create_fig()
    plt.text(0.5, 0.9, text, horizontalalignment='center', fontsize=14)
    plt.text(0.5, 0.6, subtitle, horizontalalignment='center', fontsize=10)
    plt.axis('off')

    pdf.savefig(plt.gcf())
    plt.close()


def create_text_page(pdf, text):
    create_fig()

    plt.axis('off')
    y = 1.0
    for line in text:
        plt.text(0.0, y, line, fontsize=8)
        y -= 0.03
        if y < 0.05:
            pdf.savefig(plt.gcf())
            plt.clf()
            plt.axis('off')
            y = 1.0
    pdf.savefig(plt.gcf())
    plt.close()


def create_table_page(pdf, col1, col2, col3, col4, decoration):
    create_fig()

    plt.axis('off')
    y = 1.0
    for i in range(0, len(col1)):
        if decoration[i] is None:
            weight = 'normal'
            color  = 'black'
        elif decoration[i] == 'red':
            weight = 'normal'
            color  = 'red'
        elif decoration[i] == 'bold':
            weight = 'bold'
            color  = 'black'

        plt.text(0.0, y, col1[i], fontsize=8, fontweight=weight, color=color)
        plt.text(0.4, y, col2[i], fontsize=8, fontweight=weight, color=color)
        plt.text(0.7, y, col3[i], fontsize=8, fontweight=weight, color=color)
        plt.text(0.9, y, col4[i], fontsize=8, fontweight=weight, color=color)

        y -= 0.02
        if y < 0.02:
            pdf.savefig(plt.gcf())
            plt.clf()
            plt.axis('off')
            y = 1.0
    pdf.savefig(plt.gcf())
    plt.close()


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
create_title_page(pp, 'Sensor Report',subtitle=(datetime.isoformat(datetime.now())))

# Generate the details for each device
for device in sensor_agents:
    if device[0] == 'title':
        create_title_page(pp, device[1])
        continue

    print device

    myDevice = cbDevice(device[0])

    attr_list = ['temperature', 'humidity', 'rssi', 'battery_remaining']

    create_fig()
    fig = plt.gcf()
    fig.suptitle("%s - %s" % (device[3], device[2]))

    ax = []
    i = 0
    for attr in attr_list:
        if len(ax) == 0:
            ax.append(plt.subplot(len(attr_list), 1, i+1))
        else:
            ax.append(plt.subplot(len(attr_list), 1, i+1, sharex=ax[0]))
        xlist, ylist = myDevice.getData(attr, tstart, tend)
        y = [float(y) for y in ylist]
        ax[i].plot(xlist, y, "-", alpha=0.5)
        ax[i].set(ylabel=attr)
        if i+1 == len(attr_list):
            ax[i].set(xlabel='Date')
        if attr == 'battery_remaining':
            if len(y) > 0:
                # call out the actual battery remaining value
                plt.annotate(y[-1], (xlist[-1], y[-1]))
        i += 1

    fig.autofmt_xdate()     # cleans up the x-axis tick marks

    pp.savefig(plt.gcf())  # This generates pdf page and appends it to the file

    plt.close()  # Close the plot - pyplot doesn't like having lots open

# Generate Battery Summary
print "Running Battery Summary..."
create_title_page(pp, 'Battery Summary')
col1 = []
col2 = []
col3 = []
col4 = []
alert = []
for device in sensor_agents:
    if device[0] == 'title':
        col1.append('')
        col1.append(device[1])
        col2.append('')
        col2.append('Last Full')
        col3.append('')
        col3.append('Current %')
        col4.append('')
        col4.append('Est. Life')
        alert.append(None)
        alert.append('bold')
        continue

    myDevice = cbDevice(device[0])
    xlist, ylist = myDevice.getData('battery_remaining')
    y = [float(y) for y in ylist]
    try:
        last_full_i = next(i for i in reversed(range(len(y))) if y[i] > 0.999)
        last_full = xlist[last_full_i]
        last_full_str = last_full.strftime("%Y/%m/%d")
        current = y[-1]

        if current < 0.98:
            est_life = ((xlist[-1] - last_full).total_seconds()) / (1.0 - y[-1]) / (60.0*60.0*24.0*365.0/12.0)
            est_life_str = "%.2f months" % est_life
        else:
            est_life_str = 'Need more data'
    except:
        last_full_str = 'Unknown'
        est_life_str = 'Unknown'

    try:
        current = y[-1]
        if current < 0.05:
            alert.append('red')
        else:
            alert.append(None)
    except:
        current = 'Unknown'
        alert.append(None)

    col1.append(device[2])
    col2.append("%s" % (last_full_str,))
    col3.append(current)
    col4.append(est_life_str)


create_table_page(pp, col1, col2, col3, col4, alert)


# close and finalize the pdf file
pp.close()
