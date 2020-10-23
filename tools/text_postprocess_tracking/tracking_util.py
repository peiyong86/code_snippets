from char_featurizer import Featurizer
import edit_distance


def extract_char_fea(sent):
    # 提取四角码作为特征
    try:
        featurizer = Featurizer()
        feas = featurizer.featurize(sent)
        fea = feas[3] + feas[4]
    except Exception as e:
        return None
    #         print("四角码提取错误")
    #         print(sent)
    #         raise e
    return fea


def compare_char_fea(fea0, fea1):
    if fea0 is None or fea1 is None:
        return False
    re = [1 if a == b else 0 for a, b in zip(fea0, fea1)]
    return sum(re) > int(0.8 * len(fea0))


def is_repeat_text(texta, textb):
    # 如果有包含关系为True
    if texta in textb or textb in texta:
        return True

    # 如果字数相同，且80%的四角码相同
    if len(texta) == len(textb):
        feaa = extract_char_fea(texta)
        feab = extract_char_fea(textb)
        if compare_char_fea(feaa, feab):
            return True

    # 或 编辑距离小于等于1且字符串小于10
    # 或 编辑距离小于等于2 为True
    sm = edit_distance.SequenceMatcher(texta, textb)
    dis = sm.distance()
    if min(len(texta), len(textb)) < 10:
        return dis <= 1
    else:
        return dis <= 2


def remove_repeat(tracker):
    tracker_boxes = tracker.boxes
    while True:
        pop_indexes = []
        for i in range(len(tracker_boxes) - 1):
            box, nextbox = tracker_boxes[i:i + 2]
            if is_repeat_text(box['text'], nextbox['text']):
                pop_indexes.append(i + 1)

        if len(pop_indexes) == 0:
            break

        for ind in pop_indexes[::-1]:
            tracker_boxes.pop(ind)