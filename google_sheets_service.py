"""Google Sheets integration service.

This module provides the :class:`GoogleSheetsService` which encapsulates the
authentication and data-access helpers used across the project.  The service is
able to authenticate using Google Cloud service account credentials provided
via environment variables (recommended for Cloud Run) or a local JSON file
(used in development).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

import pandas as pd
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Helper wrapper around the Google Sheets API.

    The service attempts to authenticate automatically during initialisation.
    It supports two strategies:

    * ``GOOGLE_SERVICE_ACCOUNT_JSON`` (or compatible) environment variables
      containing the JSON credentials.
    * ``GOOGLE_APPLICATION_CREDENTIALS`` (or compatible) environment variables
      pointing to the service account JSON file on disk.

    If authentication fails the error is logged and ``is_configured`` returns
    ``False``.  Consumers can still create the class safely and check for
    configuration before attempting API calls.
    """

    SCOPES: Iterable[str] = (
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    )

    _SERVICE_ACCOUNT_ENV_KEYS: Iterable[str] = (
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        "GOOGLE_SERVICE_ACCOUNT_INFO",
        "GOOGLE_SHEETS_SERVICE_ACCOUNT",
    )

    _SERVICE_ACCOUNT_FILE_ENV_KEYS: Iterable[str] = (
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_SHEETS_CREDENTIALS_FILE",
        "GOOGLE_CREDENTIALS_FILE",
    )

    def __init__(self) -> None:
        self._service = None
        self._auth_error: Optional[Exception] = None
        self._credentials_source: Optional[str] = None

        # Ensure logging has at least a default configuration
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO)

        self._authenticate()

    # ------------------------------------------------------------------
    # Authentication helpers
    # ------------------------------------------------------------------
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets using service account credentials."""

        try:
            credentials = self._load_credentials()
            if not credentials:
                logger.warning(
                    "Google Sheets credentials not configured. Set a service account "
                    "JSON via environment variable or provide a credentials file."
                )
                return

            self._service = build(
                "sheets",
                "v4",
                credentials=credentials,
                cache_discovery=False,
            )
            logger.info(
                "✅ Google Sheets autenticado com sucesso (%s)",
                self._credentials_source or "unknown source",
            )
        except (GoogleAuthError, OSError, ValueError, HttpError) as exc:
            self._auth_error = exc
            logger.error("❌ Erro na autenticação com Google Sheets: %s", exc, exc_info=True)
            self._service = None
        except Exception as exc:  # pragma: no cover - defensive logging
            self._auth_error = exc
            logger.error(
                "❌ Erro inesperado durante autenticação com Google Sheets: %s",
                exc,
                exc_info=True,
            )
            self._service = None

    def _load_credentials(self):
        """Try to load service account credentials from supported sources."""

        # First check for JSON provided directly via environment variables.
        for env_key in self._SERVICE_ACCOUNT_ENV_KEYS:
            raw_value = os.environ.get(env_key)
            if not raw_value:
                continue

            try:
                credentials_dict = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                logger.error(
                    "⚠️ Conteúdo inválido em %s: %s", env_key, exc, exc_info=True
                )
                self._auth_error = exc
                continue

            self._credentials_source = f"env:{env_key}"
            return service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=self.SCOPES,
            )

        # Then fall back to environment variables pointing to credential files.
        for env_key in self._SERVICE_ACCOUNT_FILE_ENV_KEYS:
            path = os.environ.get(env_key)
            if not path:
                continue

            expanded_path = os.path.expanduser(path)
            if not os.path.exists(expanded_path):
                logger.error(
                    "⚠️ Arquivo de credenciais não encontrado: %s (de %s)",
                    expanded_path,
                    env_key,
                )
                continue

            self._credentials_source = f"file:{expanded_path}"
            return service_account.Credentials.from_service_account_file(
                expanded_path,
                scopes=self.SCOPES,
            )

        # Finally, look for local development files "credentials.json" or "service-account-key.json".
        for filename in ["credentials.json", "service-account-key.json"]:
            default_path = os.path.join(os.getcwd(), filename)
            if os.path.exists(default_path):
                self._credentials_source = f"file:{default_path}"
                logger.info(f"✅ Usando credenciais do arquivo: {filename}")
                return service_account.Credentials.from_service_account_file(
                    default_path,
                    scopes=self.SCOPES,
                )

        # Try to download credentials from Google Cloud Storage (for Cloud Run)
        try:
            logger.info("🔄 Tentando baixar credenciais do Google Cloud Storage...")
            import google.cloud.storage
            bucket_name = "south-media-credentials"
            blob_name = "service-account-key.json"
            
            logger.info(f"🪣 Criando cliente do Storage para bucket: {bucket_name}")
            storage_client = google.cloud.storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Download to a temporary file
            temp_credentials_path = "/tmp/service-account-key.json"
            logger.info(f"⬇️ Baixando {blob_name} para {temp_credentials_path}")
            blob.download_to_filename(temp_credentials_path)
            
            self._credentials_source = f"gcs:{bucket_name}/{blob_name}"
            logger.info(f"✅ Usando credenciais do Google Cloud Storage: {bucket_name}/{blob_name}")
            return service_account.Credentials.from_service_account_file(
                temp_credentials_path,
                scopes=self.SCOPES,
            )
        except Exception as e:
            logger.error(f"❌ Erro ao baixar credenciais do GCS: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")

        # Try Application Default Credentials as fallback
        try:
            import google.auth
            credentials, project = google.auth.default(scopes=self.SCOPES)
            if credentials:
                self._credentials_source = "application_default"
                logger.info("✅ Usando Application Default Credentials")
                return credentials
        except Exception as e:
            logger.warning(f"⚠️ Application Default Credentials não disponíveis: {e}")

        return None

    # ------------------------------------------------------------------
    # Public helpers used throughout the project
    # ------------------------------------------------------------------
    def is_configured(self) -> bool:
        """Return ``True`` when the service is authenticated and ready."""

        return self._service is not None

    def test_connection(self) -> str:
        """Check the connectivity with Google Sheets.

        Returns a short status string:
        ``"connected"`` when the service is ready and the optional test sheet is
        accessible, ``"unauthorized"`` when Google returns a 401/403 response,
        ``"error"`` when an unexpected error occurs and ``"not_configured"`` when
        authentication has not completed successfully.
        """

        if not self.is_configured():
            return "not_configured"

        test_sheet_id = os.environ.get("GOOGLE_SHEETS_TEST_SHEET_ID")
        if not test_sheet_id:
            # Nothing else to validate – authentication already succeeded.
            return "connected"

        try:
            self._service.spreadsheets().get(spreadsheetId=test_sheet_id).execute()
            return "connected"
        except HttpError as exc:  # pragma: no cover - requires external API call
            status = getattr(exc.resp, "status", None)
            if status in {401, 403}:
                logger.error(
                    "❌ Service account sem permissão para acessar a planilha de teste %s",
                    test_sheet_id,
                )
                return "unauthorized"
            logger.error(
                "❌ Erro ao testar conexão com Google Sheets (%s): %s", status, exc
            )
            return "error"
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("❌ Erro inesperado ao testar conexão: %s", exc, exc_info=True)
            return "error"

    def get_sheet_metadata(self, sheet_id: str) -> Optional[Dict[str, Any]]:
        """Return spreadsheet metadata when accessible."""

        if not self.is_configured():
            return None

        try:
            return self._service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        except HttpError as exc:
            logger.error(
                "❌ Erro ao buscar metadados da planilha %s: %s", sheet_id, exc
            )
            return None
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "❌ Erro inesperado ao buscar metadados da planilha %s: %s",
                sheet_id,
                exc,
                exc_info=True,
            )
            return None

    def get_sheet_name_by_gid(self, sheet_id: str, gid: Any) -> Optional[str]:
        """Translate a sheet GID to its human readable title."""

        metadata = self.get_sheet_metadata(sheet_id)
        if not metadata:
            return None

        for sheet in metadata.get("sheets", []):
            properties = sheet.get("properties", {})
            if str(properties.get("sheetId")) == str(gid):
                return properties.get("title")
        return None

    def validate_sheet_access(self, sheet_id: str, gid: Any = None) -> bool:
        """Return ``True`` when the spreadsheet (and optional tab) is accessible."""

        if not self.is_configured():
            logger.warning("⚠️ Google Sheets Service não configurado")
            return False

        try:
            metadata = self.get_sheet_metadata(sheet_id)
            if not metadata:
                return False

            if gid is None:
                return True

            sheet_name = self.get_sheet_name_by_gid(sheet_id, gid)
            if sheet_name:
                return True

            logger.warning(
                "⚠️ Aba com GID %s não encontrada na planilha %s", gid, sheet_id
            )
            return False
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "❌ Erro ao validar acesso à planilha %s (gid %s): %s",
                sheet_id,
                gid,
                exc,
                exc_info=True,
            )
            return False

    def read_sheet_data(
        self,
        sheet_id: str,
        sheet_name: Optional[str] = None,
        gid: Any = None,
        range_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """Read data from a Google Sheet and return it as :class:`DataFrame`."""

        if not self.is_configured():
            logger.warning("⚠️ Tentativa de leitura sem credenciais configuradas")
            return pd.DataFrame()

        target_range = range_name
        resolved_sheet_name = sheet_name

        if gid and not sheet_name:
            resolved_sheet_name = self.get_sheet_name_by_gid(sheet_id, gid)
            if not resolved_sheet_name:
                logger.warning(
                    "⚠️ Não foi possível localizar o GID %s na planilha %s",
                    gid,
                    sheet_id,
                )
                return pd.DataFrame()

        if not target_range:
            if resolved_sheet_name:
                target_range = f"'{resolved_sheet_name}'!A:ZZ"
            else:
                target_range = "A:ZZ"

        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(spreadsheetId=sheet_id, range=target_range)
                .execute()
            )
        except HttpError as exc:  # pragma: no cover - requires external API
            logger.error(
                "❌ Erro HTTP ao ler planilha %s (%s): %s",
                sheet_id,
                target_range,
                exc,
            )
            return pd.DataFrame()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(
                "❌ Erro inesperado ao ler planilha %s (%s): %s",
                sheet_id,
                target_range,
                exc,
                exc_info=True,
            )
            return pd.DataFrame()

        values = result.get("values", [])
        if not values:
            logger.info(
                "ℹ️ Planilha %s (%s) não contém dados", sheet_id, target_range
            )
            return pd.DataFrame()

        header = values[0]
        data_rows = values[1:]
        if not header:
            # Without a header we simply return the raw values.
            return pd.DataFrame(values)

        # Normalise the header length when rows have different sizes.
        normalised_rows = [
            row + [None] * (len(header) - len(row)) if len(row) < len(header) else row
            for row in data_rows
        ]

        df = pd.DataFrame(normalised_rows, columns=header)
        logger.info(
            "✅ %d linhas carregadas da planilha %s (%s)",
            len(df),
            sheet_id,
            resolved_sheet_name or target_range,
        )
        return df

    def get_campaign_data(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate Google Sheets data for a campaign configuration."""

        if not campaign:
            return {}

        channels_data: Dict[str, Any] = {}
        for channel in campaign.get("channels", []):
            channel_name = channel.get("name") or f"channel_{len(channels_data) + 1}"
            sheet_id = channel.get("sheet_id")
            sheet_name = channel.get("sheet_name")
            gid = channel.get("gid")

            if not sheet_id:
                logger.warning(
                    "⚠️ Canal '%s' ignorado – ID da planilha não informado", channel_name
                )
                channels_data[channel_name] = {
                    "sheet_id": None,
                    "data": [],
                    "retrieved_at": None,
                }
                continue

            df = self.read_sheet_data(sheet_id, sheet_name=sheet_name, gid=gid)
            channels_data[channel_name] = {
                "sheet_id": sheet_id,
                "sheet_name": sheet_name or self.get_sheet_name_by_gid(sheet_id, gid)
                if gid
                else sheet_name,
                "gid": gid,
                "data": df.to_dict(orient="records") if not df.empty else [],
                "retrieved_at": datetime.utcnow().isoformat(),
            }

        return {
            "campaign_id": campaign.get("id"),
            "campaign_name": campaign.get("name"),
            "period": {
                "start": campaign.get("start_date"),
                "end": campaign.get("end_date"),
            },
            "total_budget": campaign.get("total_budget"),
            "channels": channels_data,
            "generated_at": datetime.utcnow().isoformat(),
        }


__all__ = ["GoogleSheetsService"]
