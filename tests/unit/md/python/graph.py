import typing

import unittest.mock
import pytest

import md.python.graph


__all__ = (
    'TestAscendingTopologicalSort',
    'TestDescendingTopologicalSort',
    'TestGetPathList',
    'TestAscendingTopologicalSortImplementation',
    'TestDescendingTopologicalSortImplementation',
)


# internal utility:
def dataset(data_set: typing.Dict[str, typing.Dict[str, typing.Any]]) -> pytest.mark.parametrize:
    argnames = []
    argvalues = []
    ids = []
    for id_, argument_map in data_set.items():
        if not argnames:
            argnames = list(argument_map.keys())
        argvalues.append([argument_map[argument_value] for argument_value in argnames])
        ids.append(id_)
    return pytest.mark.parametrize(argnames=argnames, argvalues=argvalues, ids=ids)


# Tests:
class TestAscendingTopologicalSort:
    @dataset({
        'empty graph': dict(
            graph={},
            expected_linearized_sorted_graph=[],
        ),
        'only leaves': dict(
            graph={
                1: [],
                2: [],
                3: [],
            },
            expected_linearized_sorted_graph=[1, 2, 3],
        ),
        'only leaves, discovered': dict(
            graph={
                1: [],
                3: [2],
            },
            expected_linearized_sorted_graph=[1, 2, 3],
        ),
        'node single relation': dict(
            graph={
                4: {1},
                5: {2},
                6: {3},
            },
            expected_linearized_sorted_graph=[1, 2, 3, 4, 5, 6],
        ),
        'few levels depth graph': dict(
            graph={
                7: {5, 4},
                5: {3, 2},
                8: {5, 1},
                6: {5},
                4: {3, 1},
            },
            expected_linearized_sorted_graph=[1, 2, 3, 4, 5, 6, 7, 8],
        )
    })
    def test_acyclic_graph(
        self,
        graph: md.python.graph.GraphType,
        expected_linearized_sorted_graph: typing.Sequence[md.python.graph.NodeType]
    ) -> None:
        # act
        linearized_sorted_graph = list(md.python.graph.topological_sort_ascending(graph=graph))

        # assert
        assert linearized_sorted_graph == expected_linearized_sorted_graph

    @dataset({
        'direct related node cycle': dict(
            graph={1: {2}, 2: {1}},
            normalized_graph={1: {2}, 2: {1}}
        ),
        'transitive related node cycle': dict(
            graph={1: {2}, 2: {3}, 3: {1}},
            normalized_graph={1: {2}, 2: {3}, 3: {1}}
        ),
        'transitive related node cycle, with subtree without cycle': dict(
            graph={1: {2}, 2: {3}, 3: {1}, 5: {4}, 4: {6}},
            normalized_graph={1: {2}, 2: {3}, 3: {1}}
        ),
    })
    def test_cycled_graph(
        self,
        graph: md.python.graph.GraphType,
        normalized_graph: md.python.graph.GraphType
    ) -> None:
        try:
            # act
            list(md.python.graph.topological_sort_ascending(graph=graph))
        except md.python.graph.TopologicalSortException as e:
            # assert
            assert e.code == md.python.graph.TopologicalSortException.CYCLE_DETECTED
            assert e.graph == normalized_graph

    def test_graph_with_hashable_but_not_sortable_nodes(self) -> None:
        # arrange
        class A:
            pass

        class B:
            pass

        class C:
            pass

        graph = {
            42: [A, B, C]
        }

        # act
        result = list(md.python.graph.topological_sort_ascending(graph=graph))

        # assert
        assert {A, B, C} == set(result[0:3])
        assert 42 == result[-1]


class TestDescendingTopologicalSort:
    @dataset({
        'empty graph': dict(
            graph={},
            expected_linearized_sorted_graph=[]
        ),
        'only leaves': dict(
            graph={
                1: [],
                2: [],
                3: [],
            },
            expected_linearized_sorted_graph=[1, 2, 3],
        ),
        'node single relation': dict(
            graph={
                4: {1},
                5: {2},
                6: {3},
            },
            expected_linearized_sorted_graph=[1, 4, 2, 5, 3, 6]
        ),
        'few levels depth graph': dict(
            graph={
                7: {5, 4},
                5: {3, 2},
                8: {5, 1},
                6: {5},
                4: {3, 1},
            },
            expected_linearized_sorted_graph=[1, 3, 4, 2, 5, 7, 8, 6]
        ),
    })
    def test_acyclic_graph(
        self,
        graph: md.python.graph.GraphType,
        expected_linearized_sorted_graph: typing.Sequence[md.python.graph.NodeType]
    ) -> None:
        # act
        linearized_sorted_graph = list(
            md.python.graph.topological_sort_descending(graph=graph)
        )

        # assert
        assert linearized_sorted_graph == expected_linearized_sorted_graph

    @dataset({
        'direct related node cycle': dict(
            graph={1: {2}, 2: {1}},
            normalized_graph=[2, 1]
        ),
        'transitive related node cycle': dict(
            graph={1: {2}, 2: {3}, 3: {1}},
            normalized_graph=[3, 2, 1]
        ),
        'transitive related node cycle, with subtree without cycle': dict(
            graph={1: {2}, 2: {3}, 3: {1}, 5: {4}, 4: {6}},
            normalized_graph=[3, 2, 1, 6, 4, 5]
        )
    })
    def test_cycled_graph(
        self,
        graph: md.python.graph.GraphType,
        normalized_graph: md.python.graph.GraphType
    ) -> None:
        # act
        result = list(md.python.graph.topological_sort_descending(graph=graph))

        # assert
        assert result == normalized_graph


class TestGetPathList:
    @dataset({
        'empty graph': dict(
            graph={},
            expected_path_list=[],
            include_subtree=True
        ),
        'only leaves': dict(
            graph={
                1: [],
                2: [],
                3: [],
            },
            expected_path_list=[],
            include_subtree=True
        ),
        'node single relation': dict(
            graph={
                4: {1},
                5: {2},
                6: {3},
            },
            expected_path_list=[[6, 3], [5, 2], [4, 1]],
            include_subtree=True
        ),
        'few levels depth graph': dict(
            graph={
                7: {5, 4},
                5: {3, 2},
                8: {5, 1},
                6: {5},
                4: {3, 1},
            },
            expected_path_list=[
                [7, 5, 3],
                [7, 5, 2],
                [7, 4, 3],
                [7, 4, 1],
                [5, 3],
                [5, 2],
                [8, 5, 3],
                [8, 5, 2],
                [8, 1],
                [6, 5, 3],
                [6, 5, 2],
                [4, 3],
                [4, 1],
            ],
            include_subtree=True
        ),
        'no subtree / empty graph': dict(
            graph={},
            expected_path_list=[],
            include_subtree=False
        ),
        'no subtree / only leaves': dict(
            graph={
                1: [],
                2: [],
                3: [],
            },
            expected_path_list=[],
            include_subtree=False
        ),
        'no subtree / node single relation': dict(
            graph={
                4: {1},
                5: {2},
                6: {3},
            },
            expected_path_list=[[6, 3], [5, 2], [4, 1]],
            include_subtree=False
        ),
        'few levels depth graph, include subtree': dict(
            graph={
                7: {5, 4},
                5: {3, 2},
                8: {5, 1},
                6: {5},
                4: {3, 1},
            },
            expected_path_list=[
                [7, 5, 3],
                [7, 5, 2],
                [7, 4, 3],
                [7, 4, 1],
                [8, 5, 3],
                [8, 5, 2],
                [8, 1],
                [6, 5, 3],
                [6, 5, 2],
            ],
            include_subtree=False
        ),
    })
    def test_acyclic_graph(
        self,
        graph: md.python.graph.GraphType,
        expected_path_list: typing.List[md.python.graph.GraphPathType],
        include_subtree: bool
    ) -> None:  # (black/positive)
        # act
        path_list, cycle_path_list = md.python.graph.get_paths(graph=graph, include_subtree=include_subtree)

        # assert
        assert len(path_list) == len(expected_path_list)
        for path in path_list:
            assert path in expected_path_list

        assert len(cycle_path_list) == 0

    @dataset({
        'direct related node cycle': dict(
            graph={1: {2}, 2: {1}},
            expected_cycle_path_list=[[1, 2, 1]],
            include_subtree=False
        ),
        'transitive related node cycle': dict(
            graph={1: {2}, 2: {3}, 3: {1}},
            expected_cycle_path_list=[[1, 2, 3, 1]],
            include_subtree=False
        ),
        'transitive related node cycle, with subtree without cycle': dict(
            graph={1: {2}, 2: {3}, 3: {1}, 5: {4}, 4: {6}},
            expected_cycle_path_list=[[1, 2, 3, 1]],
            include_subtree=False
        ),
        'transitive related node cycle 2': dict(
            graph={1: {2, 3}, 2: {3}, 3: {2}},
            expected_cycle_path_list=[[2, 3, 2]],
            include_subtree=False
        ),
        'few transitive related nodes cycles': dict(
            graph={1: {2}, 2: {1, 3}, 3: {1}},
            expected_cycle_path_list=[[1, 2, 1], [1, 2, 3, 1]],
            include_subtree=False
        ),
        'few transitive related nodes cycles, with subtree': dict(
            graph={1: {2}, 2: {1, 3}, 3: {1}},
            expected_cycle_path_list=[[1, 2, 1], [1, 2, 3, 1]],
            include_subtree=True
        ),
        'direct related node cycle, with subtree without cycle': dict(
            graph={1: {2}, 2: {1}, 4: {20}},
            expected_cycle_path_list=[[1, 2, 1]],
            include_subtree=True
        ),
        'transitive related node cycle, expose subtree paths': dict(
            graph={1: {2, 3}, 2: {3}, 3: {2}},
            expected_cycle_path_list=[[2, 3, 2]],
            include_subtree=True
        ),
        'transitive related node cycle, with subtree without cycle, expose subtree paths': dict(
            graph={1: {2}, 2: {3}, 3: {1}, 4: {20}},
            expected_cycle_path_list=[[1, 2, 3, 1]],
            include_subtree=True
        ),
        'transitive related node cycle, with subtree without cycle, no subtree': dict(
            graph={1: {2}, 2: {3}, 3: {1}, 5: {4}, 4: {6}},
            expected_cycle_path_list=[[1, 2, 3, 1]],
            include_subtree=True
        ),
    })
    def test_cycled_graph(
        self,
        graph: md.python.graph.GraphType,
        expected_cycle_path_list: typing.List[md.python.graph.GraphPathType],
        include_subtree: bool
    ) -> None:
        # act
        path_list, cycle_path_list = md.python.graph.get_paths(graph=graph, include_subtree=include_subtree)

        # assert
        assert len(cycle_path_list) == len(expected_cycle_path_list)
        for cycle_path in cycle_path_list:
            assert cycle_path in expected_cycle_path_list


class TestAscendingTopologicalSortImplementation:
    def test_sort(self) -> None:
        # arrange
        graph = {42: {}}
        ascending_topological_sort = md.python.graph.AscendingTopologicalSort()

        # act
        with unittest.mock.patch(
            'md.python.graph.topological_sort_ascending',
            return_value=[4, 8, 15, 16, 23, 42]
        ) as mock:
            result = ascending_topological_sort.sort(graph=graph)
            # assert
            mock.assert_called_once_with(graph=graph)
        assert result == [4, 8, 15, 16, 23, 42]


class TestDescendingTopologicalSortImplementation:
    def test_sort(self) -> None:
        # arrange
        graph = {42: {}}
        descending_topological_sort = md.python.graph.DescendingTopologicalSort()

        # act
        with unittest.mock.patch(
            'md.python.graph.topological_sort_descending',
            return_value=[4, 8, 15, 16, 23, 42]
        ) as mock:
            result = descending_topological_sort.sort(graph=graph)
            # assert
            mock.assert_called_once_with(graph=graph)
        assert result == [4, 8, 15, 16, 23, 42]
