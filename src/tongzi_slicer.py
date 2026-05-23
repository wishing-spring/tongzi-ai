"""
童子 · 多模态 φ 切片器
======================
独立模块。所有模态 → 同一条 φ 规则 → N 位卦。
无依赖，不接入 tongzi_core。纯转换。
"""
import hashlib
import struct
from typing import List, Tuple, Dict, Optional, Any, Union

# ── φ 母体 (256-bit) ──
PHI_BITS = (
    "10011110001101110111100110111001"
    "01000011111010010001110110001010"
    "00111101001001010101111101010111"
    "01000111101010010101000111101010"
    "00010100010101010010110100110101"
    "01010111010010000111010100010001"
    "01010100110101000101010001011010"
    "00111111100101000011101111111101"
)
PHI_LEN = len(PHI_BITS)
VEC_DIM = 16


# ══════════════════════════════════════════════
# 核心：种子 → φ 切片
# ══════════════════════════════════════════════

def _phi_slice(seed: int, dim: int = VEC_DIM) -> Tuple[int, int]:
    """所有模态统一入口。返回 (卦值, φ位置)。"""
    pos = seed % PHI_LEN
    chars = [PHI_BITS[(pos + i) % PHI_LEN] for i in range(dim)]
    return int(''.join(chars), 2), pos


def _str_seed(text: str) -> int:
    """字符串 → 31位种子。"""
    seed = 0
    for i, c in enumerate(text):
        seed ^= ord(c) << (i * 7 % 32)
    return seed & 0x7FFFFFFF


def _bytes_seed(data: bytes) -> int:
    """字节串 → SHA256 → 31位种子。"""
    h = hashlib.sha256(data).digest()
    return struct.unpack('>I', h[:4])[0] & 0x7FFFFFFF


def _int_list_seed(vals: List[int], bits_per: int = 8) -> int:
    """整数列表 XOR 折叠 → 种子。"""
    seed = 0
    for i, v in enumerate(vals):
        seed ^= (v & ((1 << bits_per) - 1)) << (i * bits_per % 32)
    return seed & 0x7FFFFFFF


def _float_list_seed(vals: List[float]) -> int:
    """浮点列表 归一化 → 量化 0~255 → XOR 折叠 → 种子。"""
    if len(vals) == 1:
        q = int(vals[0] * 127.5 + 127.5) & 0xFF
        return q
    v_min, v_max = min(vals), max(vals)
    rng = v_max - v_min
    seed = 0
    for i, v in enumerate(vals):
        q = int((v - v_min) / rng * 255) & 0xFF if rng > 0 else 128
        seed ^= q << (i * 8 % 32)
    return seed & 0x7FFFFFFF


# ══════════════════════════════════════════════
# 01  文字
# ══════════════════════════════════════════════

def slice_text(text: str, dim: int = VEC_DIM) -> Tuple[int, int]:
    """文字 → 卦。"""
    return _phi_slice(_str_seed(text), dim)


# ══════════════════════════════════════════════
# 02  数字
# ══════════════════════════════════════════════

def slice_number(n: Union[int, float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """单个数字 → 卦。整数/浮点数通用。"""
    seed = struct.unpack('>I', struct.pack('>f', float(n)))[0] & 0x7FFFFFFF
    return _phi_slice(seed, dim)


def slice_numbers(nums: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """数值列表 → 卦。"""
    return _phi_slice(_float_list_seed(nums), dim)


def slice_vector(vec: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """向量（任意维度）→ 卦。slice_numbers 别名。"""
    return slice_numbers(vec, dim)


# ══════════════════════════════════════════════
# 03  图像
# ══════════════════════════════════════════════

def slice_image_binary(bits: List[int], dim: int = VEC_DIM) -> Tuple[int, int]:
    """二值矩阵 → 卦。bits: 0/1 列表（任意长度，4×4=16, 8×8=64 ...）。"""
    return _phi_slice(_int_list_seed(bits, bits_per=1), dim)


def slice_image_gray(pixels: List[int], dim: int = VEC_DIM) -> Tuple[int, int]:
    """灰度像素 [0~255] → 卦。"""
    return _phi_slice(_int_list_seed(pixels, bits_per=8), dim)


def slice_image_file(path: str, dim: int = VEC_DIM) -> Tuple[int, int]:
    """图像文件 → 卦。无 PIL 依赖，SHA256 哈希。"""
    with open(path, 'rb') as f:
        raw = f.read()
    return _phi_slice(_bytes_seed(raw), dim)


# ══════════════════════════════════════════════
# 04  声纹
# ══════════════════════════════════════════════

def slice_audio_samples(samples: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """原始音频样本 [-1.0, 1.0] → 卦。"""
    return _phi_slice(_float_list_seed(samples), dim)


def slice_audio_file(path: str, dim: int = VEC_DIM) -> Tuple[int, int]:
    """音频文件 → 卦。"""
    with open(path, 'rb') as f:
        raw = f.read()
    return _phi_slice(_bytes_seed(raw), dim)


# ══════════════════════════════════════════════
# 05  视频
# ══════════════════════════════════════════════

def slice_video_frames(frames: List[List[int]], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    视频帧序列 → 卦。
    frames: [[0/1/...], [0/1/...], ...] 每帧一个二值或灰度列表。
    先每帧独立切片，再 XOR 折叠所有帧结果。
    """
    if not frames:
        raise ValueError("空帧序列")
    combined_seed = 0
    for fi, frame in enumerate(frames):
        s = _int_list_seed(frame, bits_per=8)
        combined_seed ^= (s << (fi * 7 % 32))
    combined_seed &= 0x7FFFFFFF
    return _phi_slice(combined_seed, dim)


def slice_video_frames_binary(frames: List[List[int]], dim: int = VEC_DIM) -> Tuple[int, int]:
    """视频帧序列（全二值）→ 卦。"""
    return slice_video_frames(frames, dim)


# ══════════════════════════════════════════════
# 06  结构化数据
# ══════════════════════════════════════════════

def slice_dict(d: Dict[str, Any], dim: int = VEC_DIM) -> Tuple[int, int]:
    """字典/键值对 → 卦。按键排序后序列化。"""
    items = sorted(d.items())
    raw = repr(items).encode('utf-8')
    return _phi_slice(_bytes_seed(raw), dim)


def slice_table(rows: List[List[float]], dim: int = VEC_DIM) -> Tuple[int, int]:
    """表格数据 → 卦。按行展平后做信号切片。"""
    flat = []
    for row in rows:
        flat.extend(row)
    return slice_numbers(flat, dim)


# ══════════════════════════════════════════════
# 07  传感器（IMU/环境/生物）
# ══════════════════════════════════════════════

def slice_sensor(samples: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """通用传感器读数 → 卦。slice_numbers 别名。"""
    return slice_numbers(samples, dim)


def slice_multisensor(channels: List[List[float]], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    多通道传感器 → 卦。
    channels: [[x1,x2,...], [y1,y2,...], [z1,z2,...]]  如加速度计三轴。
    每个通道独立切片，XOR 折叠。
    """
    combined_seed = 0
    for ci, ch in enumerate(channels):
        s = _float_list_seed(ch)
        combined_seed ^= (s << (ci * 11 % 32))
    combined_seed &= 0x7FFFFFFF
    return _phi_slice(combined_seed, dim)


# ══════════════════════════════════════════════
# 08  时间 / 位置
# ══════════════════════════════════════════════

def slice_timestamp(ts: float, dim: int = VEC_DIM) -> Tuple[int, int]:
    """Unix 时间戳 → 卦。"""
    seed = int(ts * 1000) & 0x7FFFFFFF
    return _phi_slice(seed, dim)


def slice_gps(lat: float, lon: float, alt: float = 0.0, dim: int = VEC_DIM) -> Tuple[int, int]:
    """GPS 坐标 → 卦。"""
    return slice_vector([lat, lon, alt], dim)


# ══════════════════════════════════════════════
# 09  字节流
# ══════════════════════════════════════════════

def slice_bytes(data: bytes, dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    任意字节流 → 卦。
    网络包、二进制协议、加密数据——来者不拒。
    """
    return _phi_slice(_bytes_seed(data), dim)


def slice_file(path: str, dim: int = VEC_DIM) -> Tuple[int, int]:
    """任意文件 → 卦。自动识别类型，否则当字节流。"""
    ext = path.lower().split('.')[-1] if '.' in path else ''
    img_exts = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp', 'tiff'}
    aud_exts = {'wav', 'mp3', 'ogg', 'flac', 'aac', 'm4a', 'wma'}

    if ext in img_exts:
        return slice_image_file(path, dim)
    elif ext in aud_exts:
        return slice_audio_file(path, dim)
    else:
        with open(path, 'rb') as f:
            return slice_bytes(f.read(), dim)


# ══════════════════════════════════════════════
# 10  图 / 网络
# ══════════════════════════════════════════════

def slice_graph(edges: List[Tuple[int, int]], dim: int = VEC_DIM) -> Tuple[int, int]:
    """图结构（边列表）→ 卦。展平所有节点编号后做信号切片。"""
    flat = []
    for a, b in edges:
        flat.append(float(a))
        flat.append(float(b))
    return slice_numbers(flat, dim)


# ══════════════════════════════════════════════
# 11  代码
# ══════════════════════════════════════════════

def slice_code(source: str, dim: int = VEC_DIM) -> Tuple[int, int]:
    """源代码 → 卦。去空白、去注释后哈希。"""
    clean = '\n'.join(
        line.split('#')[0].split('//')[0]
        for line in source.split('\n')
        if line.strip() and not line.strip().startswith(('#', '//'))
    )
    return slice_text(clean, dim)


# ══════════════════════════════════════════════
# 12  动作 / 控制
# ══════════════════════════════════════════════

def slice_action_joints(angles: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    机器人关节角度 → 卦。
    angles: [肩, 肘, 腕, ...] 每关节 0~360 度。
    """
    return slice_vector(angles, dim)


def slice_action_keys(keys: List[str], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    键盘/快捷键组合 → 卦。
    keys: ['Ctrl', 'Alt', 'Del'] 等。
    """
    seed = 0
    for k in sorted(keys):
        seed ^= _str_seed(k.lower())
    return _phi_slice(seed & 0x7FFFFFFF, dim)


def slice_action_command(cmd: str, args: Optional[List[float]] = None,
                         dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    指令 + 参数 → 卦。
    cmd: 'move', 'grip', 'rotate' 等。
    args: 可选的数值参数 [x, y, z]。
    """
    seed = _str_seed(cmd)
    if args:
        seed ^= _float_list_seed(args)
    return _phi_slice(seed & 0x7FFFFFFF, dim)


def slice_action_path(waypoints: List[List[float]], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    路径/轨迹 → 卦。
    waypoints: [[x1,y1,z1], [x2,y2,z2], ...]。
    展平所有航点后切片。
    """
    flat = []
    for wp in waypoints:
        flat.extend(wp)
    return slice_vector(flat, dim)


# ══════════════════════════════════════════════
# 13  时序切片（GPT 提醒的第二层）
# ══════════════════════════════════════════════

def slice_sequence(values: List[float], dim: int = VEC_DIM) -> List[Tuple[int, int]]:
    """
    数值序列 → 卦流。
    不压成一个卦，保留时间结构。
    返回 [t0卦, t1卦, t2卦, ...] 每个时刻独立切片。
    """
    return [slice_number(v, dim) for v in values]


def slice_sliding(values: List[float], window: int = 8, stride: int = 4,
                  dim: int = VEC_DIM) -> List[Tuple[int, int]]:
    """
    滑窗切片 → 卦流。
    窗口在序列上滑动，每窗一个卦。
    保留局部上下文。
    """
    results = []
    for start in range(0, len(values) - window + 1, stride):
        window_vals = values[start:start + window]
        results.append(slice_vector(window_vals, dim))
    return results


def slice_multiscale(values: List[float], scales: List[int] = None,
                     dim: int = VEC_DIM) -> Dict[int, Tuple[int, int]]:
    """
    多尺度切片。
    同一序列在不同窗口尺度下独立切片。
    返回 {scale: (卦值, φ位置)}。
    """
    if scales is None:
        scales = [4, 8, 16]
    result = {}
    for w in scales:
        if w > len(values):
            w = len(values)
        window_vals = values[-w:]  # 取尾部
        result[w] = slice_vector(window_vals, dim)
    return result


def slice_rhythm(values: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    节奏切片 → 卦。
    提取序列的"变化模式"而非绝对值。
    相邻差值的正负号 → 种子。
    慢慢说 vs 急促说在这里分化。
    """
    if len(values) < 2:
        return slice_vector(values, dim)
    diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
    # 正负号 + 幅度
    seed = 0
    for i, d in enumerate(diffs):
        bit = 1 if d > 0 else 0
        seed |= bit << (i % 31)
    return _phi_slice(seed & 0x7FFFFFFF, dim)


def slice_interval(values: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    间隔切片 → 卦。
    提取序列的时间间隔模式。
    相邻时间戳的差值 → 种子。
    用于检测节奏快慢变化。
    """
    if len(values) < 3:
        return slice_vector(values, dim)
    intervals = [values[i+1] - values[i] for i in range(len(values)-1)]
    return slice_vector(intervals, dim)


def slice_dynamics(values: List[float], dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    动力学切片 → 卦（终极时序入口）。
    同时捕捉位置、速度、加速度。
    三通道 XOR 折叠 → 一个卦。
    """
    pos = slice_vector(values, dim)[0]
    vel = slice_rhythm(values, dim)[0] if len(values) >= 2 else 0
    acc_seed = 0
    if len(values) >= 3:
        acc = [values[i+2] - 2*values[i+1] + values[i] for i in range(len(values)-2)]
        acc_seed = _float_list_seed(acc)
        acc_val = _phi_slice(acc_seed, dim)[0]
    else:
        acc_val = 0
    combined = pos ^ vel ^ acc_val
    seed = combined & 0x7FFFFFFF
    return _phi_slice(seed, dim)


# ══════════════════════════════════════════════
# 批量 / 统一入口
# ══════════════════════════════════════════════

def slice_any(data, mode: str = 'auto', dim: int = VEC_DIM) -> Tuple[int, int]:
    """
    统一入口。自动检测或手动指定。

    支持 mode:
      'auto'   'text'  'number'  'image'  'audio'
      'video'  'dict'   'table'   'sensor' 'bytes'
      'file'   'gps'    'graph'   'code'   'vector'
    """
    if mode == 'auto':
        if isinstance(data, str):
            if any(data.lower().endswith(e) for e in
                   ['.png','.jpg','.jpeg','.bmp','.gif','.webp']):
                return slice_image_file(data, dim)
            elif any(data.lower().endswith(e) for e in
                     ['.wav','.mp3','.ogg','.flac','.aac','.m4a']):
                return slice_audio_file(data, dim)
            else:
                return slice_text(data, dim)
        elif isinstance(data, bytes):
            return slice_bytes(data, dim)
        elif isinstance(data, (int, float)):
            return slice_number(data, dim)
        elif isinstance(data, list):
            if data and isinstance(data[0], (int, float)):
                return slice_numbers([float(x) for x in data], dim)
        elif isinstance(data, dict):
            return slice_dict(data, dim)
        raise ValueError(f"无法自动检测: {type(data).__name__}")

    # 手动模式
    modes = {
        'text':      lambda: slice_text(str(data), dim),
        'number':    lambda: slice_number(float(data), dim),
        'image':     lambda: slice_image_file(str(data), dim),
        'audio':     lambda: slice_audio_file(str(data), dim) if isinstance(data, str)
                     else slice_audio_samples([float(x) for x in data], dim),
        'video':     lambda: slice_video_frames(data, dim),
        'dict':      lambda: slice_dict(data, dim),
        'table':     lambda: slice_table(data, dim),
        'sensor':    lambda: slice_sensor([float(x) for x in data], dim),
        'bytes':     lambda: slice_bytes(data if isinstance(data, bytes) else bytes(data), dim),
        'file':      lambda: slice_file(str(data), dim),
        'gps':       lambda: slice_gps(*data, dim=dim),
        'graph':     lambda: slice_graph(data, dim),
        'code':      lambda: slice_code(str(data), dim),
        'vector':    lambda: slice_vector([float(x) for x in data], dim),
        'action':    lambda: slice_action_command(str(data[0]), data[1] if len(data)>1 else None, dim),
        'keys':      lambda: slice_action_keys(data, dim),
        'path':      lambda: slice_action_path(data, dim),
        'rhythm':    lambda: slice_rhythm([float(x) for x in data], dim),
        'interval':  lambda: slice_interval([float(x) for x in data], dim),
        'dynamics':  lambda: slice_dynamics([float(x) for x in data], dim),
    }
    if mode not in modes:
        raise ValueError(f"未知模式: {mode}。支持: {list(modes.keys())}")
    return modes[mode]()


# ══════════════════════════════════════════════
# 快速遍历
# ══════════════════════════════════════════════

if __name__ == '__main__':
    tests = [
        ("文字",       slice_text("圆")),
        ("数字",       slice_number(3.14159)),
        ("数组",       slice_numbers([1.0, 2.0, 3.0, 5.0, 8.0])),
        ("向量",       slice_vector([0.5, -0.3, 0.8])),
        ("二值图",     slice_image_binary([0,1,1,0, 1,0,0,1, 1,0,0,1, 0,1,1,0])),
        ("灰度图",     slice_image_gray([128,64,32, 200,100,50, 255,128,0])),
        ("声频样本",   slice_audio_samples([0.1, -0.2, 0.3, -0.1, 0.05])),
        ("视频帧",     slice_video_frames([[1,0]*8, [0,1]*8, [1,1]*8])),
        ("字典",       slice_dict({"x": 1, "y": 2, "name": "test"})),
        ("表格",       slice_table([[1.0,2.0],[3.0,4.0],[5.0,6.0]])),
        ("传感器",     slice_sensor([9.8, 9.7, 9.9, 9.8, 9.6])),
        ("多通道",     slice_multisensor([[1,2,3],[4,5,6],[7,8,9]])),
        ("时间戳",     slice_timestamp(1716374400.0)),
        ("GPS",        slice_gps(39.9042, 116.4074)),
        ("字节",       slice_bytes(b'\x00\xFF\xAB\xCD\x12\x34')),
        ("图结构",     slice_graph([(1,2),(2,3),(3,1)])),
        ("代码",       slice_code("def add(a,b): return a+b")),
        ("关节动作",   slice_action_joints([90, 45, 180, 0, 30])),
        ("按键",       slice_action_keys(['Ctrl', 'Alt', 'Del'])),
        ("指令",       slice_action_command('move', [10.0, 20.0, 5.0])),
        ("路径",       slice_action_path([[0,0,0],[1,1,0],[2,2,1]])),
        ("节奏",       slice_rhythm([1,3,2,5,3,6,4,7])),
        ("间隔",       slice_interval([0,10,25,30,50,55,80])),
        ("动力学",     slice_dynamics([0,1,3,6,10,15,21])),
    ]
    for name, (val, pos) in tests:
        print(f"  {name:8s}  {val:016b}  pos={pos:3d}")
    print(f"\n✅ 全模态 φ 切片器就绪 · 共 {len(tests)} 种入口 · 统一通道")
