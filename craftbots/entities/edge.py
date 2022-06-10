import math as m


class Edge:
    def __init__(self, world, node_a, node_b):
        """
        An edge between two nodes in the craftbots simulation. An actor can travel along this to get from node to node.
        :param world: The world in which the edge exists
        :param node_a: One of the nodes that the edge connects
        :param node_b: One of the nodes that the edge connects
        """
        self.node_a = node_a
        self.node_b = node_b
        self.world = world

        self.id = world.get_new_id()
        self.node_a.append_edge(self)
        self.node_b.append_edge(self)

        self.fields = {"node_a": self.node_a.id, "node_b": self.node_b.id, "id": self.id, "length": self.length()}

    def __eq__(self, other):
        if isinstance(other, Edge):
            if self.node_a == other.node_a and self.node_b == other.node_b or self.node_a == other.node_b and\
                    self.node_b == other.node_a:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Edge" + self.__str__()

    def __str__(self):
        return "(" + str(self.node_a) + ", " + str(self.node_b) + ", " + str(self.length()) + ")"

    def length(self):
        """
        Returns the length of the edge for an actor to travel along it
        :return: the length of the edge
        """
        return m.ceil(m.dist((self.node_a.x, self.node_a.y), (self.node_b.x, self.node_b.y)))

    def connects(self, node):
        """
        Returns true if the edge connects to the node provided, and False otherwise
        :param node: the node to be checked
        :return: True if the node is connected to the edge, and false otherwise.
        """
        return node == self.node_a or node == self.node_b

    def get_other_node(self, node):
        """
        Returns the other node the edge connects to if the node provided is connected to the edge.
        :param node: The node that the edge should be checked against
        :return: The other node the edge connects if the passed in node is connected to the edge. Otherwise returns None
        """
        if self.node_a == node:
            return self.node_b
        elif self.node_b == node:
            return self.node_a
        return None

    def get_other_node_id(self, node_id):
        """
        Returns the id of the other node the edge is connected to. Used in the fields of the edge to be called in the
        API by the agent
        :param node_id: the id of the node to be compared against the node
        :return: the id of the other node the edge connects if the passed in node is connected to the edge. Otherwise
        returns None
        """
        node = self.world.get_by_id(node_id, entity_type="Node")
        if node is not None:
            other_node = self.get_other_node(node)
            if other_node is not None:
                return other_node.id
        return None
