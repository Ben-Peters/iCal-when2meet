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
    name = ''
    url = ''
    days = 0
    startTime, endTime = datetime.now(), datetime.now()
    hours = endTime - startTime
    availability = []
    eventID = 0
    slots = []
    personID = 0

    def calculateLength(self):
        self.startTime.replace(tzinfo=datetime.now().astimezone().tzinfo)
        self.startTime.replace(tzinfo=datetime.now().astimezone().tzinfo)
        self.days = (self.endTime - self.startTime).days + 1
        self.hours = (self.endTime.hour - self.startTime.hour)
        # self.slots = (self.startTime-datetime(1970, 1, 1)+timedelta(hours=5)).total_seconds()
        print(self.slots)
        print(self.hours)

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
        hours = int((endTime-startTime).seconds / 3600)
        minutes = int(((endTime - startTime).seconds - (hours * 3600)) / 60)
        length = (hours * 4) + int((minutes + 14) / 15)
        start = int(((startTime-self.startTime).days * self.hours * 4) +
                    (startTime - self.startTime).seconds / 3600 * 4)
        for i in range(length):
            self.availability[i+start] = "0"
            #self.slot = (startTime-datetime(1970, 1, 1) + timedelta(hours=5)).total_seconds()
            #postAvail(self)
        return


def parseCal(filepath):
    iCalStream = open("calendar.ics").read()

    cal = vobject.readOne(iCalStream)
    for event in cal.contents.get('vevent'):

        if verbosity == 2:
            try:
                print('Summary: ', event.summary.valueRepr())
                print('Description: ', event.description.valueRepr())
                print('Time (as a datetime object): ', event.dtstart.value)
                print('-------------------------------------------------\n')
            except AttributeError:
                print("Something wasn't found")
    return


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


def addMeetingData(filepath, meeting):
    meeting.url = 'https://www.when2meet.com/?' + filepath
    file = open(filepath, 'r')
    lastLine = ''
    twoAgo = ''
    timeArray = False
    while True:

        line = file.readline()

        if not line:
            break
        if '<title>' in line:
            meeting.name = line.split('<title>')[1].split(' - When2meet')[0]
            print(meeting.name)
        if "TimeOfSlot[0]" in line:
            meeting.startTime = datetime.fromtimestamp(int(line.split('=')[1].split(";")[0]))
            # meeting.slots.append(line.split('=')[1].split(";")[0] + '%')
            print(meeting.startTime)
            timeArray = True
        if "TimeOfSlot[" in line and timeArray:
            meeting.slots.append(line.split('=')[1].split(";")[0] + '%')
        if ("var AvailableIDs=new Array();" in line and "TimeOfSlot" in twoAgo) or \
                ("PeopleNames[0]" in line and "TimeOfSlot" in twoAgo):
            meeting.endTime = datetime.fromtimestamp(int(twoAgo.split('=')[1].split(";")[0])) + timedelta(minutes=15)
            print(meeting.endTime)
            break
        twoAgo = lastLine
        lastLine = line
    meeting.calculateLength()
    meeting.initAvailability()
    meeting.initEventID()
    file.close()
    return


def updateMeeting(cal, meeting):
    events = recurring_ical_events.of(cal).between(meeting.startTime, meeting.endTime)
    for event in events:
        if event.get('X-MICROSOFT-CDO-BUSYSTATUS') == 'BUSY':
            if meeting.startTime.replace(day=1, month=1, year=1) <= \
                    event.get('dtstart').dt.replace(tzinfo=None, day=1, month=1, year=1) < \
                    meeting.endTime.replace(day=1, month=1, year=1) or \
                    (event.get('dtend').dt.replace(tzinfo=None, day=1, month=1, year=1) > meeting.startTime.replace(day=1, month=1, year=1) > event.get('dtstart').dt.replace(tzinfo=None, day=1, month=1, year=1)):
                meeting.setUnavailable(event.get('dtstart').dt, event.get('dtend').dt)
                print(event.get('summary'), end='')
                print(': ', end='')
                print(event.get('dtstart').dt)

    return


def login(meeting):
    file = open('creds.jpg', 'r')
    name = file.readline().split('\n')[0]
    password = file.readline().split('\n')[0]
    meetingID = meeting.eventID
    file.close()
    url = 'https://www.when2meet.com/ProcessLogin.php'
    formData = {'id': meetingID,
                'name': name,
                'password': password,
                '_': ''}
    response = requests.post(url, data=formData)
    meeting.personID = response.text
    print(response.text)
    return


def postAvail(meeting):
    url = 'https://www.when2meet.com/SaveTimes.php'

    formData = {'person': meeting.personID,
                'event': meeting.eventID,
                'slots': meeting.slots,
                'availability': ''.join(meeting.availability),
                '_': ''}
    response = requests.post(url, data=formData)
    # print(response)
    return


def cleanupFiles(fileList):
    # todo
    return


def main():
    when2meetFiles = getFromWeb(urlFile)
    iCalStream = open(static).read()
    cal = icalendar.Calendar.from_ical(iCalStream)
    # cal = calObj.contents.get('vevent')
    meetings = [When2Meet for i in range(len(when2meetFiles))]
    for file, meeting in zip(when2meetFiles, meetings):
        meeting = When2Meet()
        addMeetingData(file, meeting)
        login(meeting)
        updateMeeting(cal, meeting)
        postAvail(meeting)
    cleanupFiles(when2meetFiles)
    return


main()
