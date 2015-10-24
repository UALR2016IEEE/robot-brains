import types
from time import time
from utils import Point3


class Base:
    def __init__(self, cid: str=None):
        self._current_task = Action()

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

        self.current_task = Action(angle=angle, arc=r)
        return self.current_task


    def _calc_angle(self, arcl: float) -> float:
        pass
        #return angle

    def exec_line(self, l: float):
        self.current_task = Action(line=l)
        return self.current_task

    def rotate(self, angle: float):
        self.current_task = Action(angle=angle)
        return self.current_task

    def exec_suicide(self, line:float, angle:float):
        self.current_task = Action(angle=angle, line=line)
        return self.current_task

    def sendtask(self):
        self.current_task.start()


class Mobility:
    pass


class Action:
    def __init__(self, line: float=None, angle: float=None, arc: float=None):
        argmask = [_ is None for _ in (line, angle, arc)]
        argtable = [(True, True, True),
                    (True, False, True),
                    (False, False, True), ]
        if argmask in argtable:
            raise ValueError("Cannot pass in {}".format(
                " ".join(a for a, m in zip(('line', 'angle', 'arc'), argmask) if m)))

        self.start_time = None

        self.line = line
        self.angle = angle
        self.arc = arc

    def start(self):
        self.start_time = time()

    def estimate_progress(self):
        pass

    def estimate_position(self, initial_pos: Point3):
        prog = self.estimate_progress()

