#!python
# Copyright 2019 Vale
# parse vulcan map files using a DSL engine
# v1.0 04/2018 paulo.ernesto

import sys, os.path
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

import lark

#%import common.WS
#%import common.CNAME
mapfile_grammar = r'''
  WS: /[ \t\f\r\n]/+
  LCASE_LETTER: "a".."z"
  UCASE_LETTER: "A".."Z"
  LETTER: UCASE_LETTER | LCASE_LETTER
  WORD: LETTER+
  DIGIT: "0".."9"
  CNAME: ("_"|LETTER|DIGIT)+

  ?start: file

  ?value: definition
        | tab
        | pair
        | terminal

  file: value+ "END" "$FILE"
  COMMENT: /\*.*/
  definition: "BEGIN" "$DEF" CNAME value+ "END" "$DEF" CNAME
  tab: "BEGIN" "$TAB" CNAME value+ "END" "$TAB" CNAME
  ESCAPED_STRING: "'" ("\\'"|/[^']/)* "'"
  terminal: ESCAPED_STRING | CNAME
  pair: CNAME "=" [terminal]


  %ignore WS
  %ignore COMMENT
'''

class MapfileTransformer(lark.Transformer):
  pair = lambda self, _: [_[0].value, _[1]]
  definition = lambda self, _: [_[0].value, _[1:-1]]
  tab = lambda self, _: [_[0].value, _[1:-1]]
  file = dict
  terminal = lambda self, _: str.strip(_[0],"'")

def mapfile_parse(fp):
  parser = lark.Lark(mapfile_grammar, parser='lalr', transformer=MapfileTransformer())
  with open(fp) as f:
    return(parser.parse(f.read()))
  return({})

class VulcanScd(object):

  def __init__(self, fp, v_def = None, v_tab = None):
    self._parse = mapfile_parse(fp)
    
    self._device_color = None
    if 'DEVICE_COLOUR' in self._parse:
      self._device_color = self._parse['DEVICE_COLOUR'][0][1]

    self._def = None
    self._tab = None
    self._one = 0
    if v_def is not None:
      if v_def in self._parse:
        self._def = self._parse[v_def]
      
      if v_tab is not None:
        v_tab = str(v_tab).upper()
        self._tab = dict(self._def)
        if v_tab in self._tab:
          self._tab = self._tab[v_tab]
          for i in range(len(self._tab)):
            if self._tab[i].isnumeric():
              self._one = i
              break
        else:
          self._tab = None
          print("legend",v_tab,"not found")

  def get_index(self, key):
    if self._def is None or self._tab is None:
      return(None)
    c = None

    if isinstance(self._tab, dict):
      pass
    else:
      # alpha mode
      if self._tab[0][0] == '@' or self._tab[-1] == 'ALPHA':
        for i in range(self._one, len(self._tab), 2):
          if i + 1 < len(self._tab) and self._tab[i+1].upper() == str(key).upper():
            c = int(self._tab[i])
            break
      #numeric mode
      else:
        for i in range(self._one, len(self._tab),3):
          if i + 1 < len(self._tab) and float(key) >= float(self._tab[i+1]) and float(key) < float(self._tab[i+2]):
            c = int(self._tab[i])
            break

    return c    

  def index_to_rgb(self, c, alpha = False):
    rgb = [0.0,0.0,0.0,1.0]
    if c is not None and self._device_color is not None:
      for i in range(0,len(self._device_color),4):
        if int(self._device_color[i]) == c:
          rgb = [float(self._device_color[_]) / 15.0 for _ in (i+1, i+3, i+2)] + [1.0]

    if alpha:
      return(rgb)

    return rgb[0:3]

  def get_rgb(self, key, alpha = False):
    return self.index_to_rgb(self.get_index(key), alpha)

  def palete_missing(self):
    return self._device_color is None

  def legend_missing(self):
    return self._tab is None

  __getitem__ = get_rgb

# NOTE: lark %import does not work inside a pyz so we have to hardcopy
arch_d_grammar = r'''
  _WS: /[ \t\f\r\n]/+
  LCASE_LETTER: "a".."z"
  UCASE_LETTER: "A".."Z"
  LETTER: UCASE_LETTER | LCASE_LETTER
  WORD: LETTER+
  DIGIT: "0".."9"
  CNAME: ("_"|LETTER|DIGIT)+
  WS_INLINE: (" "|/\t/)+
  SIGNED_NUMBER: ["+"|"-"] NUMBER
  INT: DIGIT+
  CR : /\r/
  LF : /\n/
  _NEWLINE: (CR? LF)+
  DECIMAL: INT "." INT? | "." INT
  SIGNED_INT: ["+"|"-"] INT
  _EXP: ("e"|"E") SIGNED_INT
  FLOAT: INT _EXP | DECIMAL _EXP?
  NUMBER: FLOAT | INT

  %ignore WS_INLINE

  CVALUE: /.+/
  
  WSCHAR: (" "|"_"|"+"|"-"|":"|LETTER|SIGNED_NUMBER)
  WSDATA: WSCHAR+
  _END: "End:" WSDATA _NEWLINE
  file: magic layer
  magic: CNAME _NEWLINE
  layer: "Layer:" _WS* CNAME WSDATA _NEWLINE polhed+ _END
  polhed: "POLHED:" CNAME WSDATA _NEWLINE pair+ _END
  pair: CNAME ":" WSDATA _NEWLINE
 
'''
                              

class ArchTransformer(lark.Transformer):
  file = tuple
  layer = tuple
  CNAME = str
  WSDATA = str
  polhed = tuple
  pair = tuple

def arch_d_parse(fp):
  print(fp)
  parser = lark.Lark(arch_d_grammar, parser='lalr', transformer=ArchTransformer(), start="file")
  with open(fp) as f:
    return parser.parse(f.read())
  return {}

def pd_load_arch(fp):
  import pandas as pd
  df = []
  layer = '0'
  raw_tree = arch_d_parse(fp)
  #print(raw_tree)
  l_name, l_prop, *l_data = raw_tree[1]
  oid = 0
  dfd = []
  for d in l_data:
    p_name, p_prop, *p_data = d
    pid = 0
    for t in p_data:
      if t[0] == 'Point':
        xyz = t[1].split()
        dfd.append([l_name, p_name, oid, pid] + xyz[:4])
        pid += 1
    oid += 1

  return pd.DataFrame(dfd, columns=['layer', 'name', 'oid', 'pid', 't', 'x', 'y', 'z'])

if __name__ == '__main__':
  import sys
  if len(sys.argv) > 1:
    print(pd_load_arch(sys.argv[1]))

