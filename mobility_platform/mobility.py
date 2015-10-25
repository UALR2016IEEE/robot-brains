from time import time
from utils import Point3


class Base:
    def __init__(self, profile, cid: str=None):
        self._current_task = None
        self.profile = profile

    @property
    def current_task(self):
        return self._current_task

    @current_task.setter
    def current_task(self, task):
        self._current_task = task
        self.sendtask()

    def exec_arc(self, r: float, angle: float=None, arcl: float=None):
        nang = angle is not None
        narc = arcl is not None
        if nang and narc:
            raise ValueError('Cannot pass both angle and arc length')
        elif not (nang or narc):
            raise ValueError('Need either angle or arc length')

        if narc:
            angle = self._calc_angle(nang)

        self.current_task = Action(self.profile, arc_angle=angle, line=r)
        return self.current_task

    def _calc_angle(self, arcl: float) -> float:
        pass
        #return angle

    def exec_line(self, l: float):
        self.current_task = Action(self.profile, line=l)
        return self.current_task

    def rotate(self, angle: float):
        self.current_task = Action(self.profile, angle=angle)
        return self.current_task

    def exec_suicide_line(self, line: float, angle: float):
        self.current_task = Action(self.profile, angle=angle, line=line)
        return self.current_task

    def exec_suicide_arc(self, r: float, end_angle: float, arc_angle: float=None, arc_len: float=None):
        nang = arc_angle is not None
        narc = arc_len is not None
        if nang and narc:
            raise ValueError('Cannot pass both angle and arc length')
        elif not (nang or narc):
            raise ValueError('Need either angle or arc length')

        if narc:
            arc_angle = self._calc_angle(nang)
        self.current_task = Action(self.profile, r, end_angle, arc_angle)

    def sendtask(self):
        self.current_task.start()


class Mobility:
    pass


class Action:
    def __init__(self, profile: dict, line: float=None, angle: float=None, arc_angle: float=None):
        """
        passing only line is a line action
        passing only angle is rotate
        passing angle and line is rotate and move in a line
        passing arcangle will make line the radius of the arc and angle will be the final angle
        """
        argmask = [_ is None for _ in (line, angle, arc_angle)]
        argtable = [(False, True, True),
                    (True, False, True),
                    (False, False, True), ]
        if argmask in argtable:
            raise ValueError("Cannot pass in {}".format(
                " ".join(a for a, m in zip(('line', 'angle', 'arc angle'), argmask) if m)))

        self.start_time = None

        self.line = line
        self.angle = angle
        self.arc_angle = arc_angle

        self.profile = profile

    def start(self):
        self.start_time = time()

    def estimate_progress(self):
        return 0

    def estimate_position(self, initial_pos: Point3):
        prog = self.estimate_progress()
