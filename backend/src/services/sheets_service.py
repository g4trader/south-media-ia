import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src.config import settings
from src.models.campaign import CampaignType, VideoMetrics, DisplayMetrics
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Check if we have credentials file
            if settings.google_sheets_credentials_file and os.path.exists(settings.google_sheets_credentials_file):
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_sheets_credentials_file, self.scopes)
                self.credentials = flow.run_local_server(port=0)
            else:
                # Use service account if available
                if settings.google_application_credentials and os.path.exists(settings.google_application_credentials):
                    from google.oauth2 import service_account
                    self.credentials = service_account.Credentials.from_service_account_file(
                        settings.google_application_credentials, scopes=self.scopes)
                else:
                    logger.warning("No Google Sheets credentials found. Using mock data.")
                    return
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=self.credentials)
            
        except Exception as e:
            logger.error(f"Error authenticating with Google Sheets: {e}")
            self.service = None
    
    def read_sheet_data(self, spreadsheet_id: str, sheet_name: str, range_name: str = None) -> Optional[pd.DataFrame]:
        """Read data from a Google Sheet"""
        if not self.service:
            logger.warning("Google Sheets service not available. Returning mock data.")
            return self._get_mock_data()
        
        try:
            # Determine the range to read
            if range_name:
                range_to_read = f"{sheet_name}!{range_name}"
            else:
                range_to_read = sheet_name
            
            # Read the data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_to_read
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning(f"No data found in sheet {sheet_name}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            return df
            
        except HttpError as error:
            logger.error(f"Error reading Google Sheet: {error}")
            return None
    
    def process_video_campaign_data(self, df: pd.DataFrame, campaign_id: str) -> List[VideoMetrics]:
        """Process video campaign data from Google Sheets"""
        metrics = []
        
        try:
            # Map column names (case-insensitive)
            column_mapping = {
                'day': 'date',
                'video completion rate %': 'completion_rate',
                'video skip rate %': 'skip_rate',
                'video start rate %': 'start_rate',
                '25% video complete': 'completions_25',
                '50% video complete': 'completions_50',
                '75% video complete': 'completions_75',
                '100% complete': 'completions_100',
                'video starts': 'video_starts',
                'valor investido': 'investment',
                'criativo': 'creative'
            }
            
            # Rename columns
            df.columns = [col.lower().strip() for col in df.columns]
            df = df.rename(columns=column_mapping)
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    date_str = str(row.get('date', ''))
                    if not date_str or date_str == 'nan':
                        continue
                    
                    # Try different date formats
                    date = None
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']:
                        try:
                            date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if not date:
                        continue
                    
                    # Create metrics object
                    metric = VideoMetrics(
                        date=date,
                        completion_rate=float(row.get('completion_rate', 0)) / 100,
                        skip_rate=float(row.get('skip_rate', 0)) / 100,
                        start_rate=float(row.get('start_rate', 0)) / 100,
                        completions_25=int(row.get('completions_25', 0)),
                        completions_50=int(row.get('completions_50', 0)),
                        completions_75=int(row.get('completions_75', 0)),
                        completions_100=int(row.get('completions_100', 0)),
                        video_starts=int(row.get('video_starts', 0)),
                        investment=float(str(row.get('investment', 0)).replace('R$', '').replace(',', '.').strip()),
                        creative=row.get('creative', None)
                    )
                    
                    metrics.append(metric)
                    
                except Exception as e:
                    logger.error(f"Error processing row {row}: {e}")
                    continue
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error processing video campaign data: {e}")
            return []
    
    def process_display_campaign_data(self, df: pd.DataFrame, campaign_id: str) -> List[DisplayMetrics]:
        """Process display campaign data from Google Sheets"""
        metrics = []
        
        try:
            # Map column names (case-insensitive)
            column_mapping = {
                'day': 'date',
                'line item': 'line_item',
                'creative': 'creative',
                'valor investido': 'investment',
                'imps': 'impressions',
                'clicks': 'clicks',
                'ctr': 'ctr',
                'cpm': 'cpm',
                'cpc': 'cpc'
            }
            
            # Rename columns
            df.columns = [col.lower().strip() for col in df.columns]
            df = df.rename(columns=column_mapping)
            
            for _, row in df.iterrows():
                try:
                    # Parse date
                    date_str = str(row.get('date', ''))
                    if not date_str or date_str == 'nan':
                        continue
                    
                    # Try different date formats
                    date = None
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']:
                        try:
                            date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if not date:
                        continue
                    
                    # Create metrics object
                    metric = DisplayMetrics(
                        date=date,
                        creative=str(row.get('creative', '')),
                        impressions=int(row.get('impressions', 0)),
                        clicks=int(row.get('clicks', 0)),
                        ctr=float(str(row.get('ctr', 0)).replace(',', '.')),
                        cpm=float(str(row.get('cpm', 0)).replace('R$', '').replace(',', '.').strip()),
                        cpc=float(str(row.get('cpc', 0)).replace(',', '.')),
                        investment=float(str(row.get('investment', 0)).replace('R$', '').replace(',', '.').strip())
                    )
                    
                    metrics.append(metric)
                    
                except Exception as e:
                    logger.error(f"Error processing row {row}: {e}")
                    continue
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error processing display campaign data: {e}")
            return []
    
    def _get_mock_data(self) -> pd.DataFrame:
        """Return mock data for development/testing"""
        # Mock video campaign data
        mock_data = {
            'Day': ['2025-08-01', '2025-08-02', '2025-08-03'],
            'Video Completion Rate %': ['92.5', '93.1', '91.8'],
            'Video Skip Rate %': ['0', '0', '0'],
            'Video Start Rate %': ['100', '100', '100'],
            '25% Video Complete': ['4500', '4600', '4400'],
            '50% Video Complete': ['4400', '4500', '4300'],
            '75% Video Complete': ['4300', '4400', '4200'],
            '100% Complete': ['4200', '4300', '4100'],
            'Video Starts': ['4800', '4900', '4700'],
            'Valor investido': ['R$ 1.300,00', 'R$ 1.350,00', 'R$ 1.280,00']
        }
        
        return pd.DataFrame(mock_data)

# Global sheets service instance
sheets_service = GoogleSheetsService()
