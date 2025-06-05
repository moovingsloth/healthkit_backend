from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.credentials = Credentials.from_service_account_file(
            settings.GOOGLE_SHEETS_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = settings.GOOGLE_SHEETS_ID

    async def update_health_metrics(self, metrics: dict):
        """건강 데이터를 Google Sheets에 업데이트"""
        try:
            values = [
                [
                    metrics['user_id'],
                    metrics['timestamp'].isoformat(),
                    metrics['heart_rate'],
                    metrics['sleep_hours'],
                    metrics['steps'],
                    metrics['stress_level'],
                    metrics['activity_level'],
                    metrics['caffeine_intake'],
                    metrics['water_intake']
                ]
            ]
            
            body = {
                'values': values
            }
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='HealthMetrics!A:I',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Health metrics updated for user {metrics['user_id']}")
        except Exception as e:
            logger.error(f"Error updating health metrics: {str(e)}")
            raise

    async def update_prediction(self, user_id: str, prediction: dict):
        """예측 결과를 Google Sheets에 업데이트"""
        try:
            values = [
                [
                    user_id,
                    datetime.now().isoformat(),
                    prediction['concentration_score'],
                    prediction['confidence'],
                    '|'.join(prediction['recommendations'])
                ]
            ]
            
            body = {
                'values': values
            }
            
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Predictions!A:E',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Prediction updated for user {user_id}")
        except Exception as e:
            logger.error(f"Error updating prediction: {str(e)}")
            raise 