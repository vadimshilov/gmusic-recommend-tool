# -*- coding: utf-8 -*-
import sys, traceback
from ApiProvider import ApiProvider
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from controller import RecommendationTool
from db.repository import ArtistRepository


class ArtistPlaylistWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.artistList = QtWidgets.QListView()
        self.set_list_model()
        self.createButton = QtWidgets.QPushButton("Создать Playlist")
        self.createButton.clicked.connect(self.create_playlist_clicked)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.artistList)
        self.vbox.addWidget(self.createButton)
        self.setLayout(self.vbox)


    def set_list_model(self):
        artists = ArtistRepository.find_all()
        self.artistMap = {artist.name: artist.id for artist in artists}
        self.artistModel = QtCore.QStringListModel(sorted(self.artistMap.keys()), self)
        self.artistList.setModel(self.artistModel)


    def create_playlist_clicked(self):
        try:
            index = self.artistList.currentIndex()
            if index is not None:
                api = ApiProvider.get_api()
                RecommendationTool.create_artist_playlist(api, self.artistMap[index.data()], True)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)


