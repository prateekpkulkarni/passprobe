import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

# --- AESTHETIC CONFIGURATION ---
plt.rcParams.update({
    'font.family': 'serif',
    'axes.labelsize': 10,
    'font.size': 10,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 300
})

# --- PLOTTING FUNCTIONS ---

def plot_figure_2(df_shapley, out_dir):
    """
    Reproduces Figure 2: Shapley attribution by pass category.
    Expects df_shapley to have columns: ['Compiler', 'Workload', 'Pass_Category', 'Shapley_Value']
    """
    compilers = df_shapley['Compiler'].unique()
    fig, axes = plt.subplots(1, len(compilers), figsize=(16, 4), sharey=True)
    
    # Handle case where there is only one compiler in the dataset
    if len(compilers) == 1:
        axes = [axes]
        
    for ax, compiler in zip(axes, compilers):
        df_comp = df_shapley[df_shapley['Compiler'] == compiler]
        # Pivot to create the Heatmap matrix (Workloads as rows, Passes as columns)
        pivot_df = df_comp.pivot(index='Workload', columns='Pass_Category', values='Shapley_Value').fillna(0)
        
        sns.heatmap(pivot_df, ax=ax, cmap="BuGn", cbar=False, vmin=0.0, vmax=df_shapley['Shapley_Value'].max())
        ax.set_title(compiler)
        ax.tick_params(axis='x', rotation=45)
        ax.set_xlabel('')
        ax.set_ylabel('')
    
    axes[0].set_ylabel('Workload Class')
    
    # Unified colorbar
    cbar_ax = fig.add_axes([0.15, -0.1, 0.7, 0.04])
    sm = plt.cm.ScalarMappable(cmap="BuGn", norm=plt.Normalize(vmin=0, vmax=df_shapley['Shapley_Value'].max()))
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Shapley Attribution')
    
    plt.tight_layout(rect=[0, 0, 1, 1])
    out_path = Path(out_dir) / 'figure_2_shapley_heatmap.pdf'
    plt.savefig(out_path, bbox_inches='tight')
    print(f"[✓] Saved Figure 2 to {out_path}")
    plt.close()

def plot_figure_3(df_concentration, out_dir):
    """
    Reproduces Figure 3: Shapley concentration and negligible passes.
    Expects columns: ['Workload', 'CR1', 'CR2', 'CR3', 'Neg_Passes']
    """
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    
    x = np.arange(len(df_concentration['Workload']))
    width = 0.2
    
    ax1.bar(x - width, df_concentration['CR1'], width, label='CR_1', color='#e0f3db', edgecolor='black')
    ax1.bar(x, df_concentration['CR2'], width, label='CR_2', color='#a8ddb5', edgecolor='black')
    ax1.bar(x + width, df_concentration['CR3'], width, label='CR_3', color='#43a2ca', edgecolor='black')
    
    ax2.plot(x, df_concentration['Neg_Passes'], color='#e34a33', marker='o', linewidth=2, label='#Neg Passes')
    
    ax1.set_xlabel('Workload Class')
    ax1.set_ylabel('Concentration Ratio $CR_{m}$')
    ax2.set_ylabel('#Neg Passes ($\hat{\phi}_i < 0.02$)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_concentration['Workload'])
    ax1.set_ylim(0, 1.1)
    
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=4)
    
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    out_path = Path(out_dir) / 'figure_3_concentration.pdf'
    plt.savefig(out_path, bbox_inches='tight')
    print(f"[✓] Saved Figure 3 to {out_path}")
    plt.close()

def plot_figure_4(df_structural, out_dir):
    """
    Reproduces Figure 4: Structural drivers.
    Expects columns: ['Compiler', 'Circuit', 'Logical_Connectivity', 'Routing_Shapley', 'Idle_Time_Potential', 'Scheduling_Shapley']
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # (a) Routing vs Logical Connectivity
    sns.scatterplot(data=df_structural, x='Logical_Connectivity', y='Routing_Shapley', hue='Compiler', ax=ax1, s=60)
    sns.regplot(data=df_structural, x='Logical_Connectivity', y='Routing_Shapley', scatter=False, ax=ax1, color='black', line_kws={'linestyle': '--'})
    ax1.set_title('(a) Routing vs. Logical Connectivity')
    ax1.set_xlabel('Logical Connectivity Score\n(0=Sparse, 1=Dense)')
    ax1.set_ylabel('Routing Shapley Value ($\hat{\phi}_{routing}$)')
    
    # (b) Scheduling vs Idle-Time Potential
    sns.scatterplot(data=df_structural, x='Idle_Time_Potential', y='Scheduling_Shapley', hue='Compiler', ax=ax2, s=60)
    sns.regplot(data=df_structural, x='Idle_Time_Potential', y='Scheduling_Shapley', scatter=False, ax=ax2, color='black', line_kws={'linestyle': '--'})
    ax2.set_title('(b) Scheduling vs. Idle-Time Potential')
    ax2.set_xlabel('Idle-Time Potential Score')
    ax2.set_ylabel('Scheduling Shapley Value ($\hat{\phi}_{sched}$)')
    
    plt.tight_layout()
    out_path = Path(out_dir) / 'figure_4_structural_drivers.pdf'
    plt.savefig(out_path, bbox_inches='tight')
    print(f"[✓] Saved Figure 4 to {out_path}")
    plt.close()

def plot_figure_5(df_ordering, df_pruning, out_dir):
    """
    Reproduces Figure 5: Ordering sensitivity and Pass Pruning.
    df_ordering columns: ['Workload', 'Omega_V', 'Omega_E', 'Omega_all']
    df_pruning columns: ['Compiler', 'Delta_T', 'Delta_Q']
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # (a) Ordering Sensitivity
    if not df_ordering.empty:
        x_ord = np.arange(len(df_ordering['Workload']))
        width = 0.25
        ax1.bar(x_ord - width, df_ordering['Omega_V'], width, label='$\Omega_V$', color='#f0f9e8', edgecolor='black')
        ax1.bar(x_ord, df_ordering['Omega_E'], width, label='$\Omega_E$', color='#bae4bc', edgecolor='black')
        ax1.bar(x_ord + width, df_ordering['Omega_all'], width, label='$\Omega_{all}$', color='#2b8cbe', edgecolor='black')
        
        ax1.axhline(1.0, color='red', linestyle='--', alpha=0.6)
        ax1.set_xticks(x_ord)
        ax1.set_xticklabels(df_ordering['Workload'], rotation=25)
        ax1.set_ylabel('Ordering Sensitivity $\Omega$')
        ax1.legend(loc='upper right')
        ax1.set_title('(a) Ordering Sensitivity')
    
    # (b) Pass Pruning Effects
    if not df_pruning.empty:
        ax2_left = ax2
        ax2_right = ax2.twinx()
        
        x_prun = np.arange(len(df_pruning['Compiler']))
        width_prun = 0.35
        
        bars1 = ax2_left.bar(x_prun - width_prun/2, df_pruning['Delta_T'], width_prun, label='$\Delta T$ (%)', color='#a8ddb5', edgecolor='black')
        bars2 = ax2_right.bar(x_prun + width_prun/2, df_pruning['Delta_Q'], width_prun, label='$\Delta Q$ (%)', color='#0868ac', edgecolor='black')
        
        ax2_left.set_ylabel('$\Delta T$ (%)')
        ax2_right.set_ylabel('$\Delta Q$ (%)')
        ax2_left.set_xticks(x_prun)
        ax2_left.set_xticklabels(df_pruning['Compiler'])
        
        # Scale dynamically based on data limits, but ensure 0 line is visible
        ax2_left.axhline(0, color='black', linewidth=1)
        
        lines_prun = [bars1, bars2]
        labels_prun = [bar.get_label() for bar in lines_prun]
        ax2_left.legend(lines_prun, labels_prun, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)
        ax2_left.set_title('(b) Pass Pruning Effects')
    
    plt.tight_layout()
    out_path = Path(out_dir) / 'figure_5_ordering_pruning.pdf'
    plt.savefig(out_path, bbox_inches='tight')
    print(f"[✓] Saved Figure 5 to {out_path}")
    plt.close()

# --- CLI ENTRY POINT ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PassProbe Plotting Engine")
    
    parser.add_argument('--shapley', type=str, help='Path to shapley attribution CSV for Fig 2')
    parser.add_argument('--concentration', type=str, help='Path to concentration ratios CSV for Fig 3')
    parser.add_argument('--structural', type=str, help='Path to structural drivers CSV for Fig 4')
    parser.add_argument('--ordering', type=str, help='Path to ordering sensitivity CSV for Fig 5a')
    parser.add_argument('--pruning', type=str, help='Path to pruning effects CSV for Fig 5b')
    parser.add_argument('--out_dir', type=str, default='.', help='Directory to save output PDFs')
    
    args = parser.args()
    
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    
    if args.shapley:
        print("Loading Shapley data...")
        df_shapley = pd.read_csv(args.shapley)
        plot_figure_2(df_shapley, args.out_dir)
        
    if args.concentration:
        print("Loading Concentration data...")
        df_conc = pd.read_csv(args.concentration)
        plot_figure_3(df_conc, args.out_dir)
        
    if args.structural:
        print("Loading Structural Drivers data...")
        df_struct = pd.read_csv(args.structural)
        plot_figure_4(df_struct, args.out_dir)
        
    if args.ordering or args.pruning:
        print("Loading Ordering/Pruning data...")
        df_ord = pd.read_csv(args.ordering) if args.ordering else pd.DataFrame()
        df_prun = pd.read_csv(args.pruning) if args.pruning else pd.DataFrame()
        plot_figure_5(df_ord, df_prun, args.out_dir)
        
    print("All requested plots generated successfully.")
