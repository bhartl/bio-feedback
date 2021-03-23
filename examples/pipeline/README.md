# bio-feedback pipeline-examples

Here we demonstrate life-data acquisition in Python via the [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer) (LSL), using the `pylsl` and the `biofb` framework. 

## Prerequisites
To receive data from the LSL, **devices must stream to the LSL**.

- The *[biosignalsplux](https://biosignalsplux.com/)* *[hub](https://plux.info/components/263-8-channel-hub-820201701.html)* can stream to the LSL using the *[OpenSignals (r)evolution](https://biosignalsplux.com/products/software/opensignals.html)* software: check *Lab Streaming Layer* in the settings menu of *OpenSignals (r)evolution* software (also see the documentation).
- The *[g.tec Unicorn](https://www.unicorn-bi.com/?gclid=Cj0KCQiAyoeCBhCTARIsAOfpKxjuuKF57_Ng2IqhxVD_UgluFzqpDAXGvv8eJGDZtPF1wmyVdLI_YLgaAmf8EALw_wcB)* EEG-cap can also stream to the LSL using the [Unicorn .NET API](https://github.com/unicorn-bi/Unicorn-Suite-Hybrid-Black/tree/master/Unicorn%20.NET%20API).
  A precompiled (and modified) version is available in `biofb/pipeline/LSL-Unicorn/Win64/UnicornLSL.exe` for 64-bit Windows.
- *[Melomind website](https://www.melomind.com/en/operation/)*: WIP, the Melomind [demo-app](https://github.com/mbt-administrator/DemoSDK.Android) could be used to stream the data to the LSL (using the [LSL Java binding](https://github.com/labstreaminglayer/liblsl-Java)) instead of writing the data to a file. 

## Test LSL Streams

The [Lab Recorder](https://github.com/labstreaminglayer/App-LabRecorder) can be installed and used to query the network for LSL streams and to record data from different devices simultaneously.

A precompiled *Lab Recorder* installation for64-bit Windows can be found in `biofb/pipeline/LSL-Lab_Recorder/LabRecorder.exe`. 

Checkout 
```bash
python show_LSL_Lab_Recorder_output --xdf-path <PATH_TO_YOUR_LAB_RECORDING>
``` 
to plot the data from a *Lab Recorder* Session.

## Streaming/sending `biofb`-data to the LSL
With the `biofb_lsl_send` module, already captured data can be streamed to the LSL.

This can either be device-specific data or data from an entire `Sample`.

Try executing 
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_send.py send-bioplux
``` 
to stream the data of a *biosignalsplux* *OpenSignals (r)evolution* measurement, or 
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_send.py send-sample
``` 
to stream an entire sample, comprising *Bioplux* and *Unicorn* data to the LSL.

**Note**: The relative-path definitions of the demo-files are always with respect to the `<PROJECT_ROOT>` directory.

Use `-h` for a doc-string of the different applications.

## Receiving data from the LSL

The examples in [lsl_acquisition.py](lsl_acquisition.py) demonstrate data-acquisition using `pylsl` directly (also see the official [pylsl git tutorials](https://github.com/chkothe/pylsl/blob/master/examples)).
Try executing
```bash
cd <PROJECT_ROOT>
python examples/pipeline/lsl_acquisition.py -h
``` 
for possible applications.

The examples in [biofb_lsl_acquisition.py](biofb_lsl_acquisition.py) demonstrates data-acquisition using the `biofb` framework.
Try executing
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_acquisition.py -h
``` 
for possible applications.

### Send/Receive Bioplux 

To see the interplay between data-streaming/receiving
1) start for instance a stream in one shell via
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_send.py send-bioplux
``` 
2) and receiving the data in another shell via
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_acquisition.py device-acquisition --stream VirtualPlux
``` 
which show the transmitted/received data from a predefined demo-file `biofb_lsl_send.TEST_FILE_BIOPLUX` on a matplotlib data-monitor (also checkout the different configuration options using `-h`).

**Note**: The data transmission (intentionally) breaks up before the receiver is done.

### Send/Receive Multi-Device 

For multi-device streaming/receiving try
1) starting a stream in one shell via
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_send.py send-sample
``` 
2) and receiving the data in another shell via
```bash
cd <PROJECT_ROOT>
python examples/pipeline/biofb_lsl_acquisition.py multiple-device-acquisition
``` 
which show the received data on a matplotlib data-monitor.
