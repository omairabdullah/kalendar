Kalendar
========
A KDE plasmoid with Kontact integration

Details
=======

It is a plasmoid implemented using KDE's plasma widget library and PyQt. The main task of the widget is to 
display event and todo information from Kontact. Kontact is the KDE4 Calendaring and Personal Information Management software.

Input-Output
------------
The widget resides on the desktop and is typically started automatically when the user logs in. It displays the current date 
in the calendar and the event information for the day. The user can select any date by either clicking on it in the calendar
or typing it in. The events for the selected day along with their respective times are then displayed.

The user can also input an event to add to Kontact.

The are two basic use cases:

  1. The user selects a date. The widget displays the event and todo information for that day along with the times when the events occur.
  2. The user adds a new event to the currently selected date. This is done by typing a description of the event and selecting its time.

When the user clicks the 'Add Event' button, the event is added to Kontact. Further details of the event can be edited from Kontact.

Install
=======

This application requires Python and PyQt to be installed in addition to KDE 4. In addition, the Vobject module is needed.
Kontact is expected to be installed along with the Akonadi Compatibility Bridge.

To install it, go to the directory called Kalendar. Then run the following command:

$ plasmapkg -i .

The plasmoid is then installed on your system. You can add it to your desktop in the usual way in KDE.
Alternately, you can run it by typing:

$ plasmoidviewer kalendar


You can also uninstall the plasmoid by running:

$ plasmapkg -r kalendar

