"""
AUTHOR: Hritik Soni

Description: Executable Module of the project

Pass this module to python without any arguments to run the program.


"""
import sys
from core import *

def main():
    app = QApplication(sys.argv) #This statement is used by all Qt applications
    print("Creating Primary Window Object")
    GUI = Window()
    print("Primary Window Object Created")
    sys.exit(app.exec_()) #Standard way of starting
    
    ### -FUTURE- The following code was intended to make the program run in both text and gui mode
    # USE_GUI = True
    # if len(sys.argv) > 1 and sys.argv[1] == "gui":
    #     USE_GUI = True
    # if USE_GUI:
    #     print("Creating Primary Window Object")
    #     GUI = Window()
    #     print("Primary Window Object Created")
    #     sys.exit(app.exec_())


if __name__ == '__main__':
    main()
