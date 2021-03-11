import vobject
import argparse
from datetime import *
import requests
import recurring_ical_events
import icalendar
import os

parser = argparse.ArgumentParser()
parser.add_argument('--filepath', type=str, help='filepath to text file with iCal url as well as a list of when2meet '
                                                 'urls to update (default: ./urls.txt)', default='urls.txt')
parser.add_argument('--verbosity', type=int, choices=[0, 1, 2], help='0:No output 1:Changes made 2:debugging output')
parser.add_argument('--static', type=str, help='filepath of local iCal file to use')
# parser.add_argument('--update', type=bool, default=True, help='Set to false to use already downloaded calendar')
args = parser.parse_args()

urlFile = args.filepath
verbosity = args.verbosity
updateCal = True
if args.static:
    static = args.static
    updateCal = False
else:
    static = 'calendar.ics'


class When2Meet:
    """A class to hold all information about a when2meet"""

    def __init__(self):
        self.name = ''
        self.url = ''
        self.days = 0
        self.startTime, self.endTime = datetime.now(), datetime.now()
        self.hours = 0
        self.availability = []
        self.eventID = 0
        self.slots = []
        self.personID = 0

    def calculateLength(self):
        self.startTime.replace(tzinfo=datetime.now().astimezone().tzinfo)
        self.startTime.replace(tzinfo=datetime.now().astimezone().tzinfo)
        self.days = (self.endTime - self.startTime).days + 1
        self.hours = (self.endTime.hour - self.startTime.hour)
        # self.slots = (self.startTime-datetime(1970, 1, 1)+timedelta(hours=5)).total_seconds()
        # print(self.slots)
        # print(self.hours)

    def initAvailability(self):
        for i in range(self.days * self.hours * 4):
            self.availability.append('1')

    def initEventID(self):
        self.eventID = self.url.split('?')[1].split('-')[0]

    def setUnavailable(self, startTime, endTime):
        # todo: make this work
        startTime = startTime.replace(tzinfo=None)
        endTime = endTime.replace(tzinfo=None)
        if endTime.replace(day=1, month=1, year=1) > self.endTime.replace(day=1, month=1, year=1):
            endTime = endTime.replace(hour=self.endTime.hour, minute=self.endTime.minute)
        if startTime.replace(day=1, month=1, year=1) < self.startTime.replace(day=1, month=1, year=1):
            startTime = startTime.replace(hour=self.startTime.hour, minute=self.startTime.minute)
        hours = int((endTime - startTime).seconds / 3600)
        minutes = int(((endTime - startTime).seconds - (hours * 3600)) / 60)
        length = (hours * 4) + int((minutes + 14) / 15)
        start = int(((startTime - self.startTime).days * self.hours * 4) +
                    (startTime - self.startTime).seconds / 3600 * 4)
        for i in range(length):
            self.availability[i + start] = "0"
            # self.slot = (startTime-datetime(1970, 1, 1) + timedelta(hours=5)).total_seconds()
            # postAvail(self)
        return

    def parseHTML(self, filepath):
        self.url = 'https://www.when2meet.com/?' + filepath
        file = open(filepath, 'r')
        lastLine = ''
        twoAgo = ''
        timeArray = False
        while True:

            line = file.readline()

            if not line:
                break
            if '<title>' in line:
                self.name = line.split('<title>')[1].split(' - When2meet')[0]
                print(self.name)
            if "TimeOfSlot[0]" in line:
                self.startTime = datetime.fromtimestamp(int(line.split('=')[1].split(";")[0]))
                # self.slots.append(line.split('=')[1].split(";")[0] + '%')
                print(self.startTime)
                timeArray = True
            if "TimeOfSlot[" in line and timeArray:
                self.slots.append(line.split('=')[1].split(";")[0] + '%')
            if ("var AvailableIDs=new Array();" in line and "TimeOfSlot" in twoAgo) or \
                    ("PeopleNames[0]" in line and "TimeOfSlot" in twoAgo):
                self.endTime = datetime.fromtimestamp(int(twoAgo.split('=')[1].split(";")[0])) + timedelta(
                    minutes=15)
                print(self.endTime)
                break
            twoAgo = lastLine
            lastLine = line
        self.calculateLength()
        self.initAvailability()
        self.initEventID()
        file.close()
        return

    def updateAvail(self, cal):
        events = recurring_ical_events.of(cal).between(self.startTime, self.endTime)
        for event in events:
            if event.get('X-MICROSOFT-CDO-BUSYSTATUS') == 'BUSY':
                if (self.startTime.replace(day=1, month=1, year=1) <=
                    event.get('dtstart').dt.replace(tzinfo=None, day=1, month=1, year=1) < self.endTime.replace(day=1, month=1, year=1)) or \
                        (event.get('dtstart').dt.replace(tzinfo=None, day=1, month=1, year=1) < self.endTime.replace(
                            day=1, month=1, year=1)):
                    self.setUnavailable(event.get('dtstart').dt, event.get('dtend').dt)
                    print(event.get('summary'), end='')
                    print(': ', end='')
                    print(event.get('dtstart').dt)

        return

    def login(self):
        file = open('creds.jpg', 'r')
        name = file.readline().split('\n')[0]
        password = file.readline().split('\n')[0]
        meetingID = self.eventID
        file.close()
        url = 'https://www.when2meet.com/ProcessLogin.php'
        formData = {'id': meetingID,
                    'name': name,
                    'password': password,
                    '_': ''}
        response = requests.post(url, data=formData)
        self.personID = response.text
        # print(response.text)
        return

    def postAvail(self):
        url = 'https://www.when2meet.com/SaveTimes.php'

        formData = {'person': self.personID,
                    'event': self.eventID,
                    'slots': ''.join(self.slots),
                    'availability': ''.join(self.availability),
                    '_': ''}
        response = requests.post(url, data=formData)
        # print(response)
        return

    def clear(self):
        self.__init__()


def getFromWeb(filepath):
    file = open(filepath, 'r')
    urls = []
    resultFiles = []
    while True:
        line = file.readline()
        line = line.split('\n')[0]
        if not line:
            break
        urls.append(line)
        resultFiles.append(line.split('/')[-1].split('?')[-1])
    file.close()
    for i in range(len(urls)):
        if i == 0 and not updateCal:
            i += 1
        filepath = resultFiles[i]
        url = urls[i]
        file = open(filepath, 'w')
        debugPrint(url)
        data = requests.get(url).text.replace('\r', '')
        debugPrint(data)
        file.write(data)
    resultFiles = resultFiles[1:]
    return resultFiles


def debugPrint(msg):
    if verbosity == 2:
        print(msg)


def cleanupFiles(fileList):
    # todo
    return


def main():
    when2meetFiles = getFromWeb(urlFile)
    iCalStream = open(static).read()
    cal = icalendar.Calendar.from_ical(iCalStream)
    # cal = calObj.contents.get('vevent')
    meetings = [When2Meet() for i in range(len(when2meetFiles))]
    for i in range(len(when2meetFiles)):
        meeting = meetings[i]
        file = when2meetFiles[i]
        meeting.parseHTML(file)
        meeting.login()
        meeting.updateAvail(cal)
        meeting.postAvail()
        meeting.clear()
    cleanupFiles(when2meetFiles)
    return


main()
