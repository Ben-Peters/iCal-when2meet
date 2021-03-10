import vobject
import argparse
from datetime import *
import requests
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
    slots = startTime

    def calculateLength(self):
        self.days = (self.endTime - self.startTime).days
        self.hours = (self.endTime.hour - self.startTime.hour)
        #self.slots = (self.startTime-datetime(1970, 1, 1)+timedelta(hours=5)).total_seconds()
        print(self.slots)
        print(self.hours)

    def initAvailability(self):
        self.availability = [True for i in range(self.days.days * (int(self.hours.seconds / 3600) * 4))]

    def setUnavailable(self, day, startTime, endTime):
        # todo: make this work
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
    while True:

        line = file.readline()

        if not line:
            break
        if '<title>' in line:
            meeting.name = line.split('<title>')[1].split(' - When2meet')[0]
            print(meeting.name)
        if "TimeOfSlot[0]" in line:
            meeting.startTime = datetime.fromtimestamp(int(line.split('=')[1].split(";")[0]))
            meeting.slots = line.split('=')[1].split(";")[0]
            print(meeting.startTime)
        if ("var AvailableIDs=new Array();" in line and "TimeOfSlot" in twoAgo) or \
           ("PeopleNames[0]" in line and "TimeOfSlot" in twoAgo):
            meeting.endTime = datetime.fromtimestamp(int(twoAgo.split('=')[1].split(";")[0])) + timedelta(minutes=15)
            print(meeting.endTime)
        twoAgo = lastLine
        lastLine = line
    meeting.calculateLength()
    meeting.availability = [True for i in range(meeting.days*meeting.hours*4)]
    file.close()
    return


def updateMeeting(cal, meeting):
    # todo
    return


def makeLoginPost():
    # todo
    return


def createPostMsg(meeting):
    # todo
    return


def sendPost(msg):
    # todo
    return


def cleanupFiles(fileList):
    # todo
    return


def main():
    when2meetFiles = getFromWeb(urlFile)
    when2meets = []
    for file in when2meetFiles:
        meeting = When2Meet()
        addMeetingData(file, meeting)
        when2meets.append(meeting)
    cal = parseCal(static)
    postMsg = [makeLoginPost()]
    for meeting in when2meets:
        updateMeeting(cal, meeting)
        postMsg.append(createPostMsg(meeting))
    for msg in postMsg:
        sendPost(msg)
    cleanupFiles(when2meetFiles)
    return


main()
