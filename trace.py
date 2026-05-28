# -*- coding: utf-8 -*-
"""Trace module — auditable internal decision trail"""
import time, json

class Trace:
    """Internal decision trace — every step recorded"""
    def __init__(self):
        self.steps = []
        self.input_text = ''
        self.start_time = 0

    def start(self, text: str):
        self.steps = []
        self.input_text = text
        self.start_time = time.time()

    def layer(self, name: str, **kwargs):
        self.steps.append({'layer': name, **kwargs})

    def decision(self, result: str, reason: str = '', **kwargs):
        self.steps.append({'layer': 'DECISION', 'result': result, 'reason': reason, **kwargs})

    def dump(self) -> str:
        lines = [f'[INPUT] {self.input_text}']
        for s in self.steps:
            layer = s.pop('layer', '?')
            if layer == 'DECISION':
                lines.append(f'[DECISION] {s.get("result","?")} reason={s.get("reason","")}')
            elif layer == 'gua':
                lines.append(f'[GUA] bits={s.get("hex","?")} unit={s.get("unit","?")}')
            elif layer == 'yinyang':
                lines.append(f'[YINYANG] bias={s.get("bias","?")} coherence={s.get("coherence",0):.3f}')
            elif layer == 'bite':
                hits = s.get('hits', [])
                hit_str = ','.join(hits) if hits else 'none'
                ruled_out = s.get('ruled_out', [])
                ruled_str = ' | ruled_out: '+','.join(ruled_out) if ruled_out else ''
                lines.append(f'[BITE] rule={s.get("rule","?")} hits=[{hit_str}] energy={s.get("energy",0):.3f}{ruled_str}')
            elif layer == 'bagua':
                lines.append(f'[BAGUA] state={s.get("state","?")} gate={s.get("gate","?")}')
            elif layer == 'mood':
                lines.append(f'[MOOD] {s.get("from","?")}→{s.get("to","?")} energy={s.get("energy",0):.2f}')
            elif layer == 'persona':
                lines.append(f'[PERSONA] voice={s.get("voice","?")} descs={s.get("descs","?")}')
            elif layer == 'semantic':
                lines.append(f'[SEMANTIC] field={s.get("field","?")}')
            else:
                lines.append(f'[{layer}] {s}')
        elapsed = time.time() - self.start_time
        lines.append(f'[END] {elapsed:.3f}s')
        return '\n'.join(lines)
