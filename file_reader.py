#!/usr/bin/env python
# -*- coding: utf-8 -*-

# file_reader.py: Efficient file reader with file support in python
# Copyright (C) 2011 Nicolás Serrano Martínez-Santos <nserrano@iti.upv.es>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sys import stderr
import zipfile
import codecs

class FileReader:
  def __init__(self,f,buffer_size=1024):
    #open file
    self.f = f
    self.buffer_size = 1024
    self.buff_readed = 0
    self.buff_len = 0

  def read_buff(self):
    self.buff = self.f.read(self.buffer_size)

    self.buff_len = len(self.buff)
    self.buff_readed = 0

    if self.buff_len == 0:
      return False
    else:
      return True

  def readline(self):
    s = ""
    while 1:
      while self.buff_readed < self.buff_len:
        if self.buff[self.buff_readed] == '\n':
          self.buff_readed+=1
          return s
        else:
          s+=self.buff[self.buff_readed]
          self.buff_readed+=1

      if not self.read_buff():
        return None

  def close(self):
    self.f.close()
