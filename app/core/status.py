"""统一状态词（设计稿 §六）。

所有驱动的 parse_status() 必须把各引擎五花八门的原始状态，
翻译成这里的五个词之一。对齐 OpenEverest 实测——注意是 error 不是 failed。
"""

CREATING = "creating"
INITIALIZING = "initializing"
READY = "ready"
ERROR = "error"
DELETING = "deleting"

ALL = frozenset({CREATING, INITIALIZING, READY, ERROR, DELETING})
