import datetime as dt
import pytz
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarManager:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = Credentials.from_service_account_info(
            st.secrets["google"]["client_info"], scopes=SCOPES
        )
        return build("calendar", "v3", credentials=creds)

    def list_upcoming_events(self, max_results=10):
        chile_tz = pytz.timezone('America/Santiago')
        now = dt.datetime.now(chile_tz).isoformat()
        end = (dt.datetime.now(chile_tz) + dt.timedelta(days=5)).replace(
            hour=23, minute=59, second=0, microsecond=0
        ).isoformat()

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            return events
        except HttpError as error:
            st.error(f"Ocurrió un error: {error}")
            return []

    def create_event(self, summary, start_time, end_time, timezone='America/Santiago', attendees=None):
        event = {
            'summary': summary,
            'start': {'dateTime': start_time, 'timeZone': timezone},
            'end': {'dateTime': end_time, 'timeZone': timezone},
        }
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        try:
            event = self.service.events().insert(calendarId="primary", body=event).execute()
            st.success(f"Evento creado: {event.get('htmlLink')}")
        except HttpError as error:
            st.error(f"Ocurrió un error al crear el evento: {error}")

    def update_event(self, event_id, summary=None, start_time=None, end_time=None):
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        if summary:
            event['summary'] = summary
        if start_time:
            event['start']['dateTime'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        if end_time:
            event['end']['dateTime'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')

        updated_event = self.service.events().update(
            calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event

    def delete_event(self, event_id):
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True


# Solo ejecuta si corres localmente
if __name__ == "__main__":
    calendar = GoogleCalendarManager()
    eventos = calendar.list_upcoming_events()
    for e in eventos:
        start = e['start'].get('dateTime', e['start'].get('date'))
        print(start, e.get('summary', 'Sin título'), e.get('id', 'Sin ID'))
