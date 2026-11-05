from dataclasses import dataclass, asdict
from music21 import *
from datetime import datetime

@dataclass(frozen=True, slots=True)
class Note:
    onset: float      # quarter notes from start of tune
    dur: float        # length in quarter notes
    midi: int         # 60 = middle C
    pitch: str        # e.g. "F#4"
    bar: int
    beat: float       # 1.0 = first beat of the bar

@dataclass
class Tune:
    tune_id: int
    stream: list[Note]
    name: str
    type: str
    meter: str
    mode: str
    composer: str



def getStream (
    id: int,
    ABC: str,
    meter:str,
    modeRaw:str,
    composer: str,
    name: str,
    type: str,
    date: str
    ) -> stream.Stream:
    stream = converter.parse(ABC, format="abc")

    #split key
    tonic = modeRaw[0]
    mode = modeRaw[1:]

    stream.append(meter.TimeSignature(meter))
    stream.append(key.Key(tonic, mode))

    stream.metadata = metadata.Metadata()
    stream.metadata.composer = composer
    stream.metadata.title = name
    stream.metadata.setCustom("type", type) #remember this is list! (tupple)
    stream.metadata.setCustom("tune_id", id)
    stream.metadata.dateCreated = datetime.fromisoformat(date).date() 
    
    return stream
