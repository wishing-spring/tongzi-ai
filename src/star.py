# -*- coding: utf-8 -*-
"""六芒星 · 正反双塔交织"""
import sys; sys.path.insert(0, r'C:\Users\45757\Desktop\lingxiAI_v5.0\src')
from tongzi_kernel import Pyramid, Layer, Gua, form, _fit

class Star:
    """正反双塔交叠。

      正塔(尖朝上) + 倒塔(尖朝下) = 10角全通
      重叠区: 正塔砖与倒塔砖空间交织
      咬合: 只在同塔内锁
    """

    def __init__(self, min_w=2, max_w=8):
        self.up = Pyramid(min_w, max_w)
        self.down = Pyramid(min_w, max_w)
        self.min = min_w
        self.max = max_w

    def overlap_layers(self):
        """重叠区映射: 正8爻<->倒2爻, 正7爻<->倒3爻, ..."""
        pairs = []
        for i in range(self.max - self.min + 1):
            up_layer = self.max - i
            down_layer = self.min + i
            pairs.append((up_layer, down_layer))
        return pairs

    def flow(self, g: Gua, from_up: bool = True):
        """正塔进 -> 过重叠 -> 倒塔出 (或反过来)"""
        in_tower = self.up if from_up else self.down
        out_tower = self.down if from_up else self.up

        # 第1步: 入口塔路由
        r = in_tower.flow(g)
        in_layer = r['入层']

        # 第2步: 找重叠对应层
        for up_l, down_l in self.overlap_layers():
            if from_up and up_l == in_layer:
                cross_layer = down_l
                break
            elif not from_up and down_l == in_layer:
                cross_layer = up_l
                break
        else:
            cross_layer = in_layer

        # 第3步: 重叠层内榫卯碰撞 (在出口塔的砖上)
        cross_bricks = out_tower.layers[cross_layer].bricks
        trimmed = Gua(r['入值'].value & ((1 << cross_layer) - 1))
        matches = [b for b in cross_bricks if _fit(trimmed, b)]

        # 第4步: 出口塔归类
        if matches:
            mid = matches[len(matches) // 2]
            out_r = out_tower.flow(mid)
        else:
            out_r = {'出层': cross_layer, '出值': trimmed, '咬合': 0}

        return {
            '方向': '正->倒' if from_up else '倒->正',
            '入层': r['入层'],
            '入值': r['入值'],
            '重叠层': cross_layer,
            '交叉咬合': len(matches),
            '出层': out_r['出层'],
            '出值': out_r['出值'],
        }

    def __repr__(self):
        lines = ["Star(双塔交叠)"]
        for up_l, down_l in self.overlap_layers():
            indent = "  " * (self.max - up_l)
            u = self.up.layers[up_l]
            d = self.down.layers[down_l]
            lines.append(f"{indent}正{up_l}爻({u.size}) x 倒{down_l}爻({d.size})")
        return '\n'.join(lines)


if __name__ == '__main__':
    star = Star()
    print(star)
    print()

    from tools.encode import text_to_seed
    from tongzi_kernel import phi_slice

    for ch in "道天地人":
        v = phi_slice(text_to_seed(ch), 8)
        g = Gua(v)
        r = star.flow(g, from_up=True)
        print(f"'{ch}' {form(g)} -> 入{r['入层']}爻 x{r['重叠层']}爻 出{r['出层']}爻 [{form(r['出值'])}]")
