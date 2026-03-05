from pynini.lib import rewrite
from rules import *
import pynini as pn
'''

 takes latin input and output latin
 build a translator between the two lol

 '''

ascii_table = pn.SymbolTable()
ascii_table.add_symbol("<eps>", 0)
for i in range(12, 128):
  ascii_table.add_symbol(chr(i), i)

def draw(fst, symbol_table=ascii_table):
  fst.set_input_symbols(symbol_table)
  fst.set_output_symbols(symbol_table)
  return fst  




'''
 Sound marker used in Sanskrit writing. It usually sounds like a soft “h” breath after a vowel.
 It changes to 's', 'r', 'o', or disappears entirely depending on the word that follows it in a sentence.
 '''
# gender rule

