"""
Six Thinking Hats agent implementations.

Each agent represents one of the six thinking perspectives:
- White: Facts and data
- Red: Emotions and intuition
- Black: Risks and caution
- Yellow: Benefits and optimism
- Green: Creativity and alternatives
- Blue: Process control and synthesis
"""

from src.agents.base import HatAgentBase, HatAgentConfig
from src.agents.black_hat import BlackHatAgent, create_black_hat_agent

__all__ = [
    "HatAgentBase",
    "HatAgentConfig",
    "BlackHatAgent",
    "create_black_hat_agent",
]
