# -*- coding: utf-8 -*-
"""Anti-Entropy — detect stagnation, inject φ-guided jitter.

Pure XOR/AND collision in a closed F₂ space eventually reaches thermal
death (all pairs have collided, no new information). Anti-entropy detects
stagnation (no new births for N consecutive ticks) and injects small φ-guided
bit flips to break closed groups and restart collision chains.

This is the F₂ equivalent of the I Ching's 9th hexagram — the principle
that pure order needs a small disruptive force to stay alive.
"""

from .constants import phi_slice, CT_MASK


class AntiEntropy:
    """Detects stagnation and injects φ-guided micro-perturbations."""

    def __init__(self, stagnation_window: int = 5, jitter_bits: int = 3):
        self.stagnation_window = stagnation_window
        self.jitter_bits = jitter_bits
        self.stagnation_ticks = 0
        self.total_jitters = 0
        self.last_births = 0

    def check(self, total_births: int) -> bool:
        """Return True if stagnation detected: no new births for N ticks."""
        if total_births == self.last_births:
            self.stagnation_ticks += 1
        else:
            self.stagnation_ticks = 0
            self.last_births = total_births
        return self.stagnation_ticks >= self.stagnation_window

    def jitter(self, ct: int, tick: int) -> int:
        """Apply φ-guided bit flips at pseudorandom positions."""
        self.total_jitters += 1
        self.stagnation_ticks = 0

        seed = phi_slice((tick * 17 + self.total_jitters * 31) % 256, 28)

        jitter_positions = []
        for i in range(self.jitter_bits):
            pos = ((seed >> (i * 9)) & 0x1FF) % 28
            if pos not in jitter_positions:
                jitter_positions.append(pos)

        result = ct
        for pos in jitter_positions:
            result ^= (1 << pos)

        return result & CT_MASK

    def stats(self) -> str:
        return f"AntiEntropy: {self.total_jitters} jitters"
