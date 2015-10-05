__author__ = 'StaticVOiDance'

import navigation_platform.navigation as navlib


class _Base(navlib._Base):
    def __init__(self, navigation: navlib._Base):
        self.nav = navigation

    def start(self):
        pass

    def stop(self):
        pass
