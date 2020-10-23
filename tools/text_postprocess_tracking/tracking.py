"""
This module provide tracking function for a series of OCR result(tipycaly the OCR results 
from video frames). 
Tracking of text boxes is based on spatical overlap and temporal adjection of text boxes,
and duplicated texts are removed based on edit distance and char features of Chinese 
characters.

Input data is a series of OCR results, each result may have serveral text boxes, each 
text box has those attributes: cx, cy, w, h, text.

Example:
results = [[{'cx': 298, 'cy': 730, 'text': '老板', 'w': 122, 'h': 62, 'degree': 0}],
         [{'cx': 180, 'cy': 736, 'text': '您这有慢头吗', 'w': 352, 'h': 52, 'degree': 0}],
         [{'cx': 180, 'cy': 730, 'text': '您这有馒头吗', 'w': 352, 'h': 57, 'degree': 0}],
         [{'cx': 225, 'cy': 730, 'text': '我想买2个', 'w': 268, 'h': 57, 'degree': 0}],
         [{'cx': 224, 'cy': 730, 'text': '我想买2个', 'w': 268, 'h': 57, 'degree': 0}],
         [{'cx': 151, 'cy': 730, 'text': '我们这只有套餐', 'w': 414, 'h': 57, 'degree': 0}],
         [{'cx': 151, 'cy': 729, 'text': '我们这只有套餐', 'w': 416, 'h': 69, 'degree': 0}],
         [{'cx': 241, 'cy': 730, 'text': '没有慢头', 'w': 234, 'h': 62, 'degree': 0}],
         [{'cx': 241, 'cy': 730, 'text': '不吃出去', 'w': 234, 'h': 57, 'degree': 0}],
         []]

trackers = track_results(results)
```
trackers:
[Tracker(老板
 您这有慢头吗
 我想买2个
 我们这只有套餐
 没有慢头
 不吃出去
 )]
```

"""
from tracking_util import remove_repeat


def cal_overlap(boxa, boxb):

    def _overlap(a1, a2, b1, b2):
        return max(0, min(a2, b2) - max(a1, b1))

    def _area(box):
        return box['w'] * box['h']

    _xo = _overlap(boxa['cx'], boxa['cx' ] +boxa['w'], boxb['cx'], boxb['cx' ] +boxb['w'])
    _yo = _overlap(boxa['cy'], boxa['cy' ] +boxa['h'], boxb['cy'], boxb['cy' ] +boxb['h'])
    _areao = _xo * _yo

    return _areao / min(_area(boxa), _area(boxb))


class Tracker:
    def __init__(self, box=None):
        self.boxes = []
        if box is not None:
            self.boxes.append(box)

    def track(self, box):
        lastbox = self.boxes[-1]
        o = cal_overlap(box, lastbox)
        if o > 0.5:
            self.boxes.append(box)
            return True
        else:
            return False

    def __repr__(self):
        repr_str = "Tracker("
        for box in self.boxes:
            repr_str += box['text'] + '\n'
        repr_str += ")"
        return repr_str

    def __len__(self):
        return len(self.boxes)

    def __lt__(self, other):
        return len(self.boxes)<len(other)

    def save(self, filename):
        with open(filename, 'w') as f:
            for box in self.boxes:
                line = box['text'] + '\n'
                f.write(line)


def track_results(results):
    trackers = []

    for result in results:

        for re in result:
            if_tracked = False
            for tracker in trackers:
                if if_tracked == False:
                    if_tracked = tracker.track(re)

            if if_tracked == False:
                trackers.append(Tracker(re))

    for tracker in trackers:
        remove_repeat(tracker)

    return trackers


