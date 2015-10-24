import asyncio
from mobility_platform.mobility import Base as mobbase
from navigation_platform.controller import Base as navbase
from utils import Point3


class Controller:
    def __init__(self, nav_plat: navbase, mob_plat: mobbase):
        self.nav = nav_plat
        self.mob = mob_plat
        self.local = Point3()
        self.tasks = [self.fsm]
        self.loop = asyncio.get_event_loop()

    def start(self):
        self.loop.run_until_complete(map(asyncio.ensure_future, self.tasks))

    async def fsm(self):
        local = await self.nav.get_pos()
        action = self.mob.exec_line(5)
        self.nav.set_action(action)


