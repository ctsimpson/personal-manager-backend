"""
Google Calendar API client.

This module provides a client for interacting with the Google Calendar API.
"""

import os
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)


class GoogleCalendarClient:
    """Client for interacting with Google Calendar API."""

    # If modifying these scopes, delete the token file
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(
        self, credentials_file: Optional[str] = None, token_file: str = "token.json"
    ):
        """
        Initialize Google Calendar client.

        Args:
            credentials_file: Path to credentials file (defaults to settings)
            token_file: Path to token file
        """
        self.credentials_file = credentials_file or settings.GOOGLE_CREDENTIALS_FILE
        self.token_file = token_file
        self.service = None

    async def authenticate(self) -> None:
        """
        Authenticate with Google Calendar API.

        This follows the OAuth 2.0 flow for installed applications.
        """
        creds = None

        # Check if token file exists
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_info(
                info=json.loads(open(self.token_file).read()), scopes=self.SCOPES
            )

        # If credentials don't exist or are invalid, go through OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())

        # Build the service
        self.service = build("calendar", "v3", credentials=creds)

    async def ensure_authenticated(self) -> None:
        """Ensure the client is authenticated before making API calls."""
        if not self.service:
            await self.authenticate()

    async def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
        single_events: bool = True,
        order_by: str = "startTime",
    ) -> List[Dict[str, Any]]:
        """
        List events from Google Calendar.

        Args:
            calendar_id: Calendar ID (default is primary)
            time_min: Minimum time for events
            time_max: Maximum time for events
            max_results: Maximum number of results to return
            single_events: Whether to expand recurring events
            order_by: Order of events

        Returns:
            List[Dict[str, Any]]: List of events

        Raises:
            Exception: If authentication fails
        """
        await self.ensure_authenticated()

        # Set default time range if not provided
        if not time_min:
            time_min = datetime.utcnow()
        if not time_max:
            time_max = time_min + timedelta(days=30)

        # Format times for API
        time_min_rfc = time_min.isoformat() + "Z"
        time_max_rfc = time_max.isoformat() + "Z"

        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min_rfc,
                    timeMax=time_max_rfc,
                    maxResults=max_results,
                    singleEvents=single_events,
                    orderBy=order_by,
                )
                .execute()
            )

            events = events_result.get("items", [])

            # Transform events to a more usable format
            transformed_events = []
            for event in events:
                transformed_event = {
                    "id": event.get("id", ""),
                    "summary": event.get("summary", ""),
                    "description": event.get("description", ""),
                    "start": event.get("start", {}).get(
                        "dateTime", event.get("start", {}).get("date", "")
                    ),
                    "end": event.get("end", {}).get(
                        "dateTime", event.get("end", {}).get("date", "")
                    ),
                    "location": event.get("location", ""),
                    "status": event.get("status", ""),
                    "organizer": event.get("organizer", {}).get("email", ""),
                    "attendees": [
                        attendee.get("email", "")
                        for attendee in event.get("attendees", [])
                    ],
                }
                transformed_events.append(transformed_event)

            return transformed_events

        except HttpError as error:
            logger.error(f"Error fetching events: {error}")
            raise Exception(f"Failed to fetch events: {error}")

    async def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary",
    ) -> Dict[str, Any]:
        """
        Create a new event in Google Calendar.

        Args:
            summary: Event summary/title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            attendees: List of attendee emails
            calendar_id: Calendar ID

        Returns:
            Dict[str, Any]: Created event

        Raises:
            Exception: If event creation fails
        """
        await self.ensure_authenticated()

        # Format event data
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "America/Los_Angeles",
            },
        }

        if description:
            event["description"] = description

        if location:
            event["location"] = location

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        try:
            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event, sendUpdates="all")
                .execute()
            )

            return {
                "id": created_event.get("id", ""),
                "summary": created_event.get("summary", ""),
                "description": created_event.get("description", ""),
                "start": created_event.get("start", {}).get("dateTime", ""),
                "end": created_event.get("end", {}).get("dateTime", ""),
                "location": created_event.get("location", ""),
                "status": created_event.get("status", ""),
                "organizer": created_event.get("organizer", {}).get("email", ""),
                "attendees": [
                    attendee.get("email", "")
                    for attendee in created_event.get("attendees", [])
                ],
            }

        except HttpError as error:
            logger.error(f"Error creating event: {error}")
            raise Exception(f"Failed to create event: {error}")

    async def update_event(
        self, event_id: str, calendar_id: str = "primary", **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing event in Google Calendar.

        Args:
            event_id: Event ID to update
            calendar_id: Calendar ID
            **kwargs: Event fields to update

        Returns:
            Dict[str, Any]: Updated event

        Raises:
            Exception: If event update fails
        """
        await self.ensure_authenticated()

        try:
            # Get the current event
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            # Update fields
            for key, value in kwargs.items():
                if key in ["start", "end"]:
                    if isinstance(value, datetime):
                        event[key] = {
                            "dateTime": value.isoformat(),
                            "timeZone": "America/Los_Angeles",
                        }
                elif key == "attendees" and isinstance(value, list):
                    event[key] = [{"email": email} for email in value]
                else:
                    event[key] = value

            # Update the event
            updated_event = (
                self.service.events()
                .update(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event,
                    sendUpdates="all",
                )
                .execute()
            )

            return {
                "id": updated_event.get("id", ""),
                "summary": updated_event.get("summary", ""),
                "description": updated_event.get("description", ""),
                "start": updated_event.get("start", {}).get("dateTime", ""),
                "end": updated_event.get("end", {}).get("dateTime", ""),
                "location": updated_event.get("location", ""),
                "status": updated_event.get("status", ""),
                "organizer": updated_event.get("organizer", {}).get("email", ""),
                "attendees": [
                    attendee.get("email", "")
                    for attendee in updated_event.get("attendees", [])
                ],
            }

        except HttpError as error:
            logger.error(f"Error updating event: {error}")
            raise Exception(f"Failed to update event: {error}")

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> bool:
        """
        Delete an event from Google Calendar.

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID

        Returns:
            bool: True if deleted successfully

        Raises:
            Exception: If event deletion fails
        """
        await self.ensure_authenticated()

        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id, sendUpdates="all"
            ).execute()

            return True

        except HttpError as error:
            logger.error(f"Error deleting event: {error}")
            raise Exception(f"Failed to delete event: {error}")
