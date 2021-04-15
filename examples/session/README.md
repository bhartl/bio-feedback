# Bio-feedback Recorder

The `recorder.py` program allows to perform a `biofb.controller.session`.
Such sessions might be 
- basic therapist session, capturing the bio-data from a participant
- or a key-stroke controlled feedback session (allowing a controller to replay recorded therapist phrases) while monitoring the bio-data

Either way, both the participants bio-data and the controller interactions (if specified) are tracked.

## Installation
For installation instructions see the [project's README file](../README.md). 

## Recorder Usage
Open a **terminal** and navigate to the `bio-feedback` root directory (I prefer the git-bash):
```bash
cd <PROJECT ROOT DIRECTORY>
```

If not done already, activate the *Python* environment with the *bio-feedback* installation (here assumed to be named `bio-feedback`):
```bash
conda activate bio-feedback
```

Start the `bio-feedback` recorder with
```bash
python examples/session/record.py
```

and follow the instructions (type `python examples/session/record.py -h` for help).

You can always **stop** the measurement by pressing `Ctrl-C` or `ESC` (please press `ESC` before closing the monitor).

The session recorder allows **choosing** from pre-set (or generating new) 
- *Settings* (a setting describes the environmental setup of a session. It specifies the *Controller*, the *Location* and potentially more important details)
- *Subjects* (the experiment participant whose bio-data are captured)
- *Streams* (the Lab Streaming Layer stream names, usually `Bioplux`)

The paths (filesystem locations) where to look for pre-set configurations can be specified when calling the recorder.

After the measurement a compressed **hdf5 output-file** (per default in the [`data/session/biofb` folder](../../data/session/biofb)) is generated, which comprises the entire measurement (measurement setting, subject, hardware setup, bio-data, controller actions).

## Experiment Protocol

### Third-Party Data Acquisition
1) Start *OpenSignals (r)evolution*
   - connect (and configure) the *biosignalsplux* hardware.
   - The routing of our first biosignalsplux measurements was as follows:
     ![Sketch of bio-sensory hardware devices](../../doc/biofb/fig/biopux_routing.png "Used bio-sensory devices")

     
2) Start the *g.tech* Unicorn Suit
   - connect the electrodes of the *Unicorn* EEG device to the *Unicorn* cap
     ![Sketch of bio-sensory hardware devices](../../doc/biofb/fig/unicorn_EEG_routing.svg "Used bio-sensory devices")
   - connect the *Unicorn* hardware
   - start the recorder (License required)
   - setup the EEG-cap (all signals must be green)
3) Start *OpenSignals (r)evolution* and *g.tech* Suit data acquisition by clicking on the **Record Button** in each application window.

Each software will produce its own **output** file which can be loaded into our Framework.
(This step needs to be done by hand at the moment, but can easily be implemented in the recorder.py application.)

To **synchronize** the signals from both devices, some events need to be present in both data files.
A simple way to this is to ask the participant to **perform several teeth-clenchings** at the beginning of the measurement.
(This protocol is not fully professional, better use the [full integrated measurement](#full-integrated-biofb-session-biofb-all-through) below.)

### Lab Streaming Layer Joined Measurement

#### OpenSignals (r)evolution
1) Start *OpenSignals (r)evolution*, connect (and configure) the *biosignalsplux* hardware.
2) Make sure, to enable the *Lab Streaming Layer* access of *OpenSignals (r)evolution*: 
   - Click on the *OpenSignals (r)evolution* **Settings** button.
   - Click on the **INTEGRATION tab**.
   - **Check** the **Lab Streaming Layer** option. 
   - Start *OpenSignals (r)evolution* data acquisition by clicking on the **Record Button**.

#### g.tech Unicorn
To stream the *g.tec Unicorn* data to the [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer),
the **UnicornLSL client** needs to be installed.
A pre-built of the **UnicornLSL client** can be found in the [`biofb/pipeline/LSL-Unicorn` folder](../../biofb/pipeline/LSL-Unicorn); it is supported under Windows 10 ([Win64/UnicornLSL.exe](../../biofb/pipeline/LSL-Unicorn/Win64/UnicornLSL.exe)), a Linux version is not (yet?) available.

The **UnicornLSL client** is a GUI-application which can be connected to the *g.tec Unicorn Black Suit* 
(by selecting the corresponding device an clicking on `Open`) and which can `Start`/`Stop` a stream
to the LSL. 
Once a connection to the *Unicorn* is open, a corresponding stream should then be visible in the LSL.

If something does not work, the **UnicornLSL client** can be **manually installed**.
To manually install the **UnicornLSL client** closely follow the setup-instructions for the 
[Unicorn .NET API](https://github.com/unicorn-bi/Unicorn-Suite-Hybrid-Black/tree/master/Unicorn%20.NET%20API).
Also see the [youtube-tutorial](https://www.youtube.com/watch?v=l18lJ7MGU38) on how to stream data from the 
*g.tec Unicorn* device to the [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer). 

See also the **How To: Lab Streaming Layer** Section in the [project's README file](../README.md).

#### Third Party Recording

The bio-signals of both devices should be streamed to the LSL and can, for instance, be acquired with the Lab Recorder or via the pylsl library directly in Python.

Via the [LSL LAB Recorder](https://github.com/labstreaminglayer/App-LabRecorder) -- a stand-alone Application -- data from different devices (which are streaming to the LSL) can be acquired synchronously (see the [release List](https://github.com/labstreaminglayer/App-LabRecorder/releases) for downloading and installation; a Windows10 preinstalled [Lab_Recorder.exe](../../biofb/pipeline/LSL-Lab_Recorder/LabRecorder.exe) is located in [`biofb/pipeline/LSL-Lab_Recorder`](../../biofb/pipeline/LSL-Lab_Recorder)).

#### Full Integrated `biofb`-Session (`biofb` all through)

The `biofb` recorder should also be capable of receiving the data from the Lab Streaming Layer (see [above](#recorder-usage)!

## Footswitch protocol

- start of the measurement: Two successive foot-switch signals (after the recording started)
- deepening states of relaxation:  One foot-switch during the measurement
- end of the measurement: Two or several foot-switch signals (before the recording stops)
