# -*- coding: utf-8 -*-
from gto import Config


def test_merge_route():
    gto = Config()
    local_to_target = [1, 2, 3, 9]
    local_to_source = [1]
    print(gto._merge_route(local_to_source, local_to_target))
    assert gto._merge_route(local_to_source, local_to_target) == [1, 2, 3, 9]
    local_to_source = [1, 2]
    print(gto._merge_route(local_to_source, local_to_target))
    assert gto._merge_route(local_to_source, local_to_target) == [2, 3, 9]
    local_to_source = [1, 3]
    print(gto._merge_route(local_to_source, local_to_target))
    assert gto._merge_route(local_to_source, local_to_target) == [3, 9]
    local_to_source = [1, 3, 5, 8]
    print(gto._merge_route(local_to_source, local_to_target))
    assert gto._merge_route(local_to_source, local_to_target) == [8, 5, 3, 9]
    print("test_merge_route done")


if __name__ == '__main__':
    test_merge_route()
