import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-a', '--add', help="use this flag to add more when2meet links", action="store_true")
args = parser.parse_args()


def getWhen2Meets():
    links = []
    while True:
        link = input("Please enter the link to a when2meet: ")
        if link == 'quit' or link == 'exit' or link == 'q':
            break
        links.append(link)
    return links


if args.add:
    when2meetLinks = getWhen2Meets()
    urls = open('.data/urls.txt', 'a')
    for when2meetLink in when2meetLinks:
        urls.write(when2meetLink + '\n')
    urls.close()
else:
    try:
        os.mkdir('.tmp')
        os.mkdir('.data')
        userName = input("Please enter your name: ")
        password = input("Please enter your password (press enter for no password): ")
        iCalLink = input("Please enter the link to iCalendar you would like to use: ")
        when2meetLinks = getWhen2Meets()
        creds = open('.data/creds.jpg', 'w')
        creds.write(userName + '\n')
        creds.write(password + '\n')
        urls = open('.data/urls.txt', 'w')
        urls.write(iCalLink + '\n')
        for when2meetLink in when2meetLinks:
            urls.write(when2meetLink + '\n')
        creds.close()
        urls.close()
    except OSError as error:
        print(error)



