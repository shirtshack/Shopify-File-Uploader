from datetime import datetime
from io import StringIO

from google.api_core import page_iterator
from google.cloud import storage

from .constants import CSV_CACHE_BUCKET

from loguru import logger


def gcs_list_prefixes(client, bucket_name, prefix, delimiter):
    # Adapted from https://stackoverflow.com/a/59008580

    return page_iterator.HTTPIterator(
        client=client,
        api_request=client._connection.api_request,
        path=f"/b/{bucket_name}/o",
        items_key="prefixes",
        item_to_value=lambda iterator, item: item,
        extra_params={
            "projection": "noAcl",
            "prefix": prefix,
            "delimiter": delimiter,
        },
    )


class GCSFileCacheManager:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.buffer = StringIO()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.unique_filename = None

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def open(self, file_name, extension="tsv", mode="a"):
        unique_filename = f"{file_name}_{self.current_date}.{extension}"
        force_reload = unique_filename != self.unique_filename
        self.unique_filename = unique_filename
        if mode == "a":
            self._load_from_storage(force_reload)
        elif mode == "r":
            self._load_from_storage(force_reload)
            self.buffer.seek(0)
        elif mode == "w":
            self.buffer = StringIO()
        else:
            raise NotImplementedError("Only modes available are 'w', 'r', and 'a'")
        return self

    def close(self):
        self._upload_to_storage()

    def read(self, size=-1):
        return self.buffer.read(size)

    def readline(self, size=-1):
        return self.buffer.readline(size)

    def write(self, content):
        self.buffer.write(content)

    def _load_from_storage(self, force_reload: bool = True):
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(self.unique_filename)
        if blob.exists() and (self.buffer.getvalue() == "" or force_reload):
            logger.info("Downloading from bucket")
            content = blob.download_as_text()
            self.buffer = StringIO(content)
            self.buffer.seek(0, 2)  # Go to end, always appends

    def _upload_to_storage(self):
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(self.unique_filename)
        self.buffer.seek(0)
        blob.upload_from_string(self.buffer.read())
