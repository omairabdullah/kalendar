# -*- coding: utf-8 -*-
# A KDE 4 Plasmoid with Kontact integration
#
# Copyright(C) 2009 by Omair Mohammed Abdullah <omairabdullah@gmail.com>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation; either version 2, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
#
# You should have received a copy of the GNU Library General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
import vobject, datetime
import os
from calendar_ui import *
 
class Kalendar(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
        
	self.calendar = None
        self.currentTimezone = "Local"
	self.reloadInterval = 120000 	# 2 minutes
	self.parsedCal = None
	self.calFileChanged = False
	self.year = 2009
	self.month = 9
	self.day = 30
 
    def init(self):
	"""
	Initializes the plasmoid and displays the UI. Signals for the KPushButton and the KDatePicker are connected
	to respective handlers. A timer is added to reload the file every 2 minutes.
	"""
        self.setHasConfigurationInterface(False)
        self.resize(12, 12)
        self.setAspectRatioMode(Plasma.Square)
 
        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)
        self.theme.resize(self.size())

        self.dialog = None
        self.calendarUi = Ui_calendar()
	self.eventIcon = QIcon("event.svg")
	self.todoIcon = QIcon("todo.png")
        
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self.applet)
        self.setLayout(self.layout)
	
	self.showCalendar()
	
	#set a timer to reload the file every 2 minutes.
	self.timer = QTimer(self)
	self.timer.setInterval(self.reloadInterval)
	self.connect(self.timer, SIGNAL("timeout()"), self.reloadCalFile)
	self.timer.start()
	
	# slots for selection changed, add btn clicked,
	self.connect(self.calendarUi.kpushbutton, SIGNAL("clicked()"), self.addTask)
	self.connect(self.calendarUi.kdatepicker, SIGNAL("dateChanged(const QDate &)"), self.showEvents)

 
    def showCalendar(self):
	"""
	Displays the UI. It also marks the dates when one or more events in a different colour
	by calling the parseCalFile() and showEvents() methods in succession.
	"""
        if self.calendar is None:
            self.calendar = Plasma.Dialog()
            self.calendarUi.setupUi(self.calendar)
            self.calendar.setWindowFlags(Qt.Widget)
            self.calendar.adjustSize()

            data = self.dataEngine("time").query(self.currentTimezone)
	    self.calendarUi.kdatepicker.date = data[QString("Date")].toDate()
	    self.calendarUi.timeEdit.setTime(data[QString("Time")].toTime())
	    
            self.calendar.show()
	    self.parseCalFile()
	    self.showEvents(data[QString("Date")].toDate())
	    self.calendarUi.klineedit.selectAll()
	    
    def parseCalFile(self):
	"""
	Reads the iCalendar file from the user's home directory and parses it.
	The parsed data is stored in self.parsedCal.
	The dates when one or more events/todo items occur are highlighted.
	"""
	try:
	    home = os.environ["HOME"]
	    fh = open(home + '/.kde/share/apps/korganizer/std.ics', 'r')
	    calFile = fh.read()
	    fh.close()
	    self.parsedCal = vobject.readOne(calFile)
	    print "INFO: File std.ics parsed"
	except IOError:
	    print "ERROR: Unable to read file."

	# For highlighting dates on which events occur
	dateTable = self.calendarUi.kdatepicker.dateTable()
	for ev in self.parsedCal.vevent_list:
	    dateEvent = QDate(ev.dtstart.value.year, ev.dtstart.value.month, ev.dtstart.value.day)
	    dateTable.setCustomDatePainting(dateEvent, QColor("red"))
	for ev in self.parsedCal.vtodo_list:
	    dateEvent = QDate(ev.due.value.year, ev.due.value.month, ev.due.value.day)
	    dateTable.setCustomDatePainting(dateEvent, QColor("teal"))

    def saveCalFile(self):
	"""
	Saves the parsed data back to the iCalendar file
	"""
	try:
	    home = os.environ["HOME"]
	    fh = open(home + '/.kde/share/apps/korganizer/std.ics', 'w')
	    calStream = self.parsedCal.serialize()
	    fh.write(calStream)
	    fh.close()
	    self.calFileChanged = False
	except IOError:
	    print "ERROR: Unable to write to file."
	
    def reloadCalFile(self):
	"""
	Reloads the file every time the timer times out. This is so that any changes
	to the file are updated in the plasmoid.
	"""
	if self.calFileChanged == True:
	    self.saveCalFile()
	self.parseCalFile()
	
	self.timer.setInterval(self.reloadInterval)
	self.timer.start()

	print "INFO: std.ics reloaded"
    

    def addTask(self):
	"""
	Adds the task entered by the user to the parsed representation (parsedCal) and then saves the file.
	"""
	year = self.year
	month = self.month
	day = self.day
	
	timeSelected = self.calendarUi.timeEdit.time()
	hour = timeSelected.hour()
	minute = timeSelected.minute()
	
	task = str(self.calendarUi.klineedit.text())
	self.calendarUi.klineedit.selectAll()
	
	todo = self.parsedCal.add('vevent')
	todo.add('summary').value = task
	start = todo.add('dtstart')
	start.value = datetime.datetime(year, month, day, hour, minute, tzinfo=None)
	
	self.calFileChanged = True
	self.saveCalfile()
	print "INFO: Added new event to Kontact."
	
	  

    @pyqtSignature("showEvents(const QDate &)")
    def showEvents(self, date):
	"""
	When selection of KDatePicker is changed or at time of initialization of the plasmoid,
	get the events of that particular day from parsedCal and insert them to
	the listbox 
	
	@type date: QDate
	@param date: The selected date returned by the dateSelected() signal.
	"""
	# self.year,month,date contain the currently selected date
	self.year = date.year()
	self.month = date.month()
	self.day = date.day()	
	
	atStr = ""
	tree = self.calendarUi.klistwidget
	tree.clear()

	# Populate the listwidget
	for ev in self.parsedCal.vevent_list:
	    dateEvent = QDate(ev.dtstart.value.year, ev.dtstart.value.month, ev.dtstart.value.day)
	    try:
		# adding time of event
		atStr = "  at " + str(ev.dtstart.value.hour) + ev.dtstart.value.strftime(":%M %p") 
	    except Exception:
		# Sometimes Kontact has a slightly different representation
		pass
	    if dateEvent == date:
		#add this in the list box
		event = QListWidgetItem(ev.summary.value+atStr)
		event.setIcon(self.eventIcon)
		tree.addItem(event)
	for ev in self.parsedCal.vtodo_list:
	    dateEvent = QDate(ev.due.value.year, ev.due.value.month, ev.due.value.day)
	    try:
		atStr = "  at " + str(ev.due.value.hour) + ev.due.value.strftime(":%M %p") 
	    except Exception:
		pass
	    if dateEvent == date:
		#add this in the list box
		todo = QListWidgetItem(ev.summary.value+atStr)
		todo.setIcon(self.todoIcon)
		tree.addItem(todo)
	    
def CreateApplet(parent):
    return Kalendar(parent)
    
    
# Test cases & TODO
# =================
# check for selection changed ---> listwidget correctly populated
# check for adding of event from widget
# check for adding event in Kontact and seeing in widget


# ADDITIONAL = config interface
# add slot for klineedit click such that
# the text of klineedit is selected when it is clicked. have to subclass klineedit to add slot for gained focus etc.
# ? create new dialog for add event and add more attribs to it. Maybe controlled by config?

# change name?
# configuration interface....
# - set calendar system - Hijri, hebrew, Jalali etc
# - display todo or events or both
#
# slot for return key of klineedit pressed - to add event
