import math
import time
import types
import statistics
from abc import abstractmethod
import multiprocessing

from utils import Point3, Point2
from hardware.robo_claw import RoboClaw

class Base(object):
    def __init__(self, profile, cid: str = None):
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
        # self.send_task()

    def exec_arc(self, r: float, angle: float = None, arc_len: float = None, stop=True):
        nang = angle is not None
        narc = arc_len is not None
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

    def exec_line(self, vector: Point3, stop=True):
        self.current_task = Action(self.profile, self.velocity, self.acceleration, line=vector, stop=stop)
        return self.current_task

    def rotate(self, angle: float, stop=True):
        self.current_task = Action(self.profile, self.velocity, self.acceleration, angle=angle, stop=stop)
        return self.current_task

    def exec_suicide_line(self, line: float, angle: float, stop=True):
        self.current_task = Action(self.profile, self.velocity, self.acceleration, angle=angle, line=line, stop=stop)
        return self.current_task

    def exec_suicide_arc(self, r: float, end_angle: float, arc_angle: float = None, arc_len: float = None, stop=True):
        nang = arc_angle is not None
        narc = arc_len is not None
        if nang and narc:
            raise ValueError('Cannot pass both angle and arc length')
        elif not (nang or narc):
            raise ValueError('Need either angle or arc length')

        if narc:
            arc_angle = self._calc_angle(nang)
        self.current_task = Action(self.profile, self.velocity, self.acceleration, r, end_angle, arc_angle, stop=stop)

    def arm(self, enable=True):
        pass

    def disarm(self):
        self.arm(False)

    def send_task(self):
        self.current_task.start()

ENCODER_TICKS = 979.62
WHEEL_BASE = 245 
WHEEL_ARC = math.pi * WHEEL_BASE
WHEEL_DIAMETER = 36
WHEEL_CIRCUMFERENCE = math.pi*WHEEL_DIAMETER
ROTATION_PER_TICK = WHEEL_CIRCUMFERENCE / ENCODER_TICKS

def ticks_to_mm(ticks):
    return ROTATION_PER_TICK * ticks

def mm_to_ticks(mm):
    return int(mm / ROTATION_PER_TICK)

def shift_vector_angle(y, x, shift):
    angle = math.atan2(y, x)
    mag = math.sqrt(x**2 + y**2)
    s_angle = shift + angle
    x_new = mag * math.cos(s_angle)
    y_new = mag * math.sin(s_angle)
    return y_new, x_new


class Mobility(Base):
    def __init__(self, *args, **kwargs):
        super(Mobility, self).__init__(*args, **kwargs)

    def exec_line(self, vector: Point3, stop=True):
        return LineAction(target=vector)

    def rotate(self, angle, stop=True):
        return RotateAction(target=angle)

    def stop(self, enable=True):
        with self.m1.port.lock:
            self.m1.set_motor_pwm(0, 0)
            self.m2.set_motor_pwm(0, 0)


class Action(object):
    def __init__(self, profile: dict, velocity, acceleration, line: Point2 = None, angle: float = None,
                 arc_angle: float = None, stop=True):
        """
        passing only line is a line action
        passing only angle is rotate
        passing angle and line is rotate and move in a line
        passing arc_angle will make line the radius of the arc and angle will be the final angle
        """
        arg_mask = [_ is None for _ in (line, angle, arc_angle)]
        arg_table = [(False, True, True),
                     (True, False, True),
                     (False, False, True), ]
        if arg_mask in arg_table:
            raise ValueError(
                    "Cannot pass in {}".format(
                        " ".join(a for a, m in zip(('line', 'angle', 'arc angle'), arg_mask) if m)))

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
        self.total_angle = 0
        self.d_xy = 0
        self.d_theta = 0

    def start(self):
        if not self.started:
            self.started = True
            self.start_time = time.time()
            self.current_time = self.start_time

    def estimate_progress(self):
        return 0

    def estimate(self, initial_pos: Point3):
        if not self.started:
            return 0, 0, 0

        dt = time.time() - self.current_time
        self.d_xy = 0
        self.d_theta = 0

        if self.angle:
            self.velocity.x = 0
            self.velocity.y = 0
            if self.angle > 0:
                # turning CW
                self.velocity.r = self.profile['top rotational speed']
            else:
                # turning CCW
                self.velocity.r = -self.profile['top rotational speed']

            factor = 1.0
            if abs(self.angle) - abs(self.total_angle) < abs(self.velocity.r) / 2.0:
                factor = 0.3

            self.d_theta = self.velocity.r * dt * factor
            self.total_angle += self.d_theta

            if abs(self.total_angle) > abs(self.angle):
                print('angle reached')
                if self.stop:
                    print('zeroing angular velocity')
                    self.velocity.r = 0
                self.complete = True

        if self.line:
            # velocities need to be in mm/s
            self.velocity.x = (self.profile['top lateral speed'] * 1000) * math.cos(initial_pos.r)
            self.velocity.y = (self.profile['top lateral speed'] * 1000) * math.sin(initial_pos.r)
            self.velocity.r = 0

            self.distance += self.velocity.magnitude() * dt

            if self.distance > self.line:
                print('distance reached')
                if self.stop:
                    print('zeroing velocity')
                    self.velocity.x = 0
                    self.velocity.y = 0
                self.complete = True

            self.d_xy = self.velocity.magnitude() * dt

        self.current_time = time.time()

        return self.d_xy, self.d_theta, dt


class HardwareAction(object):
    def __init__(self, target):
        self.target = target
        self.complete = False
        self.timeout = 0

    def set_status(self, status):
        self.m1 = RoboClaw(status, 0x81)
        self.m2 = RoboClaw(status, 0x80)

    @abstractmethod
    def start(self):
        raise NotImplementedError

    def stop(self):
        self.m1.set_motor_pwm(0, 0)
        self.m2.set_motor_pwm(0, 0)

    @abstractmethod
    def estimate_progress(self):
        raise NotImplementedError


class LineAction(HardwareAction):
    def start(self):
        x_in_ticks = mm_to_ticks(self.target.x)
        y_in_ticks = mm_to_ticks(self.target.y)
        y_in_ticks, x_in_ticks = map(int, shift_vector_angle(y_in_ticks, x_in_ticks, math.pi / 4))
        speed = 3000
        with self.m1.port.lock:
            self.m1.set_motor_positions(
                8000,
                (speed, x_in_ticks),
                (speed, -x_in_ticks)
            )
            self.m2.set_motor_positions(
                8000,
                (speed, y_in_ticks),
                (speed, -y_in_ticks)
            )

    def estimate_progress(self):
        with self.m1.port.lock:
            m1a_pos, m1b_pos = self.m1.get_motor_positions()
            m2a_pos, m2b_pos = self.m2.get_motor_positions()
        actual_point = Point3(
            ticks_to_mm(statistics.mean((m2a_pos, -m2b_pos))),
            ticks_to_mm(statistics.mean((m1a_pos, -m1b_pos)))
        )
        actual_point_shifted = Point3(*shift_vector_angle(actual_point.y, actual_point.x, -math.pi/4))
        delta = Point3(*(abs(actual - intent) for intent, actual in zip(self.target[None], actual_point_shifted[None])))
        if self.timeout == 0 and all(d < 300 for d in delta):
            self.timeout = time.time()
        if self.timeout != 0:
            if time.time() - self.timeout > 2 or all(d < 2 for d in delta):
                self.complete = True
                self.stop()

        return actual_point_shifted


class RotateAction(HardwareAction):
    def start(self):
        wheel_arc = WHEEL_ARC * (self.target / (math.pi * 2))
        wheel_arc_in_ticks = -mm_to_ticks(wheel_arc)
        speed = 2000
        with self.m1.port.lock:
            self.m1.set_motor_positions(
                12000, (speed, wheel_arc_in_ticks), (speed, wheel_arc_in_ticks)
            )
            self.m2.set_motor_positions(
                12000, (speed, wheel_arc_in_ticks), (speed, wheel_arc_in_ticks)
            )

    def estimate_progress(self):
        with self.m1.port.lock:
            m1a_pos, m1b_pos = self.m1.get_motor_positions()
            m2a_pos, m2b_pos = self.m2.get_motor_positions()
        actual_ticks_arc = -ticks_to_mm(statistics.mean((m1a_pos, m1b_pos, m2a_pos, m2b_pos)))
        actual_angle = (actual_ticks_arc / WHEEL_ARC) * (math.pi * 2)
        delta = abs(actual_angle - self.target)
        if self.timeout == 0 and delta < math.pi / 24:
            self.timeout = time.time()
        if self.timeout != 0:
            if time.time() - self.timeout > 2 or delta < math.pi / 120:
                self.complete = True
                self.stop()
        return actual_angle


