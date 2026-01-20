from dataclasses import dataclass, field
from datetime import datetime
import pytz

@dataclass
class RawQuote:
    """Representation of a raw quotation."""
    text: str
    author: str
    author_url: str
    tags: list[str] = field(default_factory=list)
    utl_page: str = ""
    scraped_at: datetime = field(
        default_factory=lambda: datetime.now(pytz.timezone("Europe/Paris"))
    )



