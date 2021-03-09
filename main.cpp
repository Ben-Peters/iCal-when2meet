#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main(int argc, char** argv) {
    char* filePath = "./calendar.ics";
    ifstream iCal;
    if (argc == 1)
        filePath = argv[0];
    cout << filePath << endl;
    iCal.open(filePath,ios::in);
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
