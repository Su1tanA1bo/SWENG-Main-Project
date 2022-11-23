##*************************************************************************
#   data structure that represents a file
#
#   @author	 Jamie Taylor
#   @Creation Date: 23/11/2022
##*************************************************************************

from pathlib import Path


class FileContents:

    def __init__(self, name, contents):
        self.name = name
        self.contents = contents
        self.extension = Path(name).suffix

    def to_dict(self):
        return {
            "name": self.name,
            "contents": self.contents
        }

    def __repr__(self):
        return f"Name: {self.name}\n" \
               f"Contents: {self.contents}\n"
