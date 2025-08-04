import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pathlib import Path

# Build absolute path to the Vosk model directory
model_dir = Path(__file__).parent.parent / "models" / "vosk-model-small-fr-0.22"
if not model_dir.exists():
    raise FileNotFoundError(f"Vosk model directory not found: {model_dir}")
MODEL_PATH = str(model_dir)

# Attempt to load the Vosk model
try:
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, 16000)
except Exception as e:
    print(f"Warning: STT model load failed: {e}")
    model = None
    rec = None

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

# Function to recognize speech for a given duration (seconds)
def recognize_speech(duration=5):
    if rec is None:
        return "STT unavailable: model failed to load."

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
        print("Recording...")
        rec.AcceptWaveform(b"")
        for _ in range(int(16000 / 8000 * duration)):
            data = q.get()
            rec.AcceptWaveform(data)
    result = rec.FinalResult()
    result_json = json.loads(result)
    return result_json.get('text', '')