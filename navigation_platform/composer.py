from utils.data_structures import Point2
from utils.data_structures import Vertex
from utils.astar import astar
from utils.conversion import Conversion
import math


class Base(object):
    def __init__(self, render=False):
        self.points = {}
        self.init_graph()
        self.goal = None
        self.conversion = Conversion()

    def init_graph(self):
        # define primary points first
        self.points['yellow_drop'] = Vertex('yellow_drop', Point2(735, 145))
        self.points['red_drop'] = Vertex('red_drop', Point2(860, 810))
        self.points['victim_city_left'] = Vertex('victim_city_left', Point2(605, 85))
        self.points['victim_city_right'] = Vertex('victim_city_right', Point2(735, 875))
        self.points['victim_offroad_left_upper'] = Vertex('victim_offroad_left_upper', Point2(140, 65))
        self.points['victim_offroad_left_lower'] = Vertex('victim_offroad_left_lower', Point2(455, 85))
        self.points['victim_offroad_right_upper'] = Vertex('victim_offroad_right_upper', Point2(65, 775))
        self.points['victim_offroad_right_lower'] = Vertex('victim_offroad_right_lower', Point2(230, 895))

        # define connection points
        self.points['p1'] = Vertex('p1', Point2(60, 460))
        self.points['p2'] = Vertex('p2', Point2(480, 895))

        # wall 1
        self.points['wall_1_lower'] = Vertex('wall_1_lower', Point2(855, 190))
        self.points['wall_1_upper'] = Vertex('wall_1_upper', Point2(735, 190))

        # wall 2
        self.points['wall_2_lower'] = Vertex('wall_2_lower', Point2(710, 385))
        self.points['wall_2_upper'] = Vertex('wall_2_upper', Point2(615, 385))

        # wall 3
        self.points['wall_3_lower_left'] = Vertex('wall_3_lower_left', Point2(710, 435))
        self.points['wall_3_upper_left'] = Vertex('wall_3_upper_left', Point2(615, 435))
        self.points['wall_3_lower_right'] = Vertex('wall_3_lower_right', Point2(710, 735))
        self.points['wall_3_upper_right'] = Vertex('wall_3_upper_right', Point2(615, 735))

        # wall 4
        self.points['wall_4_lower'] = Vertex('wall_4_lower', Point2(710, 775))
        self.points['wall_4_upper'] = Vertex('wall_4_upper', Point2(615, 775))

        # wall 5
        self.points['wall_5_lower'] = Vertex('wall_5_lower', Point2(575, 385))
        self.points['wall_5_upper'] = Vertex('wall_5_upper', Point2(480, 385))

        # wall 6
        self.points['wall_6_lower'] = Vertex('wall_6_lower', Point2(575, 775))
        self.points['wall_6_upper'] = Vertex('wall_6_upper', Point2(480, 775))

        # then define edges - have to be defined two way
        self.points['yellow_drop'].edges.append(self.points['wall_1_lower'])
        self.points['wall_1_lower'].edges.append(self.points['yellow_drop'])

        self.points['yellow_drop'].edges.append(self.points['wall_1_upper'])
        self.points['wall_1_upper'].edges.append(self.points['yellow_drop'])

        self.points['red_drop'].edges.append(self.points['wall_1_lower'])
        self.points['wall_1_lower'].edges.append(self.points['red_drop'])

        self.points['wall_1_lower'].edges.append(self.points['wall_1_upper'])
        self.points['wall_1_upper'].edges.append(self.points['wall_1_upper'])

        self.points['wall_2_lower'].edges.append(self.points['wall_1_upper'])
        self.points['wall_1_upper'].edges.append(self.points['wall_2_lower'])

        self.points['wall_2_lower'].edges.append(self.points['wall_2_upper'])
        self.points['wall_2_upper'].edges.append(self.points['wall_2_lower'])
        
        self.points['wall_3_lower_left'].edges.append(self.points['wall_3_upper_left'])
        self.points['wall_3_upper_left'].edges.append(self.points['wall_3_lower_left'])
        self.points['wall_3_lower_right'].edges.append(self.points['wall_3_upper_right'])
        self.points['wall_3_upper_right'].edges.append(self.points['wall_3_lower_right'])
        
        self.points['wall_4_lower'].edges.append(self.points['wall_4_upper'])
        self.points['wall_4_upper'].edges.append(self.points['wall_4_lower'])
        
        self.points['wall_5_lower'].edges.append(self.points['wall_5_upper'])
        self.points['wall_5_upper'].edges.append(self.points['wall_5_lower'])
        
        self.points['wall_6_lower'].edges.append(self.points['wall_6_upper'])
        self.points['wall_6_upper'].edges.append(self.points['wall_6_lower'])

        self.points['wall_2_lower'].edges.append(self.points['wall_3_lower_left'])
        self.points['wall_3_lower_left'].edges.append(self.points['wall_2_lower'])
        self.points['wall_2_upper'].edges.append(self.points['wall_3_upper_left'])
        self.points['wall_3_upper_left'].edges.append(self.points['wall_2_upper'])

        self.points['wall_3_lower_left'].edges.append(self.points['wall_3_lower_right'])
        self.points['wall_3_lower_right'].edges.append(self.points['wall_3_lower_left'])
        self.points['wall_3_upper_right'].edges.append(self.points['wall_3_upper_left'])
        self.points['wall_3_upper_left'].edges.append(self.points['wall_3_upper_right'])

        self.points['victim_city_left'].edges.append(self.points['wall_2_upper'])
        self.points['wall_2_upper'].edges.append(self.points['victim_city_left'])

        self.points['victim_city_left'].edges.append(self.points['wall_5_lower'])
        self.points['wall_5_lower'].edges.append(self.points['victim_city_left'])

        self.points['wall_2_upper'].edges.append(self.points['wall_5_lower'])
        self.points['wall_5_lower'].edges.append(self.points['wall_2_upper'])

        self.points['wall_3_upper_left'].edges.append(self.points['wall_5_lower'])
        self.points['wall_5_lower'].edges.append(self.points['wall_3_upper_left'])

        self.points['wall_3_upper_right'].edges.append(self.points['wall_4_upper'])
        self.points['wall_4_upper'].edges.append(self.points['wall_3_upper_right'])

        self.points['wall_3_lower_right'].edges.append(self.points['wall_4_lower'])
        self.points['wall_4_lower'].edges.append(self.points['wall_3_lower_right'])

        self.points['victim_city_right'].edges.append(self.points['wall_3_lower_right'])
        self.points['wall_3_lower_right'].edges.append(self.points['victim_city_right'])

        self.points['victim_city_right'].edges.append(self.points['wall_4_lower'])
        self.points['wall_4_lower'].edges.append(self.points['victim_city_right'])

        self.points['wall_3_upper_right'].edges.append(self.points['wall_6_lower'])
        self.points['wall_6_lower'].edges.append(self.points['wall_3_upper_right'])

        self.points['wall_4_upper'].edges.append(self.points['wall_6_lower'])
        self.points['wall_6_lower'].edges.append(self.points['wall_4_upper'])

        self.points['wall_5_lower'].edges.append(self.points['wall_6_lower'])
        self.points['wall_6_lower'].edges.append(self.points['wall_5_lower'])

        self.points['wall_5_upper'].edges.append(self.points['wall_6_upper'])
        self.points['wall_6_upper'].edges.append(self.points['wall_5_upper'])

        self.points['victim_offroad_right_upper'].edges.append(self.points['victim_offroad_right_lower'])
        self.points['victim_offroad_right_lower'].edges.append(self.points['victim_offroad_right_upper'])

        self.points['victim_offroad_right_lower'].edges.append(self.points['p2'])
        self.points['p2'].edges.append(self.points['victim_offroad_right_lower'])

        self.points['p2'].edges.append(self.points['wall_6_upper'])
        self.points['wall_6_upper'].edges.append(self.points['p2'])

        self.points['wall_5_upper'].edges.append(self.points['victim_offroad_left_lower'])
        self.points['victim_offroad_left_lower'].edges.append(self.points['wall_5_upper'])

        self.points['victim_offroad_left_lower'].edges.append(self.points['p1'])
        self.points['p1'].edges.append(self.points['victim_offroad_left_lower'])

        self.points['victim_offroad_right_upper'].edges.append(self.points['p1'])
        self.points['p1'].edges.append(self.points['victim_offroad_right_upper'])

        self.points['victim_offroad_left_upper'].edges.append(self.points['p1'])
        self.points['p1'].edges.append(self.points['victim_offroad_left_upper'])

    @staticmethod
    def get_neighbors(v):
        return v.edges

    def is_goal(self, v):
        return self.goal == v.name

    @staticmethod
    def get_cost(v1, v2):
        return v1.point.distance(v2.point)

    def get_heuristic(self, v):
        return self.points[self.goal].point.distance(v.point)

    def find_path_from_current(self):
        pass

    @staticmethod
    def reduce_actions(actions):
        current = 0
        result = []
        while current != len(actions):
            if current != len(actions) - 1:
                if actions[current][0] != actions[current + 1][0]:
                    result.append(actions[current])
                    current += 1
                else:
                    tmp = actions[current]
                    while actions[current][0] == actions[current + 1][0] and current != len(actions):
                        tmp[1] += actions[current + 1][1]
                        current += 1
                    current += 1
                    result.append(tmp)
            else:
                # check if the last one is at the same angle
                if result[-1][0] == actions[-1][0]:
                    result[-1][1] += actions[-1][1]
                else:
                    result.append(actions[-1])
                break
        return result

    def find_path(self, v1, v2):
        self.goal = v2
        path = astar(self.points[v1], self.get_neighbors, self.is_goal, 0, self.get_cost, self.get_heuristic)
        path.insert(0, self.points[v1])
        actions = []
        for idx in range(len(path)):
            if idx != len(path) - 1:
                # print('name', path[idx].name, 'to', path[idx + 1].name, 'p1', path[idx].point, 'p2', path[idx + 1].point, 'angle', math.degrees(path[idx].point.get_angle_to(path[idx + 1].point)), 'dist', path[idx].point.distance(path[idx + 1].point))
                actions.append([math.degrees(path[idx].point.get_angle_to(path[idx + 1].point)), self.conversion.pix2mm(path[idx].point.distance(path[idx + 1].point))])
        reduced = self.reduce_actions(actions)
        return reduced


class Composer(Base):
    pass
