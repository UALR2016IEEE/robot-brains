import asyncio
from mobility_platform.mobility import Base as mob_base
from navigation_platform.controller import Base as nav_base
from utils import Point3
import math
from utils.conversion import Conversion

POINT_THREASHOLD = (0, 0)
ANGLE_THREASHOLD = 3


class Controller:
    def __init__(self, nav_plat: nav_base, mob_plat: mob_base):
        self.nav = nav_plat
        self.mob = mob_plat
        self.local = Point3()
        self.tasks = [self.fsm()]
        self.loop = asyncio.get_event_loop()
        self.pos_intention = Point3()
        self.conversion = Conversion()

    def start(self):
        self.loop.run_until_complete(asyncio.wait(map(asyncio.ensure_future, self.tasks)))

    async def pilot(self, dest):
        delta_vector = self.nav.position - dest
        self.pos_intention = self.mob.exec_line(delta_vector)
        await self.audit_motion()

    async def fsm(self):
        # action = self.mob.exec_line(50)
        # self.nav.set_action(action)
        # await self.pilot(action)

        action_list = [self.mob.exec_line(self.conversion.pix2mm(625)), self.mob.rotate(-90), self.mob.exec_line(self.conversion.pix2mm(250)), self.mob.rotate(90), self.mob.exec_line(self.conversion.pix2mm(125)), self.mob.rotate(-90), self.mob.exec_line(self.conversion.pix2mm(100))]
        for action in action_list:
            self.nav.set_action(action)

    async def audit_motion(self):
        actual_pos = self.nav.position
        delta = Point3(abs(actual - intent) for intent, actual in zip(self.pos_intention[None], actual_pos[None]))
        self.mob.exec_line(delta)
        self.mob.rotate(delta.r)
