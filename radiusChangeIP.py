# update the jumpcloud radius IP via API call if public IP changes
# For backwards compatibility
from __future__ import print_function

import requests
import json
import sys

class JumpcloudRadius:
    def __init__(self):
        # This is the URL of the API
        self.url = 'https://console.jumpcloud.com/api/radiusservers/'
        # Public IP placeholders

        # Headers required for API calls
        self.headersAndAPI = {
            'Content-Type' : 'application/json',
            'Accept' : 'application/json',
            'x-api-key' : 'add-your-api-key-from-jumpcloud-here'
        }

    def printExitCodes(self):
        '''
        Will just print out a list of system exit codes that could be returned for various conditions
        '''
        print('''
        Code 5 = failed to get newIP from {url}
        Code 6 = radiusID fetch failed in parsing response data, info returned probably was not expected
        Code 7 = failed to get radiusID from Jumpcloud API call, response code was not a 200
        Code 8 = oldIP fetch failed in parsing response data, info returned probably was not expected
        Code 9 = failed to get oldIP from Jumpcloud API call, response code was not a 200
        '''.format(url=self.url))


    def getPublicIP(self):
        '''
        This will fetch the public ip of the calling host and return it
        :return: newIP
        '''
        # Grab the public IP and store in newIP
        req = requests.get('https://api.ipify.org')
        newIP = req.text

        if req.status_code == 200:
            # Return the public IP
            return newIP
        else:
            # We didn't get a 200 so we didn't get the public IP, we need to exit
            sys.exit(5)


    def getRadiusID(self):
        '''
        This will query jumpcloud to get the radius server ID in question
        :return: radiusID
        '''

        # request object using get to pull down data
        req = requests.get(self.url, headers=self.headersAndAPI)

        # data holds all info returned from API call
        data = req.json()

        if req.status_code == 200:
            try:
                # Radius server id for the next step
                radiusID = data['results'][0]['_id']

                return radiusID
            except:
                sys.exit(6)
        else:
            sys.exit(7)


    def getJumpcloudCurrentIP(self):
        '''
        This will query jumpcloud to see what the current public IP is
        :return: oldIP
        '''

        # request object using get to pull down data
        req = requests.get(self.url, headers=self.headersAndAPI)

        # data holds all info returned from API call
        data = req.json()

        if req.status_code == 200:
            try:
                # current IP info server id for the next step
                oldIP = data['results'][0]['networkSourceIp']

                return oldIP
            except:
                sys.exit(8)
        else:
            sys.exit(9)

    def updateJumpcloudIP(self, radiusID='', newIP='', oldIP=''):
        '''
        take the values of radiusID, newIP and old IP
        first compare to see if newIP and oldIP vary, and if so then update
        if no change in the public IP then exit
        :param radiusID:
        :param newIP: pulled from api.ipify.org
        :param oldIP: pulled from jumpcloud API get
        :return:
        '''

        # The data to post with the PUT
        putData = {'networkSourceIp':newIP}

        # The update is a PUT request
        newURL = '{url}{radiusID}'.format(url=self.url, radiusID=radiusID)
        # Make the change ONLY if the new IP varies from the old IP
        if oldIP != newIP:
            print('IP has changed')
            # Jumpcloud REQUIRES the data be a string and not a binary JSON object
            # json.dumps will convert the object to a string hence the s on dump(s)
            req = requests.put(newURL, data=json.dumps(putData), headers=self.headersAndAPI)

            # If request was good
            if req.status_code == 200:
                print('IP was updated in jumpcloud successfully')
                print('oldIP was {oldIP} and updated to {newIP}'.format(oldIP=oldIP, newIP=newIP))
        else:
            print('IP is the same, good try though \_("/)_/')



if __name__ == '__main__':
    update = JumpcloudRadius()
    update.updateJumpcloudIP(radiusID=update.getRadiusID(),
                             newIP=update.getPublicIP(),
                             oldIP=update.getJumpcloudCurrentIP())

