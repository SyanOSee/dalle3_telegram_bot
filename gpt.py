# Standard
from datetime import datetime, timezone, timedelta
from enum import Enum
import os

# Project
import config as cf
from logger import gpt_logger


# Third-party
os.environ['OPENAI_API_KEY'] = cf.api.get('token', '')
from openai import AsyncOpenAI


class Size(Enum):
    S_256 = '256x256'
    S_512 = '512x512'
    S_1024 = '1024x1024'
    S_1024_x_1792 = '1024×1792'
    S_1792_x_1024 = '1792×1024'


class Model(Enum):
    DALLE_2 = 'dall-e-2'
    DALLE_3 = 'dall-e-3'


_client = AsyncOpenAI(
    api_key=cf.api.get('token', ''),
    base_url=cf.api.get('base_url', '')
)


async def send_dalle(
        prompt: str, size: Size | str,
        model: Model | str, quantity: int
) -> dict:
    """
    Send a request to generate images using OpenAI's DALL-E model.

    Args:
        prompt (str): The prompt for generating the images.
        size (Size | str): The size of the image to be generated.
        model (Model | str): The model to use for image generation.
        quantity (int): The number of images to generate.

    Returns:
        dict: The response data from the OpenAI API.
    """
    response = await _client.images.generate(
        model=model.value if model is Model else model,
        prompt=prompt,
        n=quantity,
        size=size.value if size is Size else size,
    )

    gpt_logger.info(f'GPT response {datetime.now()}: {response.model_dump()}')
    return response.model_dump()
