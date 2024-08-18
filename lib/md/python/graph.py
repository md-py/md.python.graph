import typing


# Metadata
__author__ = 'https://md.land/md'
__version__ = '1.0.0'
__all__ = (
    # Metadata
    '__author__',
    '__version__',
    # Types
    'NodeType',
    'GraphType',
    'GraphPathType',
    'TopologicalSortType',
    # Exceptions
    'GraphExceptionInterface',
    'TopologicalSortException',
    # Contract
    'TopologicalSortInterface',
    # Implementation
    'topological_sort_ascending',
    'topological_sort_descending',
    'AscendingTopologicalSort',
    'DescendingTopologicalSort',
)

# Types
NodeType = typing.TypeVar('NodeType', bound=typing.Hashable)
GraphType = typing.Mapping[NodeType, typing.Collection[NodeType]]
GraphPathType = typing.Iterable[NodeType]
TopologicalSortType = typing.Callable[[GraphType], typing.Iterable[NodeType]]


# Exception
class GraphExceptionInterface:
    pass


class TopologicalSortException(RuntimeError, GraphExceptionInterface):
    CYCLE_DETECTED = 1

    def __init__(self, *args, code: int = 0, graph: GraphType = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code = code
        self.graph = graph

    @classmethod
    def as_cycle_detected(class_, graph: GraphType = None) -> 'TopologicalSortException':
        return class_(
            'Unable to perform topological sort, graph contains a cycle',
            code=class_.CYCLE_DETECTED,
            graph=graph
        )


# Contract
class TopologicalSortInterface:
    def sort(self, graph: GraphType) -> typing.Iterable[NodeType]:
        """
        Performs graph topological sorting and returns sequence of nodes
        :param graph: Generic graph structure represented by Mapping of Hashable nodes
        :returns: Iterable of sorted nodes
        """
        raise NotImplementedError


# Implementation
def topological_sort_ascending(graph: GraphType) -> typing.Iterable[NodeType]:
    """
    Performs graph topological sorting and returns sequence of nodes (from the bottom)

    :param graph: Generic graph structure represented by Mapping of Hashable nodes
    :returns: Iterable of sorted nodes
    :raises TopologicalSortException: If graph contains a cycle
    """
    if len(graph) == 0:
        return

    # 1. Normalize graph: convert collection to set
    normalized_graph: typing.Dict[NodeType, typing.Set[NodeType]] = {}
    for node, related_node_collection in graph.items():
        normalized_graph[node] = set(related_node_collection)

    leave_node_set = set()

    # 2. Search for nodes which are not explicitly defined as an empty graph
    for related_node_set in normalized_graph.values():
        for related_node in related_node_set:
            if related_node in normalized_graph:
                continue
            leave_node_set.add(related_node)

    while True:
        for node, related_node_set in normalized_graph.items():
            if len(related_node_set) == 0:
                leave_node_set.add(node)

        if not leave_node_set:
            break

        try:
            yield from sorted(leave_node_set)
        except TypeError:
            yield from leave_node_set

        for node, related_node_set in list(normalized_graph.items()):
            if node in leave_node_set:
                del normalized_graph[node]
                continue
            normalized_graph[node] -= leave_node_set
        leave_node_set = set()

    if len(normalized_graph) != 0:
        raise TopologicalSortException.as_cycle_detected(graph=normalized_graph)


def topological_sort_descending(
    graph: GraphType,
    initial_node: typing.Iterable[NodeType] = None
) -> typing.Iterable[NodeType]:
    """
    Performs graph topological sorting and returns sequence of nodes (from the top)

    Warning: This function does not check cycles in graph.

    Notice: This function does not require graph to be completed,
            when leaf node represented as empty graph (no relations).

    :param graph: Generic graph structure represented by Mapping of Hashable nodes
    :param initial_node:  Node which defines subtree of graph, to sort to
    :returns: Iterable of sorted nodes
    """

    if len(graph) == 0:
        return

    node_list = initial_node or graph.keys()   # node may be not present even as reference
    visited_node_set: typing.Set[NodeType] = set()

    for node in node_list:
        if node in visited_node_set:
            continue

        pending_node_stack = [node]
        while pending_node_stack:
            pending_node = pending_node_stack.pop()
            visited_node_set.add(pending_node)

            if pending_node not in graph:
                yield pending_node
                continue

            for related_node in graph[pending_node]:
                if related_node not in visited_node_set:
                    pending_node_stack.append(pending_node)
                    pending_node_stack.append(related_node)
                    break
            else:
                yield pending_node


def get_paths(graph: GraphType, include_subtree: bool = False) -> typing.Tuple[
    typing.List[GraphPathType],  # path list without cycle
    typing.List[GraphPathType],  # path list with cycle
]:
    """
    Returns two-sized tuple of graph paths list:
    first list contains paths without a cycle in graph,
    second list contains paths with a cycle in graph

    :param graph: Graph to scan
    :param include_subtree: When true, returns paths lists for graph subtree nodes
    """
    if len(graph) == 0:
        return [], []

    # 1. Build path list for each node in graph, determine elder nodes in graph
    topological_sorted_graph: typing.List[NodeType] = list(topological_sort_descending(graph=graph))

    node_path_map: typing.Dict[NodeType, typing.List[typing.List[NodeType]]] = {}
    cyclic_node_path_map: typing.Dict[NodeType, typing.List[typing.List[NodeType]]] = {}
    elder_node_heap: typing.List[NodeType] = []

    for node in topological_sorted_graph:
        if node not in graph or len(graph[node]) == 0:  # e.g. `graph={1: {2}}; node=2`
            continue  # leaf node cannot have path

        elder_node_heap.insert(0, node)
        node_path_map[node] = list()
        for child in graph[node]:
            if child in elder_node_heap:
                elder_node_heap.remove(child)

            for child_path in node_path_map.get(child, [[child]]):
                if node in child_path:
                    if node not in cyclic_node_path_map:
                        cyclic_node_path_map[node] = []
                    cyclic_node_path_map[node].append([node] + child_path[:child_path.index(node) + 1])
                    continue

                if child in cyclic_node_path_map:
                    node_path_map[node].append([node, child])
                    continue

                node_path_map[node].append([node] + child_path)
            assert len(node_path_map) > 0

    # 2. Build result
    node_list = elder_node_heap
    if include_subtree:
        node_list = node_path_map.keys()

    path_list: typing.List[GraphPathType] = []
    cycle_path_list = []

    for root_node in node_list:
        path_list.extend(node_path_map[root_node])

    for cycle_path in cyclic_node_path_map.values():
        cycle_path_list.extend(cycle_path)

    return path_list, cycle_path_list


class AscendingTopologicalSort(TopologicalSortInterface, typing.Generic[NodeType]):
    def sort(self, graph: GraphType) -> typing.Iterable[NodeType]:
        return topological_sort_ascending(graph=graph)


class DescendingTopologicalSort(TopologicalSortInterface, typing.Generic[NodeType]):
    def sort(self, graph: GraphType) -> typing.Iterable[NodeType]:
        return topological_sort_descending(graph=graph)
