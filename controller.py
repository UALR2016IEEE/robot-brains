import asyncio
from mobility_platform.mobility import Base as mob_base
from navigation_platform.controller import Base as nav_base
from utils import Point3
import math
import simulate.controller
import status_io
from utils.conversion import Conversion

POINT_THREASHOLD = (0, 0)
ANGLE_THREASHOLD = 3


class Controller:
    def __init__(self, nav_plat: nav_base, mob_plat: mob_base, stat_lock):
        self.nav = nav_plat
        self.mob = mob_plat
        self.stat_lock = stat_lock
        self.local = Point3()
        self.tasks = [self.fsm()]
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        self.pos_intention = Point3()
        self.conversion = Conversion()

    def start(self):
        self.loop.run_until_complete(asyncio.wait(map(asyncio.ensure_future, self.tasks)))

    async def pilot(self, dest):
        delta_vector = self.nav.position - dest
        self.pos_intention = self.mob.exec_line(delta_vector)
        await self.audit_motion()

    @staticmethod
    def renderer(navigation_platform):
        print("Initializing Renderer")
        io = status_io.IOHandler()
        print('Binding to renderer')
        io.start('144.167.148.247', 9998)
        sim_controller = simulate.controller.Controller(navigation_platform.get_position())
        sim_controller.init_grid()
        io.send_data(('full-simulation', None))
        io.send_data(('grid-colors', sim_controller.grid.get_pygame_grid()))
        io.send_data(('robot-pos', navigation_platform.get_position()))
        print("Renderer Ready")
        yield
        while True:
            lidar, estimated_velocity = yield
            io.send_data(('robot-pos', navigation_platform.get_position()))
            io.send_data(('lidar-points', (navigation_platform.get_position(), lidar)))

    async def fsm(self):
        action = self.mob.exec_line(Point3(0, 1000))
        #self.nav.set_action(action)
        self.nav.add_component('lidar render', self.renderer)
        self.nav.start()
        from status_platform import status
        status.lock = self.stat_lock
        action.set_status(status)
        while True:
            #position = await self.nav.get_pos()
            pass
            #print(action.estimate_progress())
        # await self.audit_motion()

        # action_list = [self.mob.exec_line(self.conversion.pix2mm(625)), self.mob.rotate(-90), self.mob.exec_line(self.conversion.pix2mm(250)), self.mob.rotate(90), self.mob.exec_line(self.conversion.pix2mm(125)), self.mob.rotate(-90), self.mob.exec_line(self.conversion.pix2mm(100))]
        # for action in action_list:
        #     self.nav.set_action(action)

    async def audit_motion(self):
        actual_pos = self.nav.position
        delta = Point3(abs(actual - intent) for intent, actual in zip(self.pos_intention[None], actual_pos[None]))
        if delta.x > POINT_THREASHOLD or delta.y > POINT_THREASHOLD:
            action = self.mob.exec_line(delta)
            self.nav.set_action(action)
            await asyncio.Condition().wait_for(action.complete, timeout=0.5)
        if delta.r > ANGLE_THREASHOLD:
            action = self.mob.rotate(delta.r)
            self.nav.set_action(action)
            await asyncio.Condition().wait_for(action.complete, timeout=0.5)
