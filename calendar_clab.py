import os
import json
import datetime as dt
import pytz  # Para manejar zonas horarias
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarManager:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        # Si el archivo token.json existe, usa esas credenciales
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Aquí se autentica usando el secreto desde Streamlit Secrets
                client_info = json.loads(st.secrets["google"]["client_info"])
                with open("client_secrets_temp.json", "w") as f:
                    json.dump(client_info, f)

                flow = InstalledAppFlow.from_client_secrets_file("client_secrets_temp.json", SCOPES)
                flow.run_console()

            # Guardar las credenciales para futuras ejecuciones
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        # Devuelve el servicio de Google Calendar autenticado
        return build("calendar", "v3", credentials=creds)

    def list_upcoming_events(self, max_results=10):
        chile_tz = pytz.timezone('America/Santiago')

        now = dt.datetime.now(chile_tz).isoformat()
        end = (dt.datetime.now(chile_tz) + dt.timedelta(days=5)).replace(
            hour=23, minute=59, second=0, microsecond=0
        ).isoformat()

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event.get('summary', 'Sin título'), event.get('id', 'Sin ID'))

        return events

    def create_event(self, summary, start_time, end_time, timezone, attendees=None):
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            }
        }

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        try:
            event = self.service.events().insert(calendarId="primary", body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
        except HttpError as error:
            print(f"An error has occurred: {error}")

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


# Ejecutar la clase y ver eventos
if __name__ == "__main__":
    calendar = GoogleCalendarManager()
    calendar.list_upcoming_events()