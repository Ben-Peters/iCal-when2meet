import vobject
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC

iCalStream = open("calendar.ics").read()

cal = vobject.readOne(iCalStream)
for event in cal.contents.get('vevent'):
    try:
        print('Summary: ', event.summary.valueRepr())
        print('Description: ', event.description.valueRepr())
        print('Time (as a datetime object): ', event.dtstart.value)
        print('-------------------------------------------------\n')

    except AttributeError:
        print("Something wasn't found")
