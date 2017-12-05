from PyQt5 import QtWidgets
import sys

from gui.ArtistPlaylistWidget import ArtistPlaylistWidget


app = QtWidgets.QApplication(sys.argv)
window = ArtistPlaylistWidget()
window.setWindowTitle("Генерация плейлиста")
window.resize(300, 700)
window.show()
sys.exit(app.exec_())