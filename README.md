# EEG + ECG Multichannel [Plot](https://multi-channel-plot-visualizer.netlify.app/) Visualizer

An interactive visualization tool for exploring multichannel **EEG (µV)** and **ECG (mV)** data from CSV files.
Built for the QUASAR coding screener assignment, this script makes it easy to scroll, zoom, and inspect neurophysiological signals with a modern, user-friendly UI.

The hosted HTML can be found at this link: 

https://multi-channel-plot-visualizer.netlify.app/

---

## Features

* **Multichannel plotting** of EEG (µV), ECG (mV), and CM reference signals.
* **Interactive zoom & pan** with range slider and modebar tools.
* **Unit handling**: automatic conversion of ECG/CM signals from µV → mV.
* **Channel selection**: plot all channels or only a subset.
* **Downsampling**: keep every Nth sample to handle large datasets efficiently.
* **Export options**:

  * Interactive HTML (`.html`)
  * Static image (`.png`)
  * Vector format (`.pdf`)

---



## Demo

### Interactive Plot (HTML)


https://github.com/user-attachments/assets/4fe42941-f975-4a17-9c1c-81f885b687a8



---

## Command Line Options

| Argument          | Description                                          | Default                          |
| ----------------- | ---------------------------------------------------- | -------------------------------- |
| `--data`, `-d`    | Path to CSV data file                                | `EEG and ECG data_02_raw.csv`    |
| `--title`, `-t`   | Plot title                                           | `EEG and ECG Data Visualization` |
| `--output`, `-o`  | Output directory for saved plots                     | `output`                         |
| `--show`, `-s`    | Open plot in browser interactively                   | Off                              |
| `--channels`      | List of channels to plot                             | All available                    |
| `--ecg-units`     | `uv` or `mv`                                         | `mv`                             |
| `--step`          | Downsample factor (e.g., `5` keeps every 5th sample) | `1`                              |
| `--initial-range` | Initial time window to display (`START END`)         | Full range                       |

Example with downsampling & limited channels:

```bash
python plot_signals.py -d "EEG and ECG data_02_raw.csv" --channels Fz Cz P3 C3 F3 --step 10 --show
```

---

## Design Choices

1. **Scaling**

   * EEG plotted in **µV**.
   * ECG & CM converted to **mV** for readability.
   * Dual y-axis used for ECG/CM subplot to preserve scale integrity.

2. **Performance**

   * `Scattergl` is used for large datasets (>10,000 points) for smoother rendering.
   * Downsampling via `--step` to reduce memory load when needed.

3. **Usability Enhancements**

   * Unified hovermode (`x unified`) to align tooltips across channels.
   * Range slider included on bottom subplot for intuitive navigation.
   * Custom zoom controls added to modebar.




---

## Future Work

If given more time, I would extend the project with:

* [ ] **GUI-based channel selection** (checkbox toggles instead of CLI args).
* [ ] **Normalization toggle** (scale signals per channel for comparison).
* [ ] **Real-time streaming support** for live EEG/ECG monitoring.
* [ ] **Improved test coverage** and automated validation with sample datasets.

---

## Output Files

After running, check the `output/` directory for:

* `multichannel_plot.html` → interactive visualization
* `multichannel_plot.png` → static image
* `multichannel_plot.pdf` → vector export (requires `kaleido`)

---

## License

This project was created as part of the **QUASAR Coding Screener**.

