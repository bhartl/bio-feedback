# bio-feedback controller-examples

A simple, manually controlled keystroke agent for playing musical notes via a `biofb.controller.audio.KeyAgent` or via a `biofb.controller.audio.KeySession` can be found in `examples/controller/audio`. 
These should be run from within the `<PROJECT_ROOT>` directory (*use the `-h` for help*):

- a simple `KeyAgent` implementation:
```bash
python examples/controller/audio/key_agent.py
```

- a `KeySession` implementation replaying audio-arrays
```bash
python examples/controller/audio/key_session.py main-array
```

- a `KeySession` implementation replaying audio-recordings (wave-files)
```bash
python examples/controller/audio/key_session.py main-wav
```


Another example where verbal audio recordings can manually be replayed via a `biofb.controller.verbal.HillAgent` wrapped in a `biofb.controller.audio.KeySession` is located in `examples/controller/verbal`. 
The example program should be run from within the `<PROJECT_ROOT>` directory (*use the `-h` for help*).

```bash
python examples/controller/verbal/hill_session.py
```
