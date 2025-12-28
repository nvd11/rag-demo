

from loaders.base_loader import BaseLoader


class PDFLoader(BaseLoader, str):

    def supported_extensions(self) -> list[str]:
        return ['pdf']