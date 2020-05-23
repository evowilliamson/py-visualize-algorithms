from graphviz import Digraph
from pythonalgos.graph.vertex import Vertex
from os import path
from pythonalgos.util import path_tools as pt
from pythonvizalgos.util import video_tools as vt
from pythonalgos.graph.directed_graph import DirectedGraph
from pythonvizalgos.main_runners.graph.advisors.viz_tracing_advisor \
    import VizCyclicTracingAdvisor
import os


""" Module that defines a tracing class to be used for tracing of cyclic
algorithms in relation to directed graphs """


class VizCyclicTracing:
    """ Class that is accessed in a static way. It contains functions for
    tracing cyclic algorithms in relation to directed graphs

    states structure:

    [ {"some_state": {**args} ..., {"default": {**args} ]

    For example:
        vertex_states=[
                        {VizCyclicTracing.ACTIVATED:
                            {"fillcolor":"red", "style": "filled"}},
                        {VizCyclicTracing.IN_CYCLE:
                            {"fillcolor":"blue", "style": "filled"}},
                        {VizCyclicTracing.VISISTED:
                            {"fillcolor":"gray", "style": "filled"}}])

    VizCyclicTracing.ACTIVATED takes precedence over VizCyclicTracing.IN_CYCLE
    takes predecence over VizCyclicTracing.VISITED by definition of the list

    """

    tracing = False
    path: str
    directed_graph = None
    vertex_states = list()
    edge_states = list()

    IMAGE_NAME_PREFIX = "VIZ_TRACING_"
    DEFAULT = "default"
    IMAGE_TYPE = "png"
    DEFAULT_STATE = None

    ACTIVATED = "activated"
    IN_CYCLE = "in_cycle"
    VISISTED = "visited"
    DISABLED = "disabled"

    @staticmethod
    def enable(path, directed_graph, vertex_states=None,
               edge_states=None):
        """ Class method that initialises the tracing functionality

        Args:
            path: the path that will contain the generated trace images
            directed_graph(DirectedGraph): the directed graph
            vertex_states(list): a list of stated definitions (see class) for
                the vertices
            edge_states(list): a list of stated definitions (see class) for
                the edges

        """

        VizCyclicTracing.tracing = True
        VizCyclicTracing.path = path
        VizCyclicTracing.directed_graph = directed_graph
        VizCyclicTracing.vertex_states = vertex_states or\
            [{VizCyclicTracing.DEFAULT: VizCyclicTracing.DEFAULT_STATE}]
        VizCyclicTracing.edge_states = edge_states or\
            [{VizCyclicTracing.DEFAULT: VizCyclicTracing.DEFAULT_STATE}]
        VizCyclicTracing.snapshot_no = 1

    @staticmethod
    def disable():
        VizCyclicTracing.tracing = False

    @staticmethod
    def change_activated_vertex(directed_graph, vertex: Vertex):
        """ Function that sets the attribute "active" of the vertex to true.
        It deactivates all other vertices

        Args:
            directed_graph(DirectedGraph): directed graph object
            vertex(Vertex): the vertex to be activated
        """

        if not VizCyclicTracing.tracing:
            return
        else:
            VizCyclicTracing.set_status(
                directed_graph, vertex, VizCyclicTracing.ACTIVATED)
            for v in directed_graph.get_vertices():
                if str(v.get_label()) != str(vertex.get_label()):
                    VizCyclicTracing.reset_status(
                        directed_graph, v, VizCyclicTracing.ACTIVATED)

    @staticmethod
    def set_status(directed_graph, object, status):
        """ Function that tags the vertex as with the provided status

        Args:
            directed_graph(DirectedGraph): directed graph object
            object: the vertex of edge for which the status must be set
            status(str): the status to be set
        """

        if not VizCyclicTracing.tracing:
            return
        else:
            object.set_attr(status, True)

    @staticmethod
    def reset_status(directed_graph, object, status):
        """ Function that resets the status of the object

        Args:
            directed_graph(DirectedGraph): directed graph object
            object: the vertex of edge for which the status must be reset
            status(str): the status to be reset
        """

        if not VizCyclicTracing.tracing:
            return
        else:
            object.set_attr(status, False)

    @staticmethod
    def snapshot():
        """ Take a snapshot of the current directed graph

        Args:
            file_name(str): path and file for the file to be generated
            view_type(bool): True if the attached program for the file is to
                be started on

        """

        if not VizCyclicTracing.tracing:
            return
        else:
            graph = Digraph(format=VizCyclicTracing.IMAGE_TYPE)
            for vertex in VizCyclicTracing.directed_graph.get_vertices():
                found, default_state = False, None
                for state in VizCyclicTracing.vertex_states:
                    attr_name, attr_values = next(iter(state.items()))
                    if attr_name != VizCyclicTracing.DEFAULT and\
                            vertex.get_attr(attr_name):
                        graph.node(str(vertex.get_label()), label=None,
                                   _attributes=None, **attr_values)
                        found = True
                        break
                    elif attr_name == VizCyclicTracing.DEFAULT:
                        default_state = attr_values
                if not found:
                    graph.node(str(vertex.get_label()), default_state or
                               VizCyclicTracing.DEFAULT_STATE)

                for edge in vertex.get_edges():
                    found, default_state = False, None
                    for state in VizCyclicTracing.edge_states:
                        attr_name, attr_values = next(iter(state.items()))
                        if attr_name != VizCyclicTracing.DEFAULT and \
                                edge.get_attr(attr_name):
                            graph.edge(
                                str(edge.get_tail().get_label()),
                                str(edge.get_head().get_label()),
                                label=None, _attributes=None, **attr_values)
                            found = True
                            break
                        elif attr_name == VizCyclicTracing.DEFAULT:
                            default_state = attr_values
                    if not found:
                        graph.edge(
                            str(edge.get_tail().get_label()),
                            str(edge.get_head().get_label()))
            graph.render(path.join(
                VizCyclicTracing.path, VizCyclicTracing.IMAGE_NAME_PREFIX +
                ("{:04d}".format(VizCyclicTracing.snapshot_no))))
            VizCyclicTracing.snapshot_no += 1

    @staticmethod
    def execute(directed_graph: DirectedGraph, resource_path: str):
        """ Main function that takes a number of vertices (of a directed graph),
        invokes the cycle check functionality (which in turn creates the traced
        images), and converts the images to a video

        Args:
            vertices(dict): a dictionar with vertices and for each vertex its
                destination vertices
            resource_path: the path that should contain the generated resources
        """

        work_path = os.path.join(resource_path)
        pt.create_dir_in_user_home(work_path)
        VizCyclicTracing.enable(
            pt.get_dir_in_user_home(work_path),
            directed_graph,
            vertex_states=[
                        {VizCyclicTracing.ACTIVATED:
                            {"fillcolor": "red", "style": "filled"}},
                        {VizCyclicTracing.IN_CYCLE:
                            {"fillcolor": "blue", "style": "filled"}},
                        {VizCyclicTracing.VISISTED:
                            {"fillcolor": "gray", "style": "filled"}}],
            edge_states=[{VizCyclicTracing.DISABLED: {"color": "red"}}])
        directed_graph.is_cyclic(VizCyclicTracingAdvisor())
        vt.convert_images_to_video(pt.get_dir_in_user_home(work_path))
