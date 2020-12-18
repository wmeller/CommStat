'''CommStat is a desktop app designed to be deployed to GeTac USMC computers for tracking communications check times at last sent posreps.
Required Functions:
1. Easy update comm check time by unit, by unit.
2. View and edit history of comm checks and posreps.
3. Export to a text file for sending over the air.
4. Export to excel for viewing.
5. Edit units, nets, on the fly.
W Eller, C Cimmarrusti'''

from PyQt5 import QtApplication, QLabel
app = QtApplication([])
label = QLabel('Hello World!')
label.show()
app.exec_()
