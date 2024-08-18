# md.python.graph

md.python.graph component defines contracts to perform operations over
graph type, and provides few useful tools out from box.

## Architecture overview

[![Architecture overview][architecture-overview]][architecture-overview]

## Component overview

```python3
# Types
NodeType = typing.TypeVar('NodeType', bound=typing.Hashable)
GraphType = typing.Mapping[NodeType, typing.Collection[NodeType]]
GraphPathType = typing.Iterable[NodeType]
TopologicalSortType = typing.Callable[[GraphType], typing.Iterable[NodeType]]

# Implementation 
def topological_sort_ascending(graph: GraphType) -> typing.Iterable[NodeType]: ...

def topological_sort_descending(
    graph: GraphType,
    initial_node: typing.Iterable[NodeType] = None
) -> typing.Iterable[NodeType]: ...

def get_paths(graph: GraphType, include_subtree: bool = False) -> typing.Tuple[
    typing.List[GraphPathType],
    typing.List[GraphPathType],
]: ...
```

## Install

```sh
pip install md.python.graph --index-url https://source.md.land/python/
```

## [Documentation](docs/index.md)

Read documentation with examples: <https://development.md.land/python/md.python.graph/>

## [Changelog](changelog.md)
## [License (MIT)](license.md)

[architecture-overview]: docs/_static/architecture-overview.class-diagram.svg
