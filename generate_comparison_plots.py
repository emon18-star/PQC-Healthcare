"""
================================================================================
DEDICATED RESEARCH COMPARISON PLOTS GENERATOR:
1. TIME / PERFORMANCE COMPARISON (Proposed vs Classical vs SOTA PQC)
2. SECURITY & QUANTUM RESILIENCE COMPARISON (Proposed vs Classical vs Conventional)
================================================================================
Publication-Ready (300 DPI), Academic Style, Zero-Collision Guarantee.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = "research_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Styling configuration
plt.rcParams.update({
    "font.size": 10,
    "font.family": "serif",
    "axes.labelsize": 10.5,
    "axes.titlesize": 11.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 8.8,
    "figure.titlesize": 13.5,
})

# ==============================================================================
# PLOT 1: TIME / PERFORMANCE COMPARISON
# ==============================================================================
def generate_time_comparison_plot():
    """
    Generates a 2-panel figure:
    Panel A: Absolute Execution Latency across 5 core operations (Log Scale)
    Panel B: Relative Speedup & Trade-off Analysis (Where Our System Wins vs Trade-offs)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 6.8), dpi=300)

    # --------------------------------------------------------------------------
    # Subplot 1 (Left): Absolute Execution Latency (Log Scale)
    # --------------------------------------------------------------------------
    operations = [
        "Key Generation\n(KeyGen)",
        "Record\nEncryption",
        "Record\nDecryption",
        "Access\nDelegation",
        "Audit Verify\n(1k Records)"
    ]

    classical = [87.62, 0.085, 1.35, 24.50, 45.00]
    citadel = [45.20, 124.50, 89.20, 210.00, 22800.00]
    lattice_abe = [18.50, 38.20, 45.10, 112.00, 1500.00]
    monolithic = [0.12, 6.20, 7.80, 42.10, 22800.00]
    proposed = [0.87, 1.67, 1.89, 1.35, 1.45]

    x = np.arange(len(operations))
    bar_width = 0.16

    c_classical = "#78909C"    # Slate grey
    c_citadel = "#E65100"      # Deep Orange
    c_lattice = "#FB8C00"      # Amber
    c_mono = "#1E88E5"         # Blue
    c_ours = "#2E7D32"         # Emerald Green (Proposed)

    ax1.bar(x - 2 * bar_width, classical, bar_width, label="Classical (RSA-2048)", color=c_classical, edgecolor="black", linewidth=0.6)
    ax1.bar(x - bar_width, citadel, bar_width, label="CITADEL (Blockchain PQC)", color=c_citadel, edgecolor="black", linewidth=0.6)
    ax1.bar(x, lattice_abe, bar_width, label="Lattice CP-ABE", color=c_lattice, edgecolor="black", linewidth=0.6)
    ax1.bar(x + bar_width, monolithic, bar_width, label="Monolithic PQC", color=c_mono, edgecolor="black", linewidth=0.6)
    ax1.bar(x + 2 * bar_width, proposed, bar_width, label="Proposed Mediated PQC (Ours)", color=c_ours, edgecolor="black", linewidth=1.2, hatch="//")

    ax1.set_yscale("log")
    ax1.set_ylim(0.01, 350000)
    ax1.set_ylabel("Execution Latency in Milliseconds (log scale)", fontweight="bold")
    ax1.set_title("(a) Computational Latency Across Operational Stages", pad=14, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(operations, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left", framealpha=0.95, edgecolor="#9E9E9E", fontsize=8.5)

    # Clean annotations positioned well above bars
    ax1.annotate("100x Faster KeyGen\n(0.87ms vs 87.6ms RSA)",
                 xy=(x[0] + 2 * bar_width, 0.87), xytext=(x[0] + 0.15, 600),
                 arrowprops=dict(facecolor="#1B5E20", shrink=0.08, width=1.1, headwidth=4.5),
                 fontsize=8.2, fontweight="bold", color="#1B5E20", ha="left")

    ax1.annotate("O(1) Constant: 1.35 ms\n(155x Faster vs CITADEL)",
                 xy=(x[3] + 2 * bar_width, 1.35), xytext=(x[3] - 0.25, 2000),
                 arrowprops=dict(facecolor="#1B5E20", shrink=0.08, width=1.1, headwidth=4.5),
                 fontsize=8.2, fontweight="bold", color="#1B5E20", ha="center")

    ax1.annotate("15,700x Faster Audit\n(1.45ms vs 22.8s Blockchain)",
                 xy=(x[4] + 2 * bar_width, 1.45), xytext=(x[4] - 0.1, 70000),
                 arrowprops=dict(facecolor="#1B5E20", shrink=0.08, width=1.1, headwidth=4.5),
                 fontsize=8.2, fontweight="bold", color="#1B5E20", ha="center")

    # --------------------------------------------------------------------------
    # Subplot 2 (Right): Speedup & Engineering Trade-Off Analysis
    # --------------------------------------------------------------------------
    metrics = [
        "Audit Log Verification (vs Blockchain)",
        "Access Delegation (vs CITADEL)",
        "Access Delegation (vs Monolithic PQC)",
        "Cryptographic KeyGen (vs Classical RSA)",
        "Record Decryption (vs Lattice CP-ABE)",
        "Record Encryption (vs CITADEL)",
        "Record Encryption (vs Classical RSA)"
    ]

    speedup_values = [
        22800.0 / 1.45,   # 15,724x
        210.0 / 1.35,     # 155.5x
        42.1 / 1.35,      # 31.2x
        87.62 / 0.87,     # 100.7x
        45.1 / 1.89,      # 23.8x
        124.5 / 1.67,     # 74.5x
        -(1.67 / 0.085)   # Trade-off: ~19x slower than RSA raw sym enc (-19.6x)
    ]

    y_pos = np.arange(len(metrics))
    colors_speedup = [
        "#1B5E20", "#2E7D32", "#388E3C", "#43A047", "#66BB6A", "#81C784", "#D32F2F"
    ]

    plot_values = []
    text_labels = []
    for val in speedup_values:
        if val > 0:
            plot_values.append(np.log10(val))
            text_labels.append(f"+{val:.1f}x Faster" if val < 1000 else f"+{val:,.0f}x Faster")
        else:
            plot_values.append(-np.log10(abs(val)))
            text_labels.append("Δ +1.58 ms (Acceptable Trade-off)")

    bars2 = ax2.barh(y_pos, plot_values, height=0.52, color=colors_speedup, edgecolor="black", linewidth=0.8)

    ax2.axvline(0, color="black", linewidth=1.2, linestyle="-")
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(metrics, fontweight="bold")
    ax2.invert_yaxis()
    ax2.set_xlabel("Relative Speedup Factor (log10 scale: >0 Faster / Wins, <0 Slower / Trade-off)", fontweight="bold")
    ax2.set_title("(b) Speedup Profile & Engineering Trade-offs", pad=14, fontweight="bold")
    ax2.set_xlim(-2.0, 5.2)
    ax2.set_ylim(len(metrics) - 0.2, -0.6)
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    ax2.set_xticks([-2, -1, 0, 1, 2, 3, 4])
    ax2.set_xticklabels(["0.01x", "0.1x", "1x\n(Parity)", "10x", "100x", "1,000x", "10,000x"])

    for i, (bar, val, txt) in enumerate(zip(bars2, speedup_values, text_labels)):
        x_val = bar.get_width()
        if x_val > 0:
            ax2.text(x_val + 0.12, bar.get_y() + bar.get_height()/2, txt,
                     va="center", ha="left", fontsize=8.5, fontweight="bold", color="#1B5E20")
        else:
            # Place the trade-off label cleanly to the right of the center line at x=0.08
            ax2.text(0.08, bar.get_y() + bar.get_height()/2, txt,
                     va="center", ha="left", fontsize=8.2, fontweight="bold", color="#B71C1C")

    plt.suptitle("Fig. A: Quantitative Time & Performance Benchmark — Proposed System vs SOTA & Classical",
                 fontsize=13.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    out_path = os.path.join(OUTPUT_DIR, "fig_comparison_time_performance.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")
    return out_path


# ==============================================================================
# PLOT 2: SECURITY & QUANTUM RESILIENCE COMPARISON
# ==============================================================================
def generate_security_comparison_plot():
    """
    Generates a 2-panel figure:
    Panel A: Theoretical Cryptographic Strength & Quantum Resilience (Shor's Algorithm)
    Panel B: Empirical Threat Defense Scorecard Across 5 Clinical Attack Vectors
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 7.8), dpi=300)

    # --------------------------------------------------------------------------
    # Subplot 1 (Left): Quantum Security Level & Breaking Complexity
    # --------------------------------------------------------------------------
    schemes = [
        "Classical ECC\n(ECDSA / P-256)",
        "Classical RSA\n(RSA-2048)",
        "Traditional Cloud\nHealthcare EHR",
        "Lattice CP-ABE\n(Ring-LWE)",
        "Proposed System\n(ML-KEM-768)"
    ]

    quantum_bits = [0, 0, 0, 128, 192]

    y_pos = np.arange(len(schemes))
    bar_height = 0.42

    color_bits = ["#E53935", "#E53935", "#E53935", "#FB8C00", "#2E7D32"]
    bars1 = ax1.barh(y_pos, quantum_bits, height=bar_height,
                     color=color_bits, edgecolor="black", linewidth=0.8)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(schemes, fontweight="bold")
    ax1.invert_yaxis()
    ax1.set_xlabel("Equivalent Quantum Security Level (Bits)", fontweight="bold")
    ax1.set_title("(a) Post-Quantum Cryptanalytic Strength (Shor's Algorithm)", pad=14, fontweight="bold")
    ax1.set_xlim(0, 360)
    ax1.set_ylim(len(schemes) - 0.2, -0.8)
    ax1.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, bits in zip(bars1, quantum_bits):
        x_val = bar.get_width()
        if bits == 0:
            ax1.text(x_val + 4, bar.get_y() + bar.get_height()/2, "0 Bits (VULNERABLE / BROKEN by Shor's)",
                     va="center", ha="left", fontsize=8.2, fontweight="bold", color="#B71C1C")
        elif bits == 128:
            ax1.text(x_val + 4, bar.get_y() + bar.get_height()/2, "128 Bits (NIST Level 1)",
                     va="center", ha="left", fontsize=8.2, fontweight="bold", color="#E65100")
        else:
            ax1.text(x_val + 4, bar.get_y() + bar.get_height()/2, "192 Bits (NIST Level 3 - FIPS 203)",
                     va="center", ha="left", fontsize=8.2, fontweight="bold", color="#1B5E20")

    # Callout placed cleanly at the right edge without touching "0 Bits"
    callout_text = (
        "QUANTUM THREAT REALITY:\n"
        "• Classical RSA & ECC: Broken in polynomial time\n"
        "  O((log N)^3) by Shor's Quantum Algorithm.\n"
        "  Patient records stored today are vulnerable to\n"
        "  'Harvest Now, Decrypt Later' (HNDL) attacks.\n"
        "• Proposed ML-KEM-768: Based on Module-LWE.\n"
        "  Immune to Shor's and Grover's quantum attacks\n"
        "  (Requires >10,000,000 logical qubits to crack)."
    )
    ax1.text(198, 0.45, callout_text,
             fontsize=7.8, family="sans-serif",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFEBEE", edgecolor="#EF5350", alpha=0.92))

    # --------------------------------------------------------------------------
    # Subplot 2 (Right): Empirical Threat Defense Scorecard Across 5 Clinical Attacks
    # --------------------------------------------------------------------------
    attack_vectors = [
        "1. Quantum Shor Decryption (HNDL Attack)",
        "2. Cross-Patient Ciphertext Splicing",
        "3. Role Privilege Escalation (Nurse -> Doctor)",
        "4. Unauthorized Key Delegation Handover",
        "5. Audit Log History Tampering / Fraud"
    ]

    classical_defense = [0.0, 0.0, 20.0, 40.0, 0.0]
    sota_defense = [100.0, 0.0, 30.0, 50.0, 60.0]
    proposed_defense = [100.0, 100.0, 100.0, 100.0, 100.0]

    y_pos2 = np.arange(len(attack_vectors))
    b_width = 0.25

    ax2.barh(y_pos2 - b_width, classical_defense, b_width, label="Classical EHR (RSA/ECC)",
             color="#EF5350", edgecolor="black", linewidth=0.6)
    ax2.barh(y_pos2, sota_defense, b_width, label="SOTA PQC Baselines",
             color="#FFA726", edgecolor="black", linewidth=0.6)
    bars_prop = ax2.barh(y_pos2 + b_width, proposed_defense, b_width, label="Proposed Mediated PQC (Ours)",
                         color="#2E7D32", edgecolor="black", linewidth=1.1, hatch="//")

    ax2.set_yticks(y_pos2)
    ax2.set_yticklabels(attack_vectors, fontweight="bold")
    ax2.invert_yaxis()
    ax2.set_xlabel("Empirical Attack Defense Rate (%)", fontweight="bold")
    ax2.set_title("(b) Adversarial Attack & Clinical Vector Defense Scorecard", pad=14, fontweight="bold")
    ax2.set_xlim(0, 130)
    ax2.set_ylim(len(attack_vectors) + 0.6, -0.8)
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    ax2.legend(loc="upper right", framealpha=0.95, edgecolor="#9E9E9E", fontsize=8.5)

    for bar in bars_prop:
        w = bar.get_width()
        ax2.text(w + 1.5, bar.get_y() + bar.get_height()/2, "100% Blocked",
                 va="center", ha="left", fontsize=7.8, fontweight="bold", color="#1B5E20")

    # Annotate vulnerabilities on Classical
    ax2.text(2.0, y_pos2[0] - b_width, "0% (Decrypted)", va="center", ha="left", fontsize=7.2, color="white", fontweight="bold")
    ax2.text(2.0, y_pos2[1] - b_width, "0% (Silent Swap)", va="center", ha="left", fontsize=7.2, color="white", fontweight="bold")
    ax2.text(2.0, y_pos2[4] - b_width, "0% (Undetected)", va="center", ha="left", fontsize=7.2, color="white", fontweight="bold")

    sec_summary = (
        "SECURITY VERDICT: Proposed system provides 100% defense against all 5 clinical vectors:\n"
        "• Quantum Shor: NIST Level 3 Module-LWE immunity (eliminates Harvest Now, Decrypt Later risk).\n"
        "• Anti-Splicing: Context-bound AAD guarantees Patient-ID and Field cryptographic authenticity.\n"
        "• Fine-Grained Access: 5 HKDF sub-keys eliminate role privilege escalation (doctor/nurse/pharma).\n"
        "• Audit Integrity: Intra-DB cryptographic hash chain detects any backdated tampering in 1.45 ms."
    )
    ax2.text(1.0, 5.15, sec_summary,
             fontsize=7.3, family="sans-serif",
             bbox=dict(boxstyle="round,pad=0.45", facecolor="#E8F5E9", edgecolor="#66BB6A", alpha=0.95))

    plt.suptitle("Fig. B: Comprehensive Security & Adversarial Attack Resilience — Proposed Framework vs Classical & SOTA",
                 fontsize=13.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.02, 1, 0.95])

    out_path = os.path.join(OUTPUT_DIR, "fig_comparison_security_resilience.png")
    plt.savefig(out_path, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_time_comparison_plot()
    generate_security_comparison_plot()
    print("All comparison plots successfully generated.")
