import json
from pathlib import Path



GENERATED_DIR = Path("/tmp/generated")
GENERATED_DIR.mkdir(exist_ok=True)


def generate_media(ai_media, filename):
    output_path = (
        GENERATED_DIR /
        f"{Path(filename).stem}.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            ai_media,
            file,
            ensure_ascii=False,
            indent=4
        )

    return output_path
