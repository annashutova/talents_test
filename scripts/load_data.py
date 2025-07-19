import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Any

from sqlalchemy import insert

from webapp.db.postgres import async_session
from webapp.models.meta import metadata


parser = argparse.ArgumentParser()

parser.add_argument('fixtures', nargs='+', help='<Required> Set flag')

args = parser.parse_args()


async def main(fixtures: List[str]) -> None:
    for fixture in fixtures:
        fixture_path = Path(fixture)
        model = metadata.tables[fixture_path.stem]

        with open(fixture_path, 'r') as file:
            data = json.load(file)

        # Convert date strings to datetime objects
        for entity in data:
            for key in entity:
                try:
                    new_date = datetime.strptime(entity[key], '%Y-%m-%dT%H:%M:%S')
                    entity[key] = new_date
                except Exception:
                    pass

        async with async_session() as session:
            await session.execute(insert(model).values(data))
            await session.commit()


if __name__ == '__main__':
    asyncio.run(main(args.fixtures))
