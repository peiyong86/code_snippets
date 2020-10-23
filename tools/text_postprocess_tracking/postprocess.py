"""
This module provide post processing function for OCR results of single image.
Concatenate sperated text boxes which belongs to the same line.
Replace "(" ")" "，" and "。" with empty string.

Example:
results = [[{'cx': 180, 'cy': 656, 'w': 357, 'h': 41, 'text': 'E生平安医疗险', 'degree': 0},
            {'cx': 540, 'cy': 656, 'w': 357, 'h': 41, 'text': 'E生平安医疗险', 'degree': 0},
            {'cx': 185, 'cy': 53, 'text': 'PINUAN', 'w': 184, 'h': 26, 'degree': 0},
            {'cx': 61, 'cy': 741, 'text': '最高600万保障', 'w': 594, 'h': 84, 'degree': 0},
            {'cx': 101, 'cy': 848, 'text': '让您平安无忧', 'w': 521, 'h': 84, 'degree': 0},
            {'cx': 258, 'cy': 997, 'text': '立即投你', 'w': 184, 'h': 46, 'degree': 0}]]
results = filter_size(results) # filter by size, remove small size text
results = post_process(results) # Concatenate texts.
```
[[{'cx': 180,
   'cy': 656,
   'w': 717,
   'h': 41,
   'text': 'E生平安医疗险E生平安医疗险',
   'degree': 0},
  {'cx': 61, 'cy': 741, 'text': '最高600万保障', 'w': 594, 'h': 84, 'degree': 0},
  {'cx': 101, 'cy': 848, 'text': '让您平安无忧', 'w': 521, 'h': 84, 'degree': 0},
  {'cx': 258, 'cy': 997, 'text': '立即投你', 'w': 184, 'h': 46, 'degree': 0}]]
```
"""
import copy
from collections import defaultdict


# generate pairs
def if_combine_box(boxa, boxb):
    def _overlap(a1, a2, b1, b2):
        return max(0, min(a2, b2) - max(a1, b1))

    def _distance(x1, w1, x2, w2):
        if x1 > x2:
            x1, x2, w1, w2 = x2, x1, w2, w1
        return x2 - (x1 + w1)

    _yo = _overlap(boxa['cy'], boxa['cy'] + boxa['h'], boxb['cy'], boxb['cy'] + boxb['h'])
    _yo = _yo / min(boxa['h'], boxb['h'])

    _xdis = _distance(boxa['cx'], boxa['w'], boxb['cx'], boxb['w'])

    if _yo > 0.5 and _xdis < 30:
        return True
    return False


def generate_pairs(result):
    pairs = []
    for i in range(len(result) - 1):
        for j in range(i + 1, len(result)):
            a = result[i]
            b = result[j]
            if if_combine_box(a, b):
                pairs.append([i, j])
    return pairs


def search_key(node_key, i, pair_dict):
    if node_key[i] is not None:
        return node_key[i]
    if i in pair_dict:
        for j in pair_dict[i]:
            re = search_key(node_key, j, pair_dict)
            if re is not None:
                return re
    return None


def assign_key(node_key, i, pair_dict, groupid):
    node_key[i] = groupid
    if i in pair_dict:
        for j in pair_dict[i]:
            assign_key(node_key, j, pair_dict, groupid)


def generate_groups_from_pairs(pairs):
    # generate groups from pairs
    node_key = {}
    for i, j in pairs:
        node_key[i] = None
        node_key[j] = None

    pair_dict = {}
    for i, j in pairs:
        if i not in pair_dict:
            pair_dict[i] = [j]
        else:
            pair_dict[i].append(j)

    groupid = 0
    for i, j in pairs:
        if node_key[i] is None:
            currentid = search_key(node_key, i, pair_dict)
            if currentid is not None:
                assign_key(node_key, i, pair_dict, currentid)
            else:
                assign_key(node_key, i, pair_dict, groupid)
                groupid += 1
    return node_key


# combine text
def combine_item(items, inds):
    picked = [items[i] for i in inds]
    # 从上向下，从左向右，排序
    picked.sort(key=lambda x: (x['cy'], x['cx']))
    combtext = ''.join([d['text'] for d in picked])
    x1 = min([d['cx'] for d in picked])
    x2 = max([d['cx'] + d['w'] for d in picked])
    y1 = min([d['cy'] for d in picked])
    y2 = max([d['cy'] + d['h'] for d in picked])
    newitem = {'cx': x1, 'cy': y1, 'w': x2 - x1, 'h': y2 - y1, 'text': combtext, 'degree': 0}
    return newitem


def combine_items_by_group(node_key, result):
    groups = defaultdict(list)
    for k, v in node_key.items():
        groups[v].append(k)

    newitems = []
    for k, v in groups.items():
        item = combine_item(result, v)
        newitems.append(item)

    for ind in sorted(node_key.keys(), reverse=True):
        result.pop(ind)

    newitems.extend(result)
    return newitems


def refine_text(d):
    for t in d:
        t['text'] = t['text'].replace('(', '')
        t['text'] = t['text'].replace(')', '')
        t['text'] = t['text'].replace('。', '')
        t['text'] = t['text'].replace('，', '')
    return d


def _post_process(items):
    items = copy.deepcopy(items)
    pairs = generate_pairs(items)
    groups = generate_groups_from_pairs(pairs)
    newitems = combine_items_by_group(groups, items)
    newitems = refine_text(newitems)
    return newitems


def post_process(results):
    results = [_post_process(d) for d in results]
    return results


def filter_size(results, max_height=30):
    for i,result in enumerate(results):
        result = [re for re in result if re['h']>max_height]
        results[i] = result
    return results
