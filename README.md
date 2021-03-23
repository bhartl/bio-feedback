# bio-feedback

The **bio-feedback** framework is the (first) core software framework for our shared **Brain Project** (*better names are welcome*).

It allows 

- capturing data with bio-sensory hardware (mostly 
  via the *[Melomind heaset](https://www.melomind.com/en/operation/)*,
  via the *[biosignalsplux hub](https://plux.info/components/263-8-channel-hub-820201701.html)* and *[related sensors](https://biosignalsplux.com/products/sensors.html)* 
or via the *[g.tec Unicorn EEG Device](https://www.unicorn-bi.com/?gclid=Cj0KCQiAyoeCBhCTARIsAOfpKxjuuKF57_Ng2IqhxVD_UgluFzqpDAXGvv8eJGDZtPF1wmyVdLI_YLgaAmf8EALw_wcB)*)
- opening and handling data from data-acquisition sessions of above devices,
- preprocessing, postprocessing and analysing the data, and
- providing/generating feedback signals via agent instances
  
with the goal of guiding/controlling the bio-sensory data of a subject during a session towards a characteristic state with well-defined features.

[*Note: maybe we even need an ethical agreement for our project*].

## Project Structure

### Experiment Design (in Linz: RB, DMo)

*	Select Sensors
*	Define Procedures
*	Definition of App functionalities

### Measurement of experiments (in Linz: RB, BH, TT, DMo)

*	Protocol on the session including questionnaire
*	Data acquisition and synchronisation using Python framework
*	Build up database

### Data analysis (BH, GC, DMi, DMo, TT)

*	Build Python Framework (BH, TBD)
*	Research state of the art EEG/Bio Signals analysis = preprocessing of raw data (DMi, GC)
*	Find correlations between subjective states and objective sensor values (DMo, GC, TT, BH)

 

### Controller Design (DMo, GC, BH)


### App Design (MP, DA)

*	Implement functionalities to conduct experiments (MP, DA)
*	Generation of sounds (music, sound, voice)
*	Implementation of the feedforward loop (MP, DA)
*	Implementation of the feedback loop (MP, DA)

## Framework Structure 

### The `biofb` package

The base datatype of the `biofb` package is the `biofb.session.sample` class.

It brings together
- data acquisition of a `biofb.hardware.setup` (which comprises a list of `biofb.hardware.device` instances, each containing again a list of `biofb.hardware.channel` objects for each bio-signal)
- for a `biofb.session.subject` (the participant whose bio-data are captured)
- in a well-defined `biofb.session.setting` (the overall scope of the experiment, e.g. a test-session, an in-person session or a feedback-session)
- and controlled by a `biofb.session.controller` (a human person or a machine).


### The `biofb.io` sub-package

File-handling- and database access operations are collected in the `biofb.io` sub-package.
Each class in the `bio-feedback` inherits from `biofb.io.loadable.Loadable`, which allows instances of the different classes to be loaded from `dict`-like objects (such as Python dictionaries, different representations of such dictionaries, `yaml`-files, `json`-files, etc.).

In `version 0.1`, the bio-data for captured session-samples is managed by a `yml`-based 'database' class, i.e., by `biofb.io.session_database`.

[*Note: this is a simple way to provide data access quickly in an early stage of the project. However, we should make a transition to a rigorous database soon. 
I hope, that this approach can easily be transformed to a database approach.*]

File-format transformations of *wave-audio-files* are collected in the `biofb.io.wave_file` module.

### The `biofb.session` sub-package

In the `biofb.session` sub-package, the basic data-structure of a `biofb.session.sample` is defined in a modular way which should (hopefully) be easily mappable to a database.

A `biofb.session.sample` contains information about the `participant` whose `data` are/were acquired using a specific `hardware`-`setup` during a session with a specific `controller`.
Other meta-data such as `location` or `date-time` of a session can/should also be added.
Further, we will also need feedback information about the quality of the session by the participants and their personal experiences.

The handling of these different aspects of a bio-feedback sample is realized/united in the `biofb.session.sample` class.

### The `biofb.hardware` sub-package

The general datastructures to handle a hardware setup is given by the `biofb.hardware.Setup` class.
It primarily contains a list of devices.

The general datastructures to handle a specific device is given by the `biofb.hardware.Device` class.
Each device captures data from several channels which is usually stored/provided in a `numpy` array.
For a more convenient data-handling of the different channels, each device contains a list of channel objects.
Each device also is able to perform data-acquisition using `biofb.pipeline.Receiver` configurations, which is synchronized in hardware `Setup`, or in a `Sample` session.

The general datastructures to handle a specific channel from a specific device is given by the `biofb.hardware.Channel` class.
This class has a link to its associated `Device` and can in that way access the channel-specific device data (which is one numpy array).

In the sub-package `biofb.hardware.devices`, more specific `Device`-classes are implemented that are related to more specific devices (e.g., Melomind, Bioplux and Unicorn).
These different device-specific classes allow capturing and handling the device-specific data.

In the sub-package `biofb.hardware.channels`, more specific `Channel`-classes are implemented that are related to more specific bio-sensory channels (e.g., EEG, ECG, EOG, EDA, ...).
These different channel-specific classes allow task-specific and targeted preprocessing (filtering, stabilizing, etc.) and postprocessing operations (transformations, analysis, feature extraction, quality predictions, etc.).

*[Note: channel handling works, i.e. each channel of a device can be related to a specific channel class in `biofb.hardware.channels` via labels and class names.]*

*[Note: channel specific data-handling using filters, etc., is work in progress, documentations and literature can be found on the device-specific websites and also in the related `biofb.signal.channel` sub-package, which contains(will contain) implementations of channel specific functionalities.]*

### The `biofb.pipeline` sub-package

Here, data `Reiceiver` and `Transmitter` classes are implemented that can be used to receive and send data from different bio-sensory devices (data-acquisition that can be used in Python).

We mainly rely on the open-source [*Lab Streaming Layer*](https://github.com/sccn/labstreaminglayer) and the [pylsl](https://pypi.org/project/pylsl/) package to directly access the data form third party bio-sensory hardware in the `biofb` framework.

### The `biofb.visialize` sub-package
Here, data visualization tools are implemented.

- The `biofb.visialize.DataMonitor` allows to plot (in a non-blocking way) time-series data. 

### The `biofb.signal` sub-package

The `biofb.signal` sub-package contains pure procedural (function-) collections of signal specific data operations:

- pre-/ postprocessing of various spatio-temporal bio signals
- pre-/ postprocessing of channel-specific data (ECG, EEG, ...) in the `biofb.signal.channels` sub-package (which are related to the corresponding high-level `biofb.hardware.channels` classes).

### The `biofb.controller` sub-package

The `biofb.controller` sub-package provides the main feedback loop of the `bio-feedback` software framework:

- The `biofb.controller.Session` comprises a pro-active `biofb.controller.Agent` and a participant, interacting via measured `biofb.session.Sample` bio-sensory data.
- The `Agent` proposes `actions` to be performed on a participant (e.g., it selects audio signals to be replayed).
- This will change the `state` of the participant (i.e., the captured `state` of the bio-signals in a `biofb.session.Sample`).

Once again:

- The actions are proposed by a `biofb.controller.Agent`.
- Data acquisition is performed by the used `biofb.hardware.Setup` *[Note: work in progress]*.
- The feedback of `action(state)` -> `state update` -> `action(updated state)` -> ... is controlled by the `biofb.controller.Session`. The proposed actions and the acquired bio-data (ì.e., `action` and `state`) are recorded by the `biofb.controller.Session` *[Note: work in progress]*.

The model of how to control the `state` of a participant is `Agent`-specific, and we propose three sub-categories of agents at the moment via the sub-packages *[Note: this might change in the future]*

- `biofb.controller.audio`
- `biofb.controller.generative`
- `biofb.controller.verbal`.

Each realisation of an `Agent` has an internal model (or a policy) based on which the agent decides what action to propose given a particular sample-state (or a sample-state history) *[Note: future work]*.

*[Note: this might be updated in the future]*

## Data: `/data`

The project data (which comprises *session samples*, *audio recordings*, *preprocessed data*, ...) is stored separately to the git-repository via our shared [Dropbox, `hex`](https://www.dropbox.com/sh/sppl4auj650zy4q/AACIACSEJroiu1rLcaBQDJy8a?dl=0).

The [Dropbox data-folder `hex/data`](https://www.dropbox.com/sh/kjbf0912f8dwxkf/AABJebYYiqZFMw3BuI4QFd_ka?dl=0) with all sub-folders should -- as is -- be copy-pasted into the `bio-feedback` git-project's root directory, `/`, i.e. `hex/data/*` -> `/data/*`.

The reason to store the data separately is due to data-security and privacy issues.
The `/data` folder is explicitly excluded from the git-repository via `.gitignore`.

Alternatively, the `data` folder can be shared via a peer-to-peer [Syncthing](https://syncthing.net/) client.

*[Note: Surely, there is room for improvement how to share our data. I'm happy for suggestions (e.g. an automized way how to download the data from the Dropbox or a separate git-repository).]*

## Documentation `/doc`

Documentation about third-party hardware and software-packages (user-manuals and data-sheets) can be found in the `/doc` folder. 


## Installation and Setup

### Create virtual environment (venv)
First, make sure Anaconda is installed. Then create a new virtual environment (venv):
```bash
conda create --name bio-feedback python=3.7
```
(the *OpenSignals (r)evolution* Python package (`plux`) requires Python 3.7.).

and activate it
```bash
conda activate bio-feedback
```

Also, make sure that the `bio-feedback` venv is added to the `jupyter` kernels:
```bash
python -m ipykernel install --user --name="bio-feedback"
```
(`jupyter` should be installed either in the Anaconda `base` venv or in the `bio-feedback` venv to allow usage of the jupyter demo-notebooks.)


You can leave the venv via 
```bash
conda deactivate
```

### Install `biofb` package in venv

Use `pip` to install the `biofb` package to your Python environment
```bash
python setup.py install
```

*[Note: this has been tested in Ubuntu 18.04 and in Windows 10 using the Git-Bash.]*

### Use `biofb` package as `PYTHONPATH` library

Navigate to the project root directory `<PROJECT_ROOT>`

```bash
cd <PROJECT_ROOT>
```

For *Linux* install the following dependencies:
```bash
sudo apt-get install -y python3-dev libasound2-dev
```

Use `pip` to install all requirements
```bash
python -m pip install -r requirements.txt
```

Add the `<PROJECT_ROOT>` directory to the `PYTHONPATH` environment variable 

#### Linux

```bash
export PYTHONPATH=$PYTHONPATH:<PROJECT_ROOT>
cd test
python -m unittest discover -s .
```

#### Windows (not tested)
```bash
set PYTHONPATH=%PYTHONPATH%;<GLOBAL_PROJECT_ROOT>
cd test
python -m unittest discover -s .
```

### Test Installation

Run unittests from `<PROJECT_ROOT>/test` directory:
```bash
cd <PROJECT_ROOT>/test
python -m unittest discover -s .
```

## Demos and Examples

Demos, tutorials and examples how to use the code framework should be provided in the `test/biofb_unittest/` and `examples` packages.

### Examples in `examples`

Several simple examples are implemented here, see the respective [README](examples/REAMDE.md) for details.

### Jupyter-Demo Notebooks in `/examples/notebooks`
There is some demo-notebooks used to demonstrate data-handling/analysis/visualization in `/examples/notebooks` for the *Melomind*, *g.tec Unicorn* and the *Bioplux* bio-sensory hardware.

Please do not commit changes made simple due to execution of the notebooks.
You can copy (duplicate) a notebook to `<nb-name>.local.ipynb`, the duplicated notebook with `.local` is excluded from git via `/.gitignore`. In that way you can quickly experiment around. 

### Unittests in `test/biofb_unittest/<same structure as biofb-packages>`
The module-structure of `biofb_unittest` is equivalent to the module structure of `biofb`.
Class/Task specific tests of the `biofb` module can thus be found in the `biofb_unittest` package.

The unittests **can** be run from within the `<PROJECT_ROOT>` folder via:
```bash
python -m unittest discover -s test
```

but **should** be run from within the `<PROJECT_ROOT>/test` folder.
This requires to either 
- add the `<PROJECT_ROOT>` to the `PYTHONPATH` environment variable (see **Setup** above)
- or to install the `biofb` Python package via the `setup.py` script (see **Setup** above). 

The reason for this is relative path-relations to the `test/data` folder.
(Some fallbacks to an execution directly from `<PROJECT_ROIOT>` are implemented.)

## Third-Party Bio-Sensory Data-Acquisition Systems

### Melomind

Here you can find the official *[Melomind website](https://www.melomind.com/en/operation/)*.

This is a very simple head-set device with 2 EEG sensores and 2 related quality signals.
Its goal is to guide participants towards deep relaxation via audio-feedback.
We (RB, BH, TH) have the impression, that this does not work properly: 
the software-feedback often displays states of relaxation when people are highly focused -- so the feedback loop of *Melomind* might be improvable. 

We modified the *Melomind* [Android demo-app](https://github.com/mbt-administrator/DemoSDK.Android) such that data are stored to a file on the Android device running the demo-app (not included in the bio-feedback package -- we are not sure if we will proceed with this hardware).

### biosignalsplux Bio-Sensor Acquisition
Here you can find the official *[biosignals plux homepage](https://biosignalsplux.com/)*.
We are currently using the *[biosignalsplux hub](https://plux.info/components/263-8-channel-hub-820201701.html)* and *[related sensors](https://biosignalsplux.com/products/sensors.html)* with whom we capture various bio-sensory data (EEG, ECG, EMG, EOG, EDA, ...).

Channel specific signal analysis should be implemented in the package [`biofb/signals/channels`](biofb/signals/channels) (procedural) and on a higher-level in [`biofb/hardware/channels`](biofb/hardware/channels). 

The *biosignalsplux* hardware is interfaces with the *[OpenSignals (r)evolution](https://biosignalsplux.com/products/software/opensignals.html)* software, a Python-powered web-based application.
The *OpenSignals (r)evolution* Documentation can be found [here](./doc/bioplux/OpenSignals_Manual.pdf).

#### Installation (for linux)
1) Download *OpenSignals (r)evolution* either from the [*biosignalsplux*](https://www.biosignalsplux.com/en/software/) or from the [*BiTalino*](https://bitalino.com/en/software) websites. 
2) Install open the *Terminal* and `cd` to the dictionary where the `OpenSignals_revolution_ubuntu_amd64.deb` file is located.
3) Install the software with the following command and follow the instructions:
```bash
sudo apt install ./OpenSignals_revolution_ubuntu_amd64.deb
```
4) The *OpenSignals (r)evolution* interface should be *available as application* (as `OpenSignals`) or through the *Terminal* (as `opensignals`).

### g.tec Unicorn EEG Device
We rely on the *[g.tec Unicorn](https://www.unicorn-bi.com/?gclid=Cj0KCQiAyoeCBhCTARIsAOfpKxjuuKF57_Ng2IqhxVD_UgluFzqpDAXGvv8eJGDZtPF1wmyVdLI_YLgaAmf8EALw_wcB)*
as 8-channel EEG-device.

## Third-Party Software

### Melomind *Demo App*

Ideally, we manage to stream the data from the Melomind *Demo App* to the 
[**Lab Streaming Layer**](https://github.com/sccn/labstreaminglayer) and 
capture the data in Python using the `pylsl` library (see below).

### *OpenSignals (r)evolution*

The *OpenSignals (r)evolution* allows to configure the hardware setup of a *biosingalsplux* device, i.e., the channel configuration.

*OpenSignals (r)evolution* is supported  
- on **Windows 10** and
- on **Android**
- (basically also on **Linux**, but here **bluetooth connection issues** permit data acquisition).

A short documentation how to get bio-signals from a *OpenSignals (r)evolution* 
data-acquisition session can be found [here](doc/bioplux/OpenSignals%20LSL%20Manual.pdf).

The *OpenSignals (r)evolution* studio allows to stream the data on the 
[**Lab Streaming Layer**](https://github.com/sccn/labstreaminglayer) such that data can synchrounously be acquired using 
the `pylsl` library (see below).

### *g.tec Unicorn Suit Recorder*

The *g.tec Unicorn Suit* comes with a **Recorder** Application. 
The *Unicorn Recorder* provides a **quality-assessment** of the EEG channels, which is **most likely** based on comparing the **variance of each channel over an extended time-period** (only high-end devices provide quality assessment via impedance values of each electrode).
Further, it allows to filter the EEG signals using a **notch** and a **bandpass** filter.

The *Unicorn Recorder* application requires a Software License (to be purchased).

The data from the *g.tec Unicorn Suit* can be acquired via the *g.tec* **Python API**, which also requires a Software Lience (to be purchased).

*[Note: We therefore should implement the basic filters (notch and bandpass) in the bio-feedback framework]*


Alternatively, 
- a **c-API exists**, which can be used to generate a custom data-acquisition python module (e.g. via boost-python)
- or the data from the unicorn are acquired via the [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer) 
  (see below).

## Putting All Together: *Lab Streaming Layer* (LSL)

LSL is an overlay network for real-time exchange of time series between applications, 
most often used in research environments. LSL has clients for many languages (such as Python) 
and platforms (such as Max, Windows or Linux) that are compatible with each other 
*[from the official LSL git repository]*.

**ATTENTION: Privacy and Security issues might be a problem for the production state. 
LSL streams without encryption on serveral ports without authentication necessities.**

### LSL Recorder

Via the [LSL Recorder](https://github.com/labstreaminglayer/App-LabRecorder) -- a stand-alone Application -- 
data from different devices (which are streaming to the LSL) can be acquired synchronously.
Here the [Release List](https://github.com/labstreaminglayer/App-LabRecorder/releases) for downloading and installation.

The LSL Recorder stores data in a binary *xdf* format, which can be accessed in Python via `pyxdf` 
(here the [official github repo](https://github.com/xdf-modules/pyxdf)).

### The `pylsl` Package

`pylsl` is a [Python interface](https://pypi.org/project/pylsl/) to the Lab Streaming Layer (LSL) 
which can be installed via 
```bash
pip install pylsl
``` 
*(supported for Python 3.7 or 3.8 and Wind32/64, Linux64 and macOS 10.6+ in `pylsl-1.14.0`)*.

The package can also be built manually following the [installation guide](https://github.com/labstreaminglayer/liblsl-Python/).

Examples of `pylsl` usage can be found on the official [github repo](https://github.com/labstreaminglayer) 
in the [`pylsl/examples` subfolder](https://github.com/labstreaminglayer/liblsl-Python/tree/master/pylsl/examples). 
Note that these can be run directly from the commandline with (e.g.) 
```bash
python -m pylsl.examples.SendStringMarkers
```

### *Melomind*
[**TODO**: Data-streaming from the modified Demo-App to the LSL.]

### *OpenSignals (r)evolution*
How to setup the *OpenSignals (r)evolution* data-streaming to the LSL can be 
found in the [manual](doc/bioplux/OpenSignals%20LSL%20Manual.pdf):
- Click on the *OpenSignals (r)evolution* **Settings** button.
- Click on the **INTEGRATION** tab.
- Check the **Lab Streaming Layer** option.
- Start *OpenSignals (r)evolution* data acquisition by clicking on the **Record Button**.
- The bio-signals are streamed to the LSL and can, for instance, be acquired with the 
  [Lab Recorder](https://github.com/labstreaminglayer/App-LabRecorder) 
  or via the `pylsl` library directly in Python.


### *g.tec Unicorn*

To stream the *g.tec Unicorn* data to the [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer),
the **UnicornLSL client**  needs to be installed.
A pre-built of the **UnicornLSL client** can be found in `biofb/hardware/pipeline/LSL-Unicorn`
- Windows 10: `Win64/UnicornLSL.exe`
- Linux: **Not available**

The **UnicornLSL client** is a GUI-application which can be connected to the *g.tec Unicorn Black Suit* 
(by selecting the corresponding device an clicking on `Open`) and which can `Start`/`Stop` a stream
to the LSL. 
Once a connection to the *Unicorn* is open, a corresponding stream should then be visible in the LSL.
This can be checked using the [Lab Recorder](https://github.com/labstreaminglayer/App-LabRecorder).

If something does not work, the **UnicornLSL client** can be **manually installed**.
To manually install the **UnicornLSL client** closely follow the setup-instructions for the 
[Unicorn .NET API](https://github.com/unicorn-bi/Unicorn-Suite-Hybrid-Black/tree/master/Unicorn%20.NET%20API).
Also see the [youtube-tutorial](https://www.youtube.com/watch?v=l18lJ7MGU38) on how to stream data from the 
*g.tec Unicorn* device to the [Lab Streaming Layer](https://github.com/sccn/labstreaminglayer). 

**Prerequisites**:

-    Microsoft Windows 10 Pro, 64-bit, English
-    Unicorn Suite Hybrid Black 1.18.00
-    Microsoft Visual Studio -- Microsoft .NET framework 4.7.1 
     (see the [.NET releases](https://dotnet.microsoft.com/download/visual-studio-sdks?utm_source=getdotnetsdk&utm_medium=referral) 
     site)

1. Ensure that the Unicorn Suite Hybrid Black is installed on your computer.
2. Unzip  `biofb/hardware/pipeline/LSL-Unicorn/UnicornLSL.zip`
3. *(Covered by step 2.:)* Go to the *g.tec Unicorn* [git-repo](https://github.com/unicorn-bi/Unicorn-Suite-Hybrid-Black).
4. *(Covered by step 2.:)* Download the entire git-repo as zip-file and extract it,
5. Copy the files in the `Unicorn .NET API/Unicorn LSL` folder 
   to `C:\Users\<USERNAME>\Documents\gtec\Unicorn Suite\Hybrid Black\Unicorn DotNet\Examples\UnicornLSL`
6. Open the solution `UnicornLSL.sln` in Visual Studio
7. Select the desired configuration (Release/Debug) and build the project

**ATTENTION**: If the build fails the prerequisites have not been installed properly, 
or the project has not been copied to the appropriate path (post build scripts will fail). 
Check the paths to the referenced Unicorn Suite libraries in the project file settings, 
as well as in the post build action.

## Additional Dependencies and Sources

### Audio Interactions (*Linux*)

Under *Linux* the Python-package `simpleaudio` requires the following library to be installed:

```sudo apt-get install libasound2-dev```

### Visualization and Data Analysis

- [MNE tools](https://mne.tools/stable/index.html) is an open-source Python package for exploring, visualizing, and analyzing human neurophysiological data: MEG, EEG, sEEG, ECoG, NIRS, and more.
- [MNE-Lab](https://github.com/cbrnr/mnelab) MNELAB is a graphical user interface (GUI) for MNE, a Python package for EEG/MEG analysis.
- [SigViewer](https://github.com/cbrnr/sigviewer)  is a viewing application for biosignals such as EEG or MEG time series. In addition to viewing raw data, SigViewer can also create, edit, and display event information (such as annotations or artifact selections).


