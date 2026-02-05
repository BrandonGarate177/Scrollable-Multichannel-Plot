# Scrollable Multichannel EEG/ECG Plotter

Interactive visualization of multichannel EEG (uV) and ECG (mV) signals from CSV files. The plot is scrollable, zoomable, and suitable for quick signal inspection or sharing as a static export.

Live demo: https://multi-channel-plot-visualizer.netlify.app/

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --show
```

## Usage

```bash
python main.py -d "EEG and ECG data_02_raw.csv" --channels Fz Cz P3 C3 F3 --step 10 --show
```

### Command line options

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

## Outputs

Generated files are written to `output/`:

- `multichannel_plot.html` (interactive)
- `multichannel_plot.png` (static)
- `multichannel_plot.pdf` (vector)

Static exports require `kaleido` (already in `requirements.txt`).

## Notes

- EEG channels are displayed in uV, ECG/CM in mV (or uV if `--ecg-units uv`).
- Large datasets render faster with `--step` downsampling.
- The sample CSV is included to make the repo runnable immediately.

## License

MIT
