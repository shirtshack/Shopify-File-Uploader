import os
from utilities.files import FileUtilities


def function():
    while True:
        print("Please enter the parent folder you wish to create the upload file for:")
        parent_folder = input()
        print("parent_folder: " + parent_folder)
        if os.path.exists(parent_folder):
            FileUtilities.run_for_parent_folder(parent_folder)
            print("File created!")
        else:
            print("Path does not exist!")


if __name__ == "__main__":
    function()