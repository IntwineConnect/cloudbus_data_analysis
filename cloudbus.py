################################################################################
# Copyright (c) 2017                                                           #
# Intwine Connect, LLC.                                                        #
#                                                                              #
# BSD-2-Clause                                                                 #
# DESCRIPTION OF OTHER RIGHTS AND LIMITATIONS                                  #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided that the following conditions are met:  #
# 1. Redistributions of source code must retain the above copyright notice,    #
#    this list of conditions and the following disclaimer.                     #
# 2. Redistributions in binary form must reproduce the above copyright notice, #
#    this list of conditions and the following disclaimer in the documentation #
#    and/or other materials provided with the distribution.                    #
#                                                                              #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,        #
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR       #
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR            #
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,        #
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,          #
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;  #
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,     #
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR      #
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF       #
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                   #
################################################################################

import urllib
import json
import datetime as dt

CBUS_IP = "54.172.91.188:8080"


def get_response(uri):
    read_url = urllib.urlopen(uri)
    response = ""
    for line in read_url:
        response += line
    read_url.close()
    return json.loads(response)


class cbDevice():
    """CloudBUS Device Class

    """
    guid = None
    data = {}

    def __init__(self, guid=None):
        if guid is not None:
            self.guid = guid

    def setGUID(self, guid):
        """Assigns the cbDevice a specified guid

        Args:
            guid: the string representation of the device identifier
        """

        assert guid is True, "GUID can not be empty"
        self.__init__(guid)

    def getData(self, variable, tstart=None, tend=None):
        """Get data from the CloudBUS device APIs

        Request all reported values of data sent to CloudBUS from this specific
        device with attribute = variable.  If desired, the time range over which
        the data was collected can be specified.

        Args:
            variable: name of the attribute for which to get historical data
            tstart:   optional datetime of the earliest time for which to request
                      the specified attribute. Defaults to Unix time of 0.
            tend:     optional datetime of the most recent time for which to
                      request the specified attribute. Defaults to tomorrow.

        Returns:
            A tuple of lists. Element 0 of the tuple is a list of datetimes and
            element 1 is the list of attibute values at each of the element 0
            datetime points. The two lists will always be the same length. The
            lists are sorted so that element 0 of the time list is the earliest
            reported timestamp.
        """

        if tstart is None:
            tstart = dt.datetime.fromtimestamp(0)
        if tend is None:
            tend = dt.datetime.now() + dt.timedelta(days=1)  # tomorrow

        # build the CloudBUS URI
        url = 'http://' + CBUS_IP + '/cloudbus/device/'
        query = '/data?attr=%s' % variable
        query += '&start=' + tstart.strftime("%Y-%m-%d %H:%M:%S")
        query += '&end=' + tend.strftime("%Y-%m-%d %H:%M:%S")
        query = query.replace(' ', '%20')

        # request the URL and read the response
        resp = get_response(url + self.guid + query)

        # format the data to be returned
        data = dict(resp['data'])
        a = sorted(data.items())
        t_vector = []
        y_vector = []
        for i in a:
            t_vector.append( dt.datetime.fromtimestamp(float(i[0])/1000.0) )
            y_vector.append( float(i[1]) )
        return t_vector, y_vector

    def getCurrentData(self):
        """Gets most recently reported data from the device.

        This method will return the most recently reported values for all attributes
        associated with the device.

        Returns:
            A dictionary with keys of attribute names. The value associated with
            each key is a tuple of datetime and attribute value.
            Note that the attribute value will be a string since we have no way
            to know the correct data type and things that pass isfloat( ) are
            inconsistent at best.  See https://stackoverflow.com/questions/379906/parse-string-to-float-or-int
        """

        # build the CloudBUS URI
        url = 'http://' + CBUS_IP + '/cloudbus/device/'
        query = '/currentdata'
        # request the URL and read the response
        resp = get_response(url + self.guid + query)

        # format the data to be returned
        current_data = {}
        if 'endpoints' not in resp:
            raise ValueError("'endpoints' not in response")

        for endpoint in resp['endpoints']:
            for k,v in endpoint.iteritems():
                if '_time' in k or k == 'endpointId':
                    continue
                t = dt.datetime.fromtimestamp(float(endpoint[k + '_time'])/1000.0)
                current_data[k] = (t, v)

        return current_data

class cbGateway(cbDevice):
    """CloudBUS Gateway device
    """

    def getDevices(self):
        """Gets a list of devices that are provisioned to this gateway device.

        This method will return a dictionary with the GUID of all devices that
        have been provisioned to this gateway.

        Returns:
            A dictionary of provisioned devices. Each key is a different device's
            GUID and the associated value is the device type.
        """

        # build the CloudBUS URI
        url = 'http://' + CBUS_IP + '/cloudbus/gateway/'
        # request the URL and read the response
        resp = get_response(url + self.guid)

        # format the data to be returned
        devices = {}
        if 'devices' not in resp:
            return None

        for device in resp['devices']:
            devices[device['deviceId']] = device['deviceType']

        return devices

    def getCurrentData(self):
        """Gets most recently reported data from the gateway.

        This method will return the most recently reported values for all attributes
        associated with the gateway.

        Returns:
            A dictionary with keys of attribute names. The value associated with
            each key is a tuple of datetime and attribute value.
            Note that the attribute value will be a string since we have no way
            to know the correct data type and things that pass isfloat( ) are
            inconsistent at best.  See https://stackoverflow.com/questions/379906/parse-string-to-float-or-int
        """

        # build the CloudBUS URI
        url = 'http://' + CBUS_IP + '/cloudbus/device/'
        query = '/currentdata'
        # request the URL and read the response
        resp = get_response(url + self.guid + query)

        # format the data to be returned
        current_data = {}
        if 'currentData' not in resp:
            raise ValueError("'currentData' not in response")

        for k,v in resp['currentData'].iteritems():
            if '_time' in k or k == 'device_id':
                continue
            t = dt.datetime.fromtimestamp(float(resp['currentData'][k + '_time'])/1000.0)
            current_data[k] = (t, v)

        return current_data
