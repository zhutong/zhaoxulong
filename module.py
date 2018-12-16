import sys

from copy import copy


def update_topo(text):
    nodes = []
    links = []
    for i, line in enumerate(text.splitlines()):
        ss = line.split(',')
        n0 = ss[0]
        n1 = ss[1]
        if n0 not in nodes:
            nodes.append(n0)
        if n1 not in nodes:
            nodes.append(n1)
        try:
            igp_metric = int(ss[2])
        except:
            igp_metric = 100
        links.append(dict(id=1+i,
                          routers=(n0, n1),
                          igp_metric=igp_metric))
    topo = dict(routers=nodes, links=links)
    return topo


def build_graph_dict(routers, links):
    node_db = {}
    for n in routers:
        node_db[n] = dict(id=n, adjacencies=[])

    for l in links:
        routers = l['routers']
        for i in (0, 1):
            n = routers[i]
            router = node_db[n]
            try:
                nei = node_db[routers[1-i]]
            except KeyError:
                continue
            metric = l['igp_metric']
            router['adjacencies'].append(
                dict(id=l['id'], neighbor=routers[1-i], metric=metric))
    return node_db


def iter_path(node_db, c_node_id, dst_id, path, cost):
    node = node_db[c_node_id]
    for adj in node['adjacencies']:
        nei_id = adj['neighbor']
        metric = adj['metric']
        cost1 = cost + metric
        path1 = copy(path)
        path1.append(nei_id)
        if nei_id in path:
            continue
        if nei_id == dst_id:
            paths.append((cost1, path1))
        else:
            iter_path(node_db, nei_id, dst_id, path1, cost1)


def get_path(db, src, dst, n_path=5):
    global paths
    paths = []
    iter_path(db, src, dst, [src], 0)
    paths.sort()
    return paths[:n_path]


if __name__ == '__main__':
    src = sys.argv[1]
    dst = sys.argv[2]
    with open('link.txt') as f:
        text = f.read()
    db = build_graph_dict(**update_topo(text))
    for i, p in enumerate(get_path(db, src, dst), 1):
        print('%3d  %6d    %s' % (i, p[0], ' --> '.join(p[1])))
