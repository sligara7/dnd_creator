"""Test framework for MessageHub service integration."""

from .framework import (
    MockService,
    MessageHubTestFramework,
    TEST_EVENT_COUNTER,
    TEST_LATENCY
)

__all__ = [
    'MockService',
    'MessageHubTestFramework',
    'TEST_EVENT_COUNTER',
    'TEST_LATENCY'
]