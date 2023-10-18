import httpx
import io
import asyncio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--file_path", type=str, help="the path of file", default="")
args = parser.parse_args()

async def transcribe(
    url: str,
    audio: io.BytesIO
):
    async with httpx.AsyncClient() as client:
        forms = {
            "file": audio,
        }
        response = await client.post(
            url=url,
            files=forms,
            timeout=60 * 6,
        )
        print(response.json())
    return

def main():
    with open(args.file_path, "rb") as f:
        buf = io.BytesIO(f.read())
        buf.name = "audio.mp3"
    asyncio.run(
        transcribe(
            "http://localhost:8000/transcribe_json",
            buf,
        )
    )

if __name__ == "__main__":
    main()