#!/usr/bin/env python
# -*- coding: utf-8 -*-

# werpp.py: Calculates WER and paints the edition operations
# Copyright (C) 2011 Nicolás Serrano Martínez-Santos <nserrano@iti.upv.es>
# Contributors: Guillem Gasco
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


import codecs
import re
from random import shuffle
from sys import argv,stderr,stdout
from optparse import OptionParser

#awk style dictionary
class D(dict):
  def __getitem__(self, i):
    if i not in self: self[i] = 0
    return dict.__getitem__(self, i)

class color:
  d={}; RESET_SEQ=""
  def __init__(self,c):
    if c == True:
      self.d['K']="\033[0;30m"    # black
      self.d['R']="\033[0;31m"    # red
      self.d['G']="\033[0;32m"    # green
      self.d['Y']="\033[0;33m"    # yellow
      self.d['B']="\033[0;34m"    # blue
      self.d['M']="\033[0;35m"    # magenta
      self.d['C']="\033[0;36m"    # cyan
      self.d['W']="\033[0;37m"    # white
      self.RESET_SEQ = "\033[0m"
    else:
      self.d['K']="["
      self.d['R']="["
      self.d['G']="["
      self.d['Y']="["
      self.d['B']="["
      self.d['M']="["
      self.d['C']="["
      self.d['W']="["
      self.RESET_SEQ = "]"

  def c_string(self,color,string):
    return self.d[color]+string+self.RESET_SEQ



def lev_changes(str1, str2, i_cost, d_cost, d_sub,vocab):
  d={}; sub={};
  for i in range(len(str1)+1):
    d[i]=dict()
    d[i][0]=i
    sub[i]={}
    sub[i][0]="D"
  for i in range(len(str2)+1):
    d[0][i] = i
    sub[0][i]="I"
  for i in range(1, len(str1)+1):
    for j in range(1, len(str2)+1):
      if d[i][j-1]+i_cost < d[i-1][j]+d_cost and d[i][j-1] < d[i-1][j-1]+(not str1[i-1] == str2[j-1])*d_sub:
        if (str2[j-1] in vocab) or vocab=={}:
          sub[i][j] = "I";
        else:
          sub[i][j] = "O"; #Oov insertion
      elif d[i-1][j]+d_cost < d[i][j-1]+i_cost and d[i-1][j] < d[i-1][j-1]+(not str1[i-1] == str2[j-1])*d_sub:
        sub[i][j] = "D";
      else:
        if str1[i-1] == str2[j-1]:
          sub[i][j] = "E";
        else:
          if (str2[j-1] in vocab) or vocab=={}:
            sub[i][j] = "S";
          else:
            sub[i][j] = "A"; #Oov Substitution
      d[i][j] = min(d[i][j-1]+i_cost, d[i-1][j]+d_cost, d[i-1][j-1]+(not str1[i-1] == str2[j-1])*d_sub)

  i=len(str1); j=len(str2); path=[]
  while(i > 0 or j > 0):
    path.append([sub[i][j],i-1,j-1])
    if(sub[i][j] == "I" or sub[i][j] == "O"):
      j-=1
    elif(sub[i][j] == "D"):
      i-=1
    else:
      j-=1; i-=1;
  path.reverse()
  return path;

def calculate_statistics(rec_file,ref_file,vocab,options):
  subs={}; subs_counts=D(); subs_all = 0
  ins=D(); ins_all = 0
  dels=D(); dels_all = 0
  join_symbol="#"
  colors=color(options.color)
  error_segment = [0]*(options.segments)
  oovSubs=0
  oovIns=0
  oovs = 0
  ref_count=0

  for i in rec_file.readlines():
    j = ref_file.readline()

    w_i = i.split()
    w_j = j.split()

    ref_count+= len(w_j)

    changes = lev_changes(w_i,w_j,1,1,1,vocab)

    if options.v == True:
      stdout.write("[II] ")
    for i in changes:
      [edition, rec_p, ref_p] = i
      rec = "" if edition == 'I' else w_i[rec_p] #avoid rec_p -1
      ref = w_j[ref_p]

      #color the operations
      if options.v == True:
        if edition == 'S':
          stdout.write("%s " %(colors.c_string("B",rec+join_symbol+ref).encode("utf-8")))
        elif edition == 'A':
          stdout.write("%s " %(colors.c_string("Y",rec+join_symbol+ref).encode("utf-8")))
        elif edition == 'I':
          stdout.write("%s " %(colors.c_string("G",ref).encode("utf-8")))
        elif edition == 'D':
          stdout.write("%s " %(colors.c_string("R",rec).encode("utf-8")))
        elif edition == 'O':
          stdout.write("%s " %(colors.c_string("Y",ref).encode("utf-8")))
        else:
          stdout.write("%s " %ref.encode("utf-8"))


      #count the segment where the errors occur
      if edition != 'E':
        error_segment[ref_p*options.segments/len(w_j)]+=1
        if options.vocab != None:
          if ref not in vocab:
            oovs+=1

      #count events in dictionaries
      if edition == 'S' or edition == 'A':
        subs_all+=1
        if edition == 'A':
          oovSubs+=1
        if ref not in subs:
          subs[ref]={}
        if rec not in subs[ref]:
          subs[ref][rec] = 1
        else:
          subs[ref][rec]+=1
        subs_counts[ref]+=1

      elif edition == 'I' or edition == 'O':
        if edition == 'O':
          oovIns+=1
        ins_all+=1
        ins[ref]+=1
      elif edition == 'D':
        dels_all+=1
        dels[rec]+=1

    if options.v == True:
      stdout.write("\n")

  stdout.write("WER: %.2f (Ins: %d Dels: %d Subs: %d Ref: %d)" \
      %(float(subs_all+ins_all+dels_all)/ref_count*100,ins_all,dels_all,subs_all,ref_count))
  if options.vocab != None:
   # stdout.write(" OOVs: %.2f%%" %(float(oovs)/ref_count*100))
    stdout.write(" OOVs: %.2f%%" %(float(oovSubs+oovIns)/ref_count*100))
    stdout.write(" OOVsSubs: %.2f%%" %(float(oovSubs)/subs_all*100))
    stdout.write(" OOVsIns: %.2f%%" %(float(oovIns)/ins_all*100))
  stdout.write("\n")

  if options.segments > 1:
    stdout.write("----------------------------------\nErrors in segment\n----------------------------------\n")
    total = sum(error_segment)
    for i in range(options.segments):
      stdout.write("%.2f " %(float(error_segment[i])/total*100))
    stdout.write("\n")

  if options.n > 0:
    stdout.write("----------------------------------\nWer due to words words\n----------------------------------\n")
    events=[]
    for i in subs:
      for j in subs[i]:
        events.append([subs[i][j],['S',i,j]])
    for i in ins:
      events.append([ins[i],['I',i]])
    for i in dels:
      events.append([dels[i],['D',i]])

    events.sort(); acc=0
    for i in range(len(events)-1,len(events)-1-options.n,-1):
      [n, e] = events[i]
      s=""
      if 'S' in e:
        s=colors.c_string("B",e[2]+join_symbol+e[1])
      elif 'I' in e:
        s=colors.c_string("G",e[1])
      elif 'D' in e:
        s=colors.c_string("R",e[1])
      acc+=n
      stdout.write("[Worst-%.2d] %.4f%% %.4f%% - %s\n" %(len(events)-1-i+1, float(n)/ref_count*100,float(acc)/ref_count*100, s.encode("utf-8")))

def main():
  cmd_parser = OptionParser(usage="usage: %prog [options] recognized_file reference_file")
  cmd_parser.add_option('-v',
      action="store_true",dest="v",
      help='Verbose power on!')
  cmd_parser.add_option('-n', '--worst-events',
     action="store", type="int", dest="n", default=0, help='Words words to print')
  cmd_parser.add_option('-s', '--error-segments',
     action="store", type="int", dest="segments", default=1, help='Number of error segments')
  cmd_parser.add_option('-c', '--colors',
      action="store_true",dest="color",
      help='Color the output')
  cmd_parser.add_option('-O', '--vocab',
     action="store", type="string", dest="vocab", default=None, help='Vocabulary to count OOVs')

  cmd_parser.parse_args(argv)
  (opts, args)= cmd_parser.parse_args()

  vocab = {}
  if opts.vocab != None:
    f = codecs.open(opts.vocab,"r","utf-8")
    for i in f.readlines():
      for j in i.split():
        if j not in vocab:
          vocab[j]=1

  if len(args) != 2:
    cmd_parser.print_help()
    exit(1)

  rec_file = codecs.open(args[0],"r","utf-8")
  ref_file = codecs.open(args[1],"r","utf-8")

  calculate_statistics(rec_file,ref_file,vocab,opts)

if __name__ == "__main__":
  main()

