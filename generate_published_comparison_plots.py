import matplotlib.pyplot as plt
import numpy as np

# Set high-quality styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# ==============================================================================
# PLOT 1: Cryptographic Latency and Storage Overhead Comparison
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7.8), dpi=300)

paper_full_title = 'Empirical Comparison with "PQ-FundusChain: A Postquantum Blockchain Framework for Secure and Privacy-Preserving\nRetinal Fundus Image Sharing in Teleophthalmology" (Kirubakaran & Vijayarajan, Frontiers in Digital Health, 2026)'

fig.suptitle(paper_full_title, fontsize=13.5, fontweight='bold', y=0.98)

# --- Subplot (a): Latency ---
ops = [
    "KEM KeyGen\n(ML-KEM-768)",
    "Encapsulation\n(Wrap Key)",
    "Decapsulation\n(Unwrap Key)",
    "E2E Encrypt\nPipeline",
    "E2E Decrypt\nPipeline"
]

pq_fundus_latency = [0.068, 0.077, 0.095, 4.02, 3.48]
# True measured benchmark: 0.87 ms (raw primitive), 0.12 ms encaps, 0.14 ms decaps
our_latency = [0.87, 0.120, 0.140, 1.89, 2.15]

x = np.arange(len(ops))
width = 0.35

rects1 = ax1.bar(x - width/2, pq_fundus_latency, width, 
                 label="PQ-FundusChain [Frontiers in Digital Health 2026, Table 8 & 10]\n(C-liboqs Reference on Intel Xeon 2.8GHz)", 
                 color='#C62828', edgecolor='#1A1A1A', linewidth=0.9, alpha=0.9)
rects2 = ax1.bar(x + width/2, our_latency, width, 
                 label="Our Proposed Framework (PQC-FLGC)\n(Field-Level HKDF + AES-256-GCM Ingest Pipeline)", 
                 color='#2E7D32', edgecolor='#1A1A1A', linewidth=0.9, alpha=0.92)

ax1.set_ylabel("Execution Time in ms (log scale)", fontsize=11, fontweight='bold')
ax1.set_title("(a) Execution Latency Benchmark (from Published Table 8 & Table 10)", fontsize=11.5, fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(ops, fontsize=9.5, fontweight='bold')
ax1.set_yscale('log')
ax1.set_ylim(0.015, 15)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
ax1.legend(loc='upper left', frameon=True, facecolor='#FAFAFA', edgecolor='#CCCCCC', fontsize=8.5)

# Value labels on latency
for rect in rects1:
    h = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width()/2., h * 1.15, f"{h:.3f}ms" if h < 1 else f"{h:.2f}ms",
             ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#B71C1C')

for rect in rects2:
    h = rect.get_height()
    ax1.text(rect.get_x() + rect.get_width()/2., h * 1.15, f"{h:.3f}ms" if h < 1 else f"{h:.2f}ms",
             ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1B5E20')

ax1.annotate('Our E2E Ingest is 2.1x faster\n(1.89 ms vs 4.02 ms in Table 10)',
             xy=(3 + width/2, 1.89), xytext=(2.6, 6.5),
             arrowprops=dict(facecolor='#1B5E20', shrink=0.08, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#1B5E20',
             bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=0.8))

# --- Subplot (b): Storage Overhead ---
storage_cats = [
    "KEM CT +\nWrapped Key",
    "Auth / Signature\nOverhead",
    "Metadata &\nAccess Policy",
    "Total Fixed\nOverhead"
]

pq_fundus_storage = [1128, 3309, 507, 4944]
our_storage = [1136, 32, 102, 1270]

x2 = np.arange(len(storage_cats))

rects3 = ax2.bar(x2 - width/2, pq_fundus_storage, width, 
                 label="PQ-FundusChain [Frontiers in Digital Health 2026, Table 9]\n(With 3,309 B ML-DSA Signature on Ledger)", 
                 color='#E57373', edgecolor='#1A1A1A', linewidth=0.9, alpha=0.9)
rects4 = ax2.bar(x2 + width/2, our_storage, width, 
                 label="Our Proposed Framework (PQC-FLGC)\n(Context-Bound Lightweight Authentication Overhead)", 
                 color='#66BB6A', edgecolor='#1A1A1A', linewidth=0.9, alpha=0.92)

ax2.set_ylabel("Storage Overhead in Bytes", fontsize=11, fontweight='bold')
ax2.set_title("(b) Storage Footprint per Record (from Published Table 9)", fontsize=11.5, fontweight='bold', pad=10)
ax2.set_xticks(x2)
ax2.set_xticklabels(storage_cats, fontsize=9.5, fontweight='bold')
ax2.set_ylim(0, 6200)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
ax2.legend(loc='upper left', frameon=True, facecolor='#FAFAFA', edgecolor='#CCCCCC', fontsize=8.5)

# Value labels on storage
for rect in rects3:
    h = rect.get_height()
    ax2.text(rect.get_x() + rect.get_width()/2., h + 70, f"{int(h)} B",
             ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#B71C1C')

for rect in rects4:
    h = rect.get_height()
    ax2.text(rect.get_x() + rect.get_width()/2., h + 70, f"{int(h)} B",
             ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1B5E20')

ax2.annotate('74.3% Storage Reduction\n(1,270 B vs 4,944 B in Table 9)',
             xy=(3 + width/2, 1270), xytext=(2.1, 4000),
             arrowprops=dict(facecolor='#1B5E20', shrink=0.08, width=1.5, headwidth=6),
             fontsize=8.5, fontweight='bold', color='#1B5E20',
             bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", lw=0.8))

plt.tight_layout()
plt.subplots_adjust(top=0.89)
plt.savefig("c:/pqc_healthcare/research_figures/fig_comparison_published_frontiers_table.png", dpi=300)
plt.close()
print("Figure 1 updated with true KeyGen 0.87 ms!")
