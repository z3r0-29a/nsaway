#
# Author: TheZero <io@thezero.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtGui, QtCore
import os, sys
import signal
import zmq
from os.path import join
from utils import get_icon_path, ZMQ_SOCK

class Listener(QtCore.QObject):
    message = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        # Socket to talk to server
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect (ZMQ_SOCK)
        self.socket.setsockopt(zmq.SUBSCRIBE, '')

        self.running = True

    def loop(self):
        while self.running:
            string = self.socket.recv()
            self.message.emit(string)

class SystemTrayIcon(QtGui.QSystemTrayIcon):

  def __init__(self, icon, parent=None):
    QtGui.QSystemTrayIcon.__init__(self, icon, parent)
    menu = QtGui.QMenu(parent)
    changeicon = menu.addAction("Reset Status")
    exitAction = menu.addAction("Exit")
    self.setContextMenu(menu)
    exitAction.triggered.connect(quit)
    changeicon.triggered.connect(self.reset_icon)
    self.thread = QtCore.QThread()
    self.listener = Listener()
    self.listener.moveToThread(self.thread)

    self.thread.started.connect(self.listener.loop)
    self.listener.message.connect(self.signal_received)

    QtCore.QTimer.singleShot(0, self.thread.start)

  def signal_received(self, message):
    if message == 'True':
        update_tray_icon(self,'alert')
    else:
        update_tray_icon(self,'good')

  def closeEvent(self, event):
    self.listener.running = False
    self.thread.quit()
    self.thread.wait()

  def reset_icon(self):
    update_tray_icon(self,'good')

def quit():
  QtGui.qApp.quit()
  os.kill(os.getppid(), signal.SIGTERM)

def update_tray_icon(tray,status):
  # status can only be (good, alert)
  tray.setIcon(QtGui.QIcon(get_icon_path(status+".ico")))

def tray():
  app = QtGui.QApplication(['NSAway'])
  style = app.style()
  ico = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_FileIcon))
  w = QtGui.QWidget()

  trayIcon = SystemTrayIcon(ico, w)
  trayIcon.show()
  trayIcon.setIcon(QtGui.QIcon(get_icon_path("good.ico")))

  sys.exit(app.exec_())