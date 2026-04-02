import os
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from loguru import logger
from tempfile import NamedTemporaryFile
import streamlit as st

creds, project = google.auth.default()


class TemplateFolder(object):
    """Class to represent a Google Drive folder."""

    folder_id = "1Q3QEHV0mIw3ntM1yDxOy3R80eVttWzCQ"

    def __str__(self):
        return f"{self.folder_name} ({self.folder_id})"

    def __init__(self) -> None:
        super().__init__()
        self.service = build("drive", "v3", credentials=creds)

    def get_template_list(self):
        """Get the list of templates in the folder."""

        # Call the Drive v3 API
        results = (
            self.service.files()
            .list(
                q="'" + self.folder_id + "' in parents",
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType)",
            )
            .execute()
        )
        items = results.get("files", [])
        xlsmfiles = [i for i in items if i["name"].endswith(".xlsm")]
        return xlsmfiles

    def download_template(self, template_id):
        """Get the template with the given ID.
        Returns the path to the downloaded file.
        """
        filename = f"/tmp/{template_id}"
        if os.path.isfile(filename):
            return filename
        request = self.service.files().get_media(fileId=template_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.debug(f"Download {int(status.progress() * 100)}.")

        with open(filename, mode="w+b") as f:
            f.write(file.getvalue())
            return filename


class RestrictedWords(object):
    list_file_id = "11oAZTfz2wUSt36QPN3urdCgAj_7w6Uwke7qkxpVWvQk" # File "Configs/Trademark Terms"

    def __init__(self) -> None:
        super().__init__()
        self.service = build("sheets", "v4", credentials=creds)

    def get_trademark_words(self):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=self.list_file_id, range="A:A").execute()
        )
        values = result.get("values", [])
        return [x[0] for x in values]


class BrandsBuckets(object):
    list_file_id = "1thLibP1tVESTuaaSFQAj2Rz8e7qD8GHb_2S5eLXYDMI" # File "Configs/Brands-Buckets"

    def __init__(self) -> None:
        super().__init__()
        self.service = build("sheets", "v4", credentials=creds)

    def get_brands_buckets(self):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=self.list_file_id, range="A:B").execute()
        )
        values = result.get("values", [])[1:]
        return {value[0]:value[1] for value in values}
    
    def get_brands_shopify(self):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=self.list_file_id, range="A:C").execute()
        )
        values = result.get("values", [])[1:]

        brands = {}
        for value in values:
            try:
                brands[value[0]] = value[2]
            except IndexError:
                brands[value[0]] = 'Shirtshack'

        return brands


class Colors(object):
    list_file_id = "1jTl1FjT8k-1RokDnl2eozR1OgTe4NSlPlCML0IvjS0Q" # File "Configs/Colors"

    def __init__(self) -> None:
        super().__init__()
        self.service = build("sheets", "v4", credentials=creds)

    def get_colors(self):
        sheet = self.service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=self.list_file_id, range="A:B").execute()
        )
        values = result.get("values", [])[1:]
        return {value[0]: value[1] for value in values}