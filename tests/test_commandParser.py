import pytest
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
# Include paths for module search
sys.path.insert(0, parentdir)

from commandParser import splitCommand

def test_splitCommand():
  text = ":cmd"
  command = splitCommand(text)
  assert command == "cmd"

  text = ":cmd arg1 arg2"
  command = splitCommand(text)
  assert command == "cmd arg1 arg2"

def test_splitCommand_fail():
  text = "!cmd"
  command = splitCommand(text)
  assert command is None

  text = "cmd arg1"
  command = splitCommand(text)
  assert command is None

  text = "no:"
  command = splitCommand(text)
  assert command is None

  text = ""
  command = splitCommand(text)
  assert command is None
  