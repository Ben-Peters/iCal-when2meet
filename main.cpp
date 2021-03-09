#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main(int argc, char** argv) {
    string filePath = "./calendar.ics";
    ifstream iCal;
    if (argc == 2)
        filePath = argv[1];
    cout << filePath << endl;
    iCal.open(filePath);
    if(iCal.is_open()) {
        string line;
        while (getline(iCal, line)) {
            cout << line << endl;
        }
    }
    else{
        cout << "Unable to open file" << endl;
        return -1;
    }
    iCal.close();
    return 0;
}
