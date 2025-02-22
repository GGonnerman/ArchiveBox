__package__ = 'archivebox.parsers'


from typing import IO, Iterable
from datetime import datetime

from ..index.schema import Link
from ..util import (
    htmldecode,
    enforce_types,
    str_between,
)


@enforce_types
def parse_shaarli_rss_export(rss_file: IO[str], **_kwargs) -> Iterable[Link]:
    """Parse Shaarli-specific RSS XML-format files into links"""

    rss_file.seek(0)
    entries = rss_file.read().split('<entry>')[1:]
    for entry in entries:
        # example entry:
        # <entry>
        #   <title>Aktuelle Trojaner-Welle: Emotet lauert in gefÃ¤lschten Rechnungsmails | heise online</title>
        #   <link href="https://www.heise.de/security/meldung/Aktuelle-Trojaner-Welle-Emotet-lauert-in-gefaelschten-Rechnungsmails-4291268.html" />
        #   <id>https://demo.shaarli.org/?cEV4vw</id>
        #   <published>2019-01-30T06:06:01+00:00</published>
        #   <updated>2019-01-30T06:06:01+00:00</updated>
        #   <content type="html" xml:lang="en"><![CDATA[<div class="markdown"><p>&#8212; <a href="https://demo.shaarli.org/?cEV4vw">Permalink</a></p></div>]]></content>
        # </entry>

        trailing_removed = entry.split('</entry>', 1)[0]
        leading_removed = trailing_removed.strip()
        rows = leading_removed.split('\n')

        def get_row(key):
            return [r.strip() for r in rows if r.strip().startswith('<{}'.format(key))][0]

        def get_rows(key):
            return [r.strip() for r in rows if r.strip().startswith('<{}'.format(key))]

        title = str_between(get_row('title'), '<title>', '</title>').strip()
        url = str_between(get_row('link'), '<link href="', '" />')
        ts_str = str_between(get_row('published'), '<published>', '</published>')
        time = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S%z")
        tags = ",".join([htmldecode(str_between(tag_line, 'label="', '" />').strip()) for tag_line in get_rows('category')])

        try:
            url
        except nameerror:
            continue

        if url == None or url == "": continue

        yield Link(
            url=htmldecode(url),
            timestamp=str(time.timestamp()),
            title=htmldecode(title) or None,
            tags=tags or None,
            sources=[rss_file.name],
        )


KEY = 'shaarli_rss'
NAME = 'Shaarli RSS'
PARSER = parse_shaarli_rss_export
