# TODO
#* SIGKILL instead of interrupt
# * Capture also stderr.
#* What does close_fds do and why buffer size is needed?
# * Why the second argument is needed for thread function?

import sys
import wx
import os
import signal
from subprocess import Popen, PIPE, STDOUT
from threading  import Thread

ON_POSIX = 'posix' in sys.builtin_module_names

class AccessibleRunner(wx.Frame):
  def __init__(self, parent, title):
    super(AccessibleRunner, self).__init__(parent, title = title)
    self.process = None
    
    self.Bind(wx.EVT_CLOSE, self.onWindowClose)
    
    self.addWidgets()
    self.Centre()
    self.Show()
    self.Fit()
    
  def onWindowClose(self, event):
    if self.process:
      self.interrupt()
    self.Destroy()

  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    
    # Command textbox
    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    hbox1.Add(self.commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.commandTextbox = wx.TextCtrl(self.panel)
    hbox1.Add(self.commandTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Arguments textbox
    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.argsLabel = wx.StaticText(self.panel, -1, 'Arguments') 
    hbox2.Add(self.argsLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.argsTextbox = wx.TextCtrl(self.panel)
    hbox2.Add(self.argsTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory textbox
    hbox3 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.dirLabel = wx.StaticText(self.panel, -1, 'Working directory') 
    hbox3.Add(self.dirLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.dirTextbox = wx.TextCtrl(self.panel)
    hbox3.Add(self.dirTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Run button
    hbox4 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.runButton = wx.Button(self.panel, label = 'Run')
    self.runButton.Bind(wx.EVT_BUTTON, self.onRunButtonClick)
    hbox4.Add(self.runButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.interruptButton = wx.Button(self.panel, label = 'Interrupt')
    self.interruptButton.Bind(wx.EVT_BUTTON, self.onInterruptButtonClick)
    hbox4.Add(self.interruptButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)    
    
    # Output textbox
    hbox5 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.outputLabel = wx.StaticText(self.panel, -1, "Output") 
    hbox5.Add(self.outputLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.outputTextbox = wx.TextCtrl(self.panel, size = (400, 150), style = wx.TE_MULTILINE | wx.TE_READONLY)
    hbox5.Add(self.outputTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Clear button
    hbox6 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.clearButton = wx.Button(self.panel, label = 'Clear output')
    self.clearButton.Bind(wx.EVT_BUTTON, self.onClearButtonClick)
    hbox6.Add(self.clearButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Copy button
    self.copyButton = wx.Button(self.panel, label = 'Copy output')
    self.copyButton.Bind(wx.EVT_BUTTON, self.onCopyButtonClick)
    hbox6.Add(self.copyButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(hbox1)
    vbox.Add(hbox2)
    vbox.Add(hbox3)
    vbox.Add(hbox4)
    vbox.Add(hbox5)
    vbox.Add(hbox6)
      
    self.panel.SetSizer(vbox)
    
  def onRunButtonClick(self, event):
    if self.process is None:
      command = self.commandTextbox.GetValue()
      args = self.argsTextbox.GetValue()
      dir = self.dirTextbox.GetValue()
      if dir == '':
        dir = None
      
      try:
        self.process = Popen([command, args], shell = True, stdout = PIPE, bufsize = 1, close_fds = ON_POSIX, cwd = dir)
      except NotADirectoryError:
        self.setOutput('Error: The directory does not exist.\n', True)//
      else:        
        thread = Thread(target=self.fetchOutput, args = (self.process.stdout, None))
        thread.daemon = True # Thread dies with the program
        thread.start()
    
  def onInterruptButtonClick(self, event):
    if self.process:
      Popen(['taskkill', '/pid', str(self.process.pid), '/t'], shell = True) # This does not work either
      #self.interrupt()
    
  def onClearButtonClick(self, event):
    self.setOutput('')
    
  def onCopyButtonClick(self, event):
    if not wx.TheClipboard.IsOpened():
      wx.TheClipboard.Open()
      data = wx.TextDataObject()
      data.SetText(self.textbox.GetValue())
      wx.TheClipboard.SetData(data)
      wx.TheClipboard.Close()
      
  def setOutput(self, text, append = False):
    prevText = self.outputTextbox.GetValue() if append else ''
    self.outputTextbox.SetValue(prevText + text)
      
  def interrupt(self):
    os.kill(self.process.pid, signal.CTRL_C_EVENT)
    self.process = None
      
  def fetchOutput(self, out, arg):
    for line in iter(out.readline,  b''):
      self.setOutput(line.decode('utf-8'), True)
    out.close()
    self.process = None
    
def main():
  app = wx.App()
  AccessibleRunner(None, title='AccessibleRunner')
  app.MainLoop()

main()
