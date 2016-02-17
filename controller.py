import asyncio
from mobility_platform.mobility import Base as mob_base
from navigation_platform.controller import Base as nav_base
from utils import Point3


class Controller:
    def __init__(self, nav_plat: nav_base, mob_plat: mob_base):
        self.nav = nav_plat
        self.mob = mob_plat
        self.local = Point3()
        self.tasks = [self.fsm()]
        self.loop = asyncio.get_event_loop()

    def start(self):
        self.loop.run_until_complete(asyncio.wait(map(asyncio.ensure_future, self.tasks)))

    async def fsm(self):
        action = self.mob.exec_line(50)
        self.nav.set_action(action)
        while not self.nav.actions.empty():
            await asyncio.sleep(0.05)
