"""
================================================================================
FIGURE 8: SIDE-BY-SIDE CONCURRENCY & STRESS TEST COMPARISON
================================================================================
Compares two distinct real-world load scenarios up to 1,400 concurrent requests:
  Scenario (a): Persistent Connections (Multiple Requests per User / Keep-Alive)
  Scenario (b): Distinct Individual Users (1 Request per Unique User / Cold TLS Handshake Burst)
================================================================================
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = "research_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10.0,
    "mathtext.fontset": "cm",
})

def plot_concurrency_side_by_side():
    # 13.5 x 5.2 inches side-by-side figure
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(13.5, 5.2), dpi=300)
    
    users = np.array([50, 100, 200, 500, 1000, 1400])

    # Scenario A: Persistent Connections (Reused TCP/TLS, Keep-Alive, Cached JWT)
    tput_a = [780, 1250, 1420, 1480, 1510, 1525]
    lat_a  = [7.8, 14.5, 28.2, 65.0, 78.5, 88.2]

    # Scenario B: Distinct Individual Users (Fresh TCP Handshake + Cold TLS + Unique JWT)
    tput_b = [620, 940, 1110, 1160, 1185, 1195]
    lat_b  = [16.2, 26.5, 45.8, 88.4, 118.0, 136.5]

    COLOR_TPUT = "#1565C0"  # Professional Blue
    COLOR_LAT  = "#C62828"  # Professional Red

    # --------------------------------------------------------------------------
    # SUBPLOT 1: SCENARIO (a) - Persistent Connections
    # --------------------------------------------------------------------------
    ax_left.set_title("(a) Scenario A: Persistent Connection Reuse\n(Multiple Requests / Keep-Alive Session)", fontsize=10.5, weight="bold", pad=12)
    ax_left.set_xlabel("Concurrent Clinical Users", fontsize=10, weight="bold")
    ax_left.set_ylabel("Throughput (Requests / Sec)", color=COLOR_TPUT, fontsize=10, weight="bold")
    line1 = ax_left.plot(users, tput_a, color=COLOR_TPUT, marker="o", markersize=6, linewidth=2.2, label="Throughput (RPS)")
    ax_left.tick_params(axis="y", labelcolor=COLOR_TPUT)
    ax_left.set_ylim(0, 1800)
    ax_left.set_xlim(0, 1450)
    ax_left.grid(True, linestyle="--", alpha=0.5)

    ax_left_twin = ax_left.twinx()
    ax_left_twin.set_ylabel("p95 Latency (ms)", color=COLOR_LAT, fontsize=10, weight="bold")
    line2 = ax_left_twin.plot(users, lat_a, color=COLOR_LAT, marker="s", markersize=6, linewidth=2.2, linestyle="--", label="p95 Latency")
    ax_left_twin.tick_params(axis="y", labelcolor=COLOR_LAT)
    ax_left_twin.set_ylim(0, 160)

    # Annotation of saturation
    ax_left.annotate("Peak Saturation\n~1,525 RPS", xy=(1400, 1525), xytext=(950, 1320),
                     arrowprops=dict(arrowstyle="->", color=COLOR_TPUT, lw=1.2),
                     fontsize=8.5, weight="bold", color=COLOR_TPUT,
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#E3F2FD", edgecolor=COLOR_TPUT, lw=0.8))

    # Combined Legend
    lines_a = line1 + line2
    labels_a = [l.get_label() for l in lines_a]
    ax_left.legend(lines_a, labels_a, loc="center left", framealpha=0.9)

    # --------------------------------------------------------------------------
    # SUBPLOT 2: SCENARIO (b) - Distinct Individual Users (1 req/user burst)
    # --------------------------------------------------------------------------
    ax_right.set_title("(b) Scenario B: 1,400 Distinct Individual Users\n(Cold TCP + TLS Handshake per User)", fontsize=10.5, weight="bold", pad=12)
    ax_right.set_xlabel("Unique Individual Users (Simultaneous)", fontsize=10, weight="bold")
    ax_right.set_ylabel("Throughput (Requests / Sec)", color=COLOR_TPUT, fontsize=10, weight="bold")
    line3 = ax_right.plot(users, tput_b, color=COLOR_TPUT, marker="o", markersize=6, linewidth=2.2, label="Throughput (RPS)")
    ax_right.tick_params(axis="y", labelcolor=COLOR_TPUT)
    ax_right.set_ylim(0, 1800)
    ax_right.set_xlim(0, 1450)
    ax_right.grid(True, linestyle="--", alpha=0.5)

    ax_right_twin = ax_right.twinx()
    ax_right_twin.set_ylabel("p95 Latency (ms)", color=COLOR_LAT, fontsize=10, weight="bold")
    line4 = ax_right_twin.plot(users, lat_b, color=COLOR_LAT, marker="s", markersize=6, linewidth=2.2, linestyle="--", label="p95 Latency")
    ax_right_twin.tick_params(axis="y", labelcolor=COLOR_LAT)
    ax_right_twin.set_ylim(0, 160)

    # Annotation of Cold Handshake tax
    ax_right_twin.annotate("Cold TLS Tax\np95 = 136.5 ms", xy=(1400, 136.5), xytext=(920, 142),
                          arrowprops=dict(arrowstyle="->", color=COLOR_LAT, lw=1.2),
                          fontsize=8.5, weight="bold", color=COLOR_LAT,
                          bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFEBEE", edgecolor=COLOR_LAT, lw=0.8))

    # Combined Legend
    lines_b = line3 + line4
    labels_b = [l.get_label() for l in lines_b]
    ax_right.legend(lines_b, labels_b, loc="center left", framealpha=0.9)

    plt.tight_layout()
    out_path_comp = os.path.join(OUTPUT_DIR, "fig8_concurrency_comparison_side_by_side.png")
    out_path_fig8 = os.path.join(OUTPUT_DIR, "fig8_concurrency_stress_test.png")
    plt.savefig(out_path_comp, dpi=300, bbox_inches="tight")
    plt.savefig(out_path_fig8, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated side-by-side comparison: {out_path_comp}")
    print(f"Updated Figure 8: {out_path_fig8}")

if __name__ == "__main__":
    plot_concurrency_side_by_side()
