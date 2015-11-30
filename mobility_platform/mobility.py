import time
from utils import Point3
import math
import copy


class Base:
    def __init__(self, profile, cid: str=None):
        self._current_task = None
        self.profile = profile
        self.velocity = Point3()
        self.acceleration = Point3()

    @property
    def current_task(self):
        return self._current_task

    @current_task.setter
    def current_task(self, task):
        self._current_task = task
        self.sendtask()

    def exec_arc(self, r: float, angle: float=None, arcl: float=None, stop=True):
        nang = angle is not None
        narc = arcl is not None
        if nang and narc:
            raise ValueError('Cannot pass both angle and arc length')
        elif not (nang or narc):
            raise ValueError('Need either angle or arc length')

        if narc:
            angle = self._calc_angle(nang)

        self.current_task = Action(self.profile, self.velocity, self.acceleration, arc_angle=angle, line=r, stop=stop)
        return self.current_task

    def _calc_angle(self, arcl: float) -> float:
        pass
        # return angle

    def exec_line(self, l: float, stop=True):
        self.current_task = Action(self.profile, self.velocity, self.acceleration, line=l, stop=stop)
        return self.current_task

    def rotate(self, angle: float, stop=True):
        self.current_task = Action(self.profile, self.velocity, self.acceleration, angle=angle, stop=stop)
        return self.current_task

    def exec_suicide_line(self, line: float, angle: float, stop=True):
        self.current_task = Action(self.profile, self.velocity, self.acceleration, angle=angle, line=line, stop=stop)
        return self.current_task

    def exec_suicide_arc(self, r: float, end_angle: float, arc_angle: float=None, arc_len: float=None, stop=True):
        nang = arc_angle is not None
        narc = arc_len is not None
        if nang and narc:
            raise ValueError('Cannot pass both angle and arc length')
        elif not (nang or narc):
            raise ValueError('Need either angle or arc length')

        if narc:
            arc_angle = self._calc_angle(nang)
        self.current_task = Action(self.profile, self.velocity, self.acceleration, r, end_angle, arc_angle, stop=stop)

    def sendtask(self):
        self.current_task.start()


class Mobility:
    pass


class Action:
    def __init__(self, profile: dict, velocity, acceleration, line: float=None, angle: float=None, arc_angle: float=None, stop=True):
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
        self.current_time = None

        self.line = line
        self.angle = angle
        self.arc_angle = arc_angle
        self.stop = stop  # whether to stop at the end of an action or not

        self.velocity = velocity
        self.acceleration = acceleration

        self.profile = profile

        self.started = False
        self.complete = False
        self.distance = 0

    def start(self):
        if not self.started:
            self.started = True
            self.start_time = time.time()
            self.current_time = self.start_time

    def estimate_progress(self):
        return 0

    def estimate(self, initial_pos: Point3):
        # prog = self.estimate_progress()

        print('intiial', initial_pos)

        if not self.started:
            return 0, 0, 0

        dt = time.time() - self.current_time

        if self.line:

            self.velocity.x = self.profile['top lateral speed'] * math.cos(initial_pos.r)
            self.velocity.y = self.profile['top lateral speed'] * math.sin(initial_pos.r)
            self.distance += self.velocity.magnitude() * dt

            if self.distance > self.line:
                print('distance reached')
                if self.stop:
                    print('zeroing velocity')
                    self.velocity.x = 0
                    self.velocity.y = 0
                self.complete = True

        self.current_time = time.time()

        return self.velocity.magnitude() * 2.54 * dt, self.velocity.r, dt
