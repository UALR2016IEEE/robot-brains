import types


class Base:
    def __init__(self, cid: str=None):
        pass

    def exec_arc(self, r: float, angle: float=None, arcl: float=None):
        nang = angle is not None
        narc = arcl is not None
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



