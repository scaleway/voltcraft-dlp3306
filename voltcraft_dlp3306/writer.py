# Copyright 2024 Scaleway
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import abc
import os


class Writer(abc.ABC):
    def close(self):
        raise NotImplementedError()

    def size(self):
        raise NotImplementedError()

    def write(self):
        raise NotImplementedError()

    @classmethod
    def get_writer_from_extension(cls, filename: str) -> "Writer":
        if filename is not None and filename.endswith(".csv"):
            return CSVWriter(filename)
        else:
            return ConsoleWriter()


class ConsoleWriter(Writer):
    def __init__(self):
        self.__filename = "console"

    def close(self):
        pass

    def size(self):
        return 0

    def write(self, *args):
        print(args)

    def filename(self):
        return self.__filename


class CSVWriter(Writer):
    def __init__(self, filepath: str):
        self.__filename = filepath
        self.__fp = open(self.__filename, "w", encoding="utf8")
        self.__writer = csv.writer(
            self.__fp,
            delimiter=",",
            quotechar='"',
            lineterminator="\n",
        )

    def close(self):
        self.__fp.close()

    def write(self, *args):
        self.__writer.writerow(args)

    def size(self):
        return os.path.getsize(self.__filename)

    def filename(self):
        return self.__filename
