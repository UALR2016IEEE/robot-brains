__author__ = 'StaticVOiDance'


import types

class _Base:
    def __init__(self, cid: str=None):
        pass

    def exec_arc(self, r: float, angle: float=None, arcl: float=None):
        nang = not angle is None
        narc = not arcl is None
        if nang and narc:
            raise ValueError('Cannot pass both angle and arc length')
        elif not (nang or narc):
            raise ValueError('Need either angle or arc length')

        if narc:
            angle = self._calc_angle(nang)


    def _calc_angle(self, arcl: float) -> float:
        return angle

    def exec_line(self, l: float):
        pass

    def rotate(self, angle: float):
        pass



