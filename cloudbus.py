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
import sys

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
        assert guid, "GUID can not be empty"
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
        url = 'http://54.172.91.188:8080/cloudbus/device/'
        query = '/data?attr=%s' % variable
        query += '&start=' + tstart.strftime("%Y-%m-%d %H:%M:%S")
        query += '&end=' + tend.strftime("%Y-%m-%d %H:%M:%S")
        query = query.replace(' ', '%20')

        if sys.version_info[0] == 3:
            with urllib.request.urlopen(url+self.guid+query) as read_url:
                s = read_url.read()
            response = s.decode('utf-8')

        else:
            # request the URL and read the response
            read_url = urllib.urlopen(url + self.guid + query)
            response = ""
            for line in read_url:
                response += line
            read_url.close()
        
        resp = json.loads(response)

        # format the data to be returned
        data = dict(resp['data'])
        a = sorted(data.items())
        t_vector = []
        y_vector = []
        for i in a:
            t_vector.append( dt.datetime.fromtimestamp(float(i[0])/1000.0) )
            y_vector.append( float(i[1]) )
        return t_vector, y_vector
