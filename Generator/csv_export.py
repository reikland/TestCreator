import csv
from datetime import datetime
from io import StringIO
from typing import List

from ftg.types import RankedTopic


def build_csv(top_topics: List[RankedTopic]) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["rank", "topic", "generated_at"])
    writer.writeheader()

    for row in top_topics:
        writer.writerow(
            {
                "rank": int(row["rank"]),
                "topic": str(row["topic"]),
                "generated_at": now,
            }
        )

    return buffer.getvalue()
