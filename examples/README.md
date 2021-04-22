# Bio-feedback examples

In this sub-directory of the `bio-feedback` project we collect example usage of the code.

- In the [`notebooks` folder](notebooks), you find 'jupyter-notebooks' which can be used for device-data **visualization** and for **data-analysis**
- In the [`controller` folder](controller), some simple **Agent**s are implemented which allow (i)  playing sound **using the keyboard** or (ii) playing recordings located in the `<PROJECT_ROOT>/data` folder (check the `Data` section in the [project's README](../README.md)).
- In the [`pipeline` folder](pipeline), `Receiver` and `Transmitter` examples are implemented to demonstrate life-data acquisition via the *Lab Streaming Layer*, using the `pylsl` and the `biofb` framework.
- In the [`session` folder](session), a *bio-feedback* session acquisition examples is implemented to demonstrate life-data acquisition from different devices (*g.tech Unicorn* and *OpenSignals (r)evolution*) via the *Lab Streaming Layer*.