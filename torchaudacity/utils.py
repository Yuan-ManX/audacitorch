from pathlib import Path
import random
from typing import Tuple

import torch
import json

def save_model(model: torch.jit.ScriptModule, metadata: dict, root_dir: Path):
  """
  Save a compiled torch.jit.ScriptModule, along with a metadata dictionary.

  Args:
      model: your Audacity-ready serialized model, using either torch.jit.trace or torch.jit.script. 
        Should derive from torchaudacity.WaveformToWaveformBase or torchaudacity.WaveformToLabelsBase.
      metadata: a metadata dictionary. Shoule be validated using torchaudio.utils.validate_metadata()

  Returns:
    Will create the following files: 
    ```
      root_dir/
      root_dir/model.pt
      root_dir/metadata.json
    ```
  """
  root_dir.mkdir(exist_ok=True, parents=True)

  # save model and metadata!
  torch.jit.save(model, root_dir / 'model.pt')

  with open(root_dir / 'metadata.json', 'w') as f:
    json.dump(metadata, f)

def get_example_inputs(multichannel: bool = False):
  """
  returns a list of possible input tensors for an AudacityModel. 

  Possible inputs are audio tensors with shape (n_channels, n_samples). 
  If multichannel == False, n_channels will always be 1. 
  """
  max_channels = 10 if multichannel else 1
  num_inputs = 10
  channels = [random.randint(1, max_channels) for _ in range(num_inputs)]
  sizes = [random.randint(2048, 396000) for _ in range(num_inputs)]
  return [
    torch.randn((c, s)) for c, s in  zip(channels, sizes)
  ]

def load_schema():
    """loads the audacity deep learning json schema for metadata"""
    from urllib.request import urlopen

    url = 'https://raw.githubusercontent.com/hugofloresgarcia/audacity/deeplearning/deeplearning-models/modelcard-schema.json'

    response = urlopen(url)

    schema = json.loads(response.read())

    return schema


def validate_metadata(metadata: dict) -> Tuple[bool, str]:
  """validate a model metadata dict using Audacity's metadata schema

  Args:
      metadata (dict): the metadata dictionary to validate

  Returns:
      boolean-str tuple, where the  bool indicates success, and 
      the string contains an error/success message
  """
  import jsonschema
  from jsonschema import validate
  schema = load_schema()

  try:
    validate(instance=metadata, schema=schema)
  except jsonschema.exceptions.ValidationError as err:
    print(err)
    return False, err

  message = "success! :)"
  return True, message