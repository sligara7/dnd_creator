"""
Tests for analysis router endpoints.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict

import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_analyze_patterns(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test analyzing event patterns."""
    response = await client.post(
        "/api/v2/analysis/patterns",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "min_support": 0.1,
        },
        json={
            "event_types": event_search_params["event_types"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert isinstance(result, list)
    # Patterns not found in test data is expected
    assert len(result) == 0

@pytest.mark.asyncio
async def test_detect_anomalies(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test detecting anomalies."""
    response = await client.post(
        "/api/v2/analysis/anomalies",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "sensitivity": 0.8,
        },
        json={
            "event_types": event_search_params["event_types"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert isinstance(result, list)
    # Anomalies not found in test data is expected
    assert len(result) == 0

@pytest.mark.asyncio
async def test_analyze_trends(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test analyzing event trends."""
    response = await client.get(
        "/api/v2/analysis/trends",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "interval": "1h",
            "event_types": event_search_params["event_types"][0]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert isinstance(result, list)
    # Trends in test data are expected to be empty
    assert len(result) == 0

@pytest.mark.asyncio
async def test_analyze_patterns_invalid_dates(client: AsyncClient):
    """Test pattern analysis with invalid date range."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date + timedelta(days=1)  # Start after end
    
    response = await client.post(
        "/api/v2/analysis/patterns",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "min_support": 0.1,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_detect_anomalies_invalid_sensitivity(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test anomaly detection with invalid sensitivity."""
    response = await client.post(
        "/api/v2/analysis/anomalies",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "sensitivity": 2.0,  # Invalid: > 1.0
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_analyze_trends_invalid_interval(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test trend analysis with invalid interval."""
    response = await client.get(
        "/api/v2/analysis/trends",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "interval": "invalid",  # Invalid interval format
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_analyze_patterns_future_dates(client: AsyncClient):
    """Test pattern analysis with future dates."""
    now = datetime.now(timezone.utc)
    start_date = now + timedelta(days=1)
    end_date = start_date + timedelta(days=1)
    
    response = await client.post(
        "/api/v2/analysis/patterns",
        params={
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "min_support": 0.1,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_analyze_patterns_invalid_support(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test pattern analysis with invalid support threshold."""
    response = await client.post(
        "/api/v2/analysis/patterns",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "min_support": -0.1,  # Invalid: negative support
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_analyze_trends_too_long_interval(
    client: AsyncClient,
    event_search_params: Dict[str, str]
):
    """Test trend analysis with excessively long interval."""
    response = await client.get(
        "/api/v2/analysis/trends",
        params={
            "start_date": event_search_params["start_date"],
            "end_date": event_search_params["end_date"],
            "interval": "100d",  # Too long for the date range
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY