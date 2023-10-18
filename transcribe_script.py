import httpx
import io
import aiohttp
import asyncio
import argparse
from sniffio import current_async_library
from pydub import AudioSegment


parser = argparse.ArgumentParser()
parser.add_argument("--file_path", type=str,
                    help="the path of file", default="")
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
        print(response.status_code)
        # print(response.text)
        print(response.json())
    return

async def process_audio():
    audio = AudioSegment.from_file(args.file_path)
    intervals = 20 * 1000
    for i in range(int(len(audio) / intervals)):
        start_time = intervals * i
        end_time = (intervals) * (i + 1)
        if end_time > len(audio):
            end_time = len(audio)
        segment = audio[start_time: end_time]
        buffer = io.BytesIO()
        segment.export(buffer, format="wav")
        buffer.name = "audio.mp3"
        print(buffer.getbuffer().nbytes / 1024 / 1024)
        res = await transcribe(
            "https://salamer-whisper-axnqlaey.leapcell.dev/transcribe_json",
            buffer,
        )
        print(res)
        

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


# # @asyncio.coroutine
# async def invoke():
#     # print("xxxx")
#     async with httpx.AsyncClient() as client:
#         # print("xqeqwe")
#         res = await client.get(
#             "https://salamer-whisper-axnqlaey.leapcell.dev"
#         )
#         print(res.status_code)
#         return res.status_code
#     return

async def invoke():
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get('https://salamer-whisper-axnqlaey.leapcell.dev') as resp:
                print(resp.status)
                # print(await resp.text())
    except Exception as e:
        print("failed")


async def bench():
    concurrency = 5000
    jobs = [
        # asyncio.create_task(invoke())
        invoke()
        for i in range(concurrency)
        ]
    # async with asyncio.TaskGroup() as tg:
    # for i in range(concurrency):
    # tg.create_task(invoke())
    # invoke()
    # print([i.result() for i in jobs])
    # for task in asyncio.as_completed(jobs):
    # print(task.result())
    # return await asyncio.gather(
    #     *jobs,
    #     return_exception=True
    # )
    fut = await asyncio.gather(*jobs, return_exceptions=False)

    return fut


def bench_main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bench())
    loop.close()
    # asyncio.run(bench())
    # bench()

def process_audio_main():
    asyncio.run(process_audio())

if __name__ == "__main__":
    # main()
    # bench_main()
    process_audio_main()
