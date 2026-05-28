# -*- coding: utf-8 -*-
"""Lingxi — Discrete Structure Reducer

A zero-training, zero-gradient, bit-level auditable artificial life system.
Child persona (age 10) with self-growth, dreaming, and personality filter.

Usage:
    import lingxi
    lingxi.demo()            # run evidence experiments
    lingxi.start()           # auto-detect GUI or terminal mode
    lingxi.start(gui=False)  # force terminal mode
"""

__version__ = "8.3.0"
__all__ = ["start", "demo", "LingxiFusion"]


def start(gui: bool = True) -> None:
    """Launch interactive child session.

    Args:
        gui: If True and tkinter is available, launch GUI window.
             Otherwise launch terminal interactive mode.
    """
    if gui:
        try:
            import tkinter  # noqa: F401
            from .child_window import launch
            launch()
            return
        except ImportError:
            pass

    from .live_child import main
    main()


def demo() -> None:
    """Run evidence experiments."""
    from .demo_evidence import main
    main()


from .lingxi_fusion import LingxiFusion  # noqa: E402
