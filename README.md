# voice-stack

Whisper's little brother: **whistle** STT (16.9 MB, CPU only) plus local TTS
and a hermes voice loop, as three CLIs and an installer.

| script | what it does |
|---|---|
| `voice` | STT → TTS loop: `say`, `transcribe`, `record`, `hermes`, `loop` |
| `voice-lesson` | transcribe audio lessons into `.txt` / `.srt` / `.vtt` |
| `voice-hermes-stt` | bridge so hermes' `local_command` STT provider uses whistle |
| `voice-install` | idempotent installer: venv, weights, CLIs, hermes hooks |

## Why whistle

| | whistle | whisper base |
|---|---|---|
| size | **16.9 MB** | 139 MB |
| runtime | CPU, no deps | CPU, needs torch |
| languages | en/de/fr/es/it/nl/pl | 99+ |
| accuracy | lower | higher |

16.9 MB and no torch is the whole point on a CPU-only node. If you need
whisper-level accuracy, raise it with `VOICE_WHISPER_MODEL` in a faster-whisper
setup — the CLI surface is the same.

## Install

```bash
git clone https://github.com/ilPez00/voice-stack.git
voice-stack/bin/voice-install          # idempotent
voice-stack/bin/voice-install --check  # report gaps, change nothing
```

It owns:

```
~/.local/share/voice-venv    python venv (cactus-needle)
~/.local/share/voice/        whistle.cact weights
~/.local/state/voice/        transcripts, sidecar, audio
~/.local/bin/voice*          the CLIs
```

No root. Nothing is ever deleted.

## Use

```bash
export PATH="$HOME/.local/bin:$PATH"

voice say "hello"                 # speak (espeak-ng)
voice record 5                    # mic -> whistle -> speak back
voice transcribe lesson.mp3       # file -> text
voice loop                        # continuous, Ctrl-C to stop
voice hermes "what is 2 plus 2"  # ask the hermes gateway, print the reply
```

`voice record` prints what it heard, then speaks the answer. The answer comes
from the hermes gateway by default; override with `VOICE_LLM_CMD`:

```bash
VOICE_LLM_CMD="ollama run gemma3 -" voice loop
```

Every transcript also lands in `~/.local/state/voice/last-transcript.txt`, so a
HUD or hook can pick it up without re-running STT.

### Lessons

```bash
voice-lesson lecture.wav --srt --words --lang en
voice-lesson --dir ~/recordings --srt
```

Writes `YYYYMMDD-HHMMSS-<slug>.txt` (and `.srt`/`.vtt` with `--srt --words`)
into `~/.local/share/voice/lessons/`. Any format ffmpeg reads works; it is
normalised to 16 kHz mono because that is what whistle is trained on.

## Hermes integration

`voice-install` points hermes' own voice mode at whistle:

```
HERMES_LOCAL_STT_COMMAND=<venv>/bin/python <bin>/voice-hermes-stt {input_path} {output_dir}
```

hermes runs that command and reads `<output_dir>/*.txt` — the contract
`voice-hermes-stt` implements. It also registers a local TTS command provider
so hermes speaks through espeak-ng instead of a paid API:

```yaml
tts:
  providers:
    espeak:
      type: command
      command: /usr/bin/espeak-ng -w {output_path} -s {speed} < {input_path}
```

## Environment

| var | default |
|---|---|
| `VOICE_VENV_PY` | `~/.local/share/voice-venv/bin/python` |
| `VOICE_WHISTLE_WEIGHTS` | `~/.local/share/voice/whistle.cact` |
| `VOICE_ALSA_DEV` | `default` |
| `VOICE_SAMPLE_RATE` | `16000` |
| `VOICE_WORK_DIR` | `~/.local/state/voice` |
| `VOICE_LESSONS_DIR` | `~/.local/share/voice/lessons` |
| `VOICE_HERMES_URL` | `http://127.0.0.1:8642/v1/chat/completions` |
| `VOICE_HERMES_ENV` | `~/.hermes/.env` |
| `VOICE_LLM_CMD` | unset — hermes is used instead |
| `VOICE_ESPEAK_VOICE` | unset (default voice) |
| `VOICE_ESPEAK_SPEED` | `150` |

## Requirements

`ffmpeg`, `espeak-ng`, `arecord`/`aplay` (ALSA), python3. `cactus-needle`
pulled into the venv by the installer.
