from loguru import logger
from tempfile import NamedTemporaryFile


class SpreadsheetMaker(object):
    def make_spreadsheet(self, template, files_uploaded, product_title):
        logger.info("Making spreadsheet.")
        with NamedTemporaryFile(mode="w", delete=False) as f:
            for file in files_uploaded:
                f.writelines(template + f",s{file.name}, {product_title}\n")
            logger.info(f"Template written to {f.name}.")
            return f.name
