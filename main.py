import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import argparse
import os


# Load data from CSV file
def load_data(filepath, step=1):

    print(f"Loading data from: {filepath}")
    
    # Ignores comments
    df = pd.read_csv(filepath, comment='#')
    
    if 'Time' not in df.columns:
        raise ValueError("Expected a 'Time' column (seconds).")
    
    # Clean up data
    df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
    df = df.dropna(subset=['Time']).sort_values('Time')
    
    ignore_cols = {'X3:', 'Trigger', 'Time_Offset', 'ADC_Status', 'ADC_Sequence', 'Event', 'Comments'}
    df = df[[c for c in df.columns if c not in ignore_cols]]
    
    for c in df.columns:
        if c != 'Time':
            df[c] = pd.to_numeric(df[c], errors='coerce')
    
    if step > 1:
        df = df.iloc[::step].copy()
        print(f"Downsampled by factor {step}")
    
    print(f"Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Time range: {df['Time'].min():.3f}s to {df['Time'].max():.3f}s")
    
    return df.reset_index(drop=True)


def create_plot(df, title="EEG and ECG Data Visualization", ecg_units='mv', channels=None, initial_range=None):

    # Define EEG channels (µV scale) - 21 channels total
    eeg_channels = ['P3', 'C3', 'F3', 'Fz', 'F4', 'C4', 'P4', 'Cz', 'A1', 'Fp1', 'Fp2', 
                    'T3', 'T5', 'O1', 'O2', 'F7', 'F8', 'A2', 'T6', 'T4', 'Pz']
    
    # Define ECG and CM channels
    ecg_channels = ['X1:LEOG', 'X2:REOG']
    cm_channels = ['CM']
    
    # Filter available channels
    available_eeg = [ch for ch in eeg_channels if ch in df.columns]
    available_ecg = [ch for ch in ecg_channels if ch in df.columns]
    available_cm = [ch for ch in cm_channels if ch in df.columns]
    
    # Apply channel filtering if specified
    if channels:
        available_eeg = [ch for ch in available_eeg if ch in channels]
        available_ecg = [ch for ch in available_ecg if ch in channels]
        available_cm = [ch for ch in available_cm if ch in channels]
    
    print(f"Available EEG channels: {available_eeg}")
    print(f"Available ECG channels: {available_ecg}")
    print(f"Available CM channels: {available_cm}")
    
    # Convert ECG to mV if needed
    if ecg_units == 'mv':
        for ch in available_ecg:
            df[f'{ch}_mV'] = df[ch] / 1000.0
        ecg_data_cols = [f'{ch}_mV' for ch in available_ecg]
        ecg_unit_label = 'mV'
    else:
        ecg_data_cols = available_ecg
        ecg_unit_label = 'uV'
    
    # Convert CM to mV if needed (CM is typically much larger, so scale appropriately)
    if ecg_units == 'mv' and available_cm:
        df[f'CM_mV'] = df['CM'] / 1000.0
        cm_data_cols = [f'CM_mV']
        cm_unit_label = 'mV'
    else:
        cm_data_cols = available_cm
        cm_unit_label = 'uV'
    
    # Create subplots with shared X-axis
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'EEG Channels (uV)', f'ECG and CM ({ecg_unit_label})'),
        vertical_spacing=0.06,
        shared_xaxes=True,  # Link X-axes
        specs=[[{"secondary_y": False}], [{"secondary_y": True}]]  # Allow secondary Y for CM
    )
    
    # Choose scatter class based on data size for performance
    def _scatter_cls(n):
        return go.Scattergl if n > 10000 else go.Scatter
    
    scatter_cls = _scatter_cls(len(df))
    
    # Colors for different channels
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', 
              '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8', '#ffbb78',
              '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d3', '#c7c7c7',
              '#dbdb8d', '#9edae5', '#ad494a']
    
    # Plot EEG channels (µV scale)
    for i, channel in enumerate(available_eeg):
        color = colors[i % len(colors)]
        fig.add_trace(
            scatter_cls(
                x=df['Time'],
                y=df[channel],
                mode='lines',
                name=channel,
                line=dict(color=color, width=0.8),
                hovertemplate=f'<b>{channel}</b><br>' +
                             'Time: %{x:.3f}s<br>' +
                             'Value: %{y:.1f}uV<br>' +
                             '<extra></extra>',
                legendgroup='eeg'
            ),
            row=1, col=1
        )
    
    # Plot ECG channels (make them more prominent)
    for i, (channel, data_col) in enumerate(zip(available_ecg, ecg_data_cols)):
        color = colors[i % len(colors)]
        fig.add_trace(
            scatter_cls(
                x=df['Time'],
                y=df[data_col],
                mode='lines',
                name=channel,
                line=dict(color=color, width=1.5),
                opacity=0.9,
                hovertemplate=f'<b>{channel}</b><br>' +
                             'Time: %{x:.3f}s<br>' +
                             f'Value: %{{y:.1f}}{ecg_unit_label}<br>' +
                             '<extra></extra>',
                legendgroup='ecg',
                showlegend=True
            ),
            row=2, col=1
        )
    
    # Plot CM reference channel on secondary Y-axis (muted appearance)
    for i, (channel, data_col) in enumerate(zip(available_cm, cm_data_cols)):
        fig.add_trace(
            scatter_cls(
                x=df['Time'],
                y=df[data_col],
                mode='lines',
                name=channel,
                line=dict(color='lightgray', width=0.8, dash='dot'),
                opacity=0.6,
                hovertemplate=f'<b>{channel}</b><br>' +
                             'Time: %{x:.3f}s<br>' +
                             f'Value: %{{y:.1f}}{cm_unit_label}<br>' +
                             '<extra></extra>',
                legendgroup='cm',
                showlegend=True
            ),
            row=2, col=1, secondary_y=True
        )
    
    # Update layout with improved UX
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20)
        ),
        height=820,
        margin=dict(t=80, r=220, b=120, l=70),  # Give titles/rangeslider room
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,            # Keep it high but inside the figure
            xanchor="left",
            x=1.02,            # Outside the plotting area
            itemsizing='trace',
            bgcolor='rgba(255,255,255,0.8)'
        ),
        hovermode='x unified',
        template='plotly_white',
        uirevision="EEGECG_v1",  # Keep view stable with consistent string
        xaxis=dict(  # top subplot axis
            rangeslider=dict(visible=False),
            rangeselector=None,
            type="linear",
        ),
        xaxis2=dict(  # bottom subplot axis
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(step='second', stepmode='backward', count=5, label='5s'),
                    dict(step='second', stepmode='backward', count=10, label='10s'),
                    dict(step='second', stepmode='backward', count=30, label='30s'),
                    dict(step='minute', stepmode='backward', count=1, label='1m'),
                    dict(step='all', label='All')
                ]
            ),
            type="linear",
        )
    )
    
    # Shared x-axis behavior
    fig.update_xaxes(matches='x')
    
    # Only bottom row gets x-axis title/ticks
    fig.update_xaxes(title_text=None, showticklabels=False, row=1, col=1)
    fig.update_xaxes(title_text="Time (seconds)", row=2, col=1)
    
    # Update y-axes with better range management
    fig.update_yaxes(title_text="Amplitude (uV)", row=1, col=1)
    fig.update_yaxes(title_text=f"ECG ({ecg_unit_label})", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text=f"CM ({cm_unit_label})", row=2, col=1, secondary_y=True, showgrid=False)
    
    # Improve subplot title visibility
    fig.update_annotations(font_size=12, yshift=8)
    
    # Set reasonable ranges for better visibility
    if available_ecg and ecg_data_cols:
        ecg_data = df[ecg_data_cols].values
        ecg_min, ecg_max = ecg_data.min(), ecg_data.max()
        ecg_padding = (ecg_max - ecg_min) * 0.1
        fig.update_yaxes(range=[ecg_min - ecg_padding, ecg_max + ecg_padding], row=2, col=1, secondary_y=False)
    
    # Set initial range if specified
    if initial_range:
        start_time, end_time = initial_range
        fig.update_layout(
            xaxis=dict(range=[start_time, end_time])
        )
    
    return fig

def add_zoom_controls(fig):

    # Add modebar buttons for better interaction
    fig.update_layout(
        modebar_add=[
            "zoom2d",
            "pan2d", 
            "select2d",
            "lasso2d",
            "zoomIn2d",
            "zoomOut2d",
            "autoScale2d",
            "resetScale2d"
        ]
    )

def save_plot(fig, output_dir="output"):

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save as HTML (interactive)
    html_path = os.path.join(output_dir, "multichannel_plot.html")
    fig.write_html(html_path, include_plotlyjs='cdn')
    print(f"Interactive plot saved to: {html_path}")
    
    # Save static images with error handling
    try:
        # Save as PNG (static image)
        png_path = os.path.join(output_dir, "multichannel_plot.png")
        fig.write_image(png_path, width=1200, height=800, scale=2)
        print(f"Static plot saved to: {png_path}")
        
        # Save as PDF (vector format)
        pdf_path = os.path.join(output_dir, "multichannel_plot.pdf")
        fig.write_image(pdf_path, width=1200, height=800)
        print(f"PDF plot saved to: {pdf_path}")
    except Exception as e:
        print("Note: Static exports require 'kaleido'. Skipping PNG/PDF. Error:", e)
        print("To enable static exports, install: pip install --upgrade kaleido")


# Command line interface
def main():
    parser = argparse.ArgumentParser(description='Create scrollable multichannel plot for EEG/ECG data')
    parser.add_argument('--data', '-d', 
                       default='EEG and ECG data_02_raw.csv',
                       help='Path to CSV data file (default: EEG and ECG data_02_raw.csv)')
    parser.add_argument('--title', '-t',
                       default='EEG and ECG Data Visualization',
                       help='Plot title (default: EEG and ECG Data Visualization)')
    parser.add_argument('--output', '-o',
                       default='output',
                       help='Output directory for saved plots (default: output)')
    parser.add_argument('--show', '-s',
                       action='store_true',
                       help='Show interactive plot in browser')
    parser.add_argument('--channels', nargs='*',
                       help='Subset of channels to plot (names)')
    parser.add_argument('--ecg-units', choices=['uv','mv'], default='mv',
                       help='Plot ECG as µV or mV (default: mV)')
    parser.add_argument('--step', type=int, default=1,
                       help='Downsample step (e.g., 5 keeps every 5th sample)')
    parser.add_argument('--initial-range', nargs=2, type=float, metavar=('START', 'END'),
                       help='Initial time range to display (e.g., --initial-range 0 10)')
    
    args = parser.parse_args()
    
    try:
        # Load data
        df = load_data(args.data, step=args.step)
        
        # Create plot
        print("Creating interactive plot...")
        fig = create_plot(df, args.title, ecg_units=args.ecg_units, channels=args.channels, initial_range=args.initial_range)
        
        # Add zoom controls
        add_zoom_controls(fig)
        
        # Save plots
        save_plot(fig, args.output)
        
        # Show plot if requested
        if args.show:
            print("Opening plot in browser...")
            fig.show()
        else:
            print("Plot created successfully! Use --show to view interactively.")
            
    except FileNotFoundError:
        print(f"Error: Data file '{args.data}' not found.")
        print("Please check the file path and try again.")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check your data format and try again.")

if __name__ == "__main__":
    main()
