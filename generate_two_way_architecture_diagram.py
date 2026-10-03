"""
================================================================================
TWO-WAY LIFECYCLE ARCHITECTURE DIAGRAM: PQC HEALTHCARE EHR SYSTEM
================================================================================
Illustrates the dual cryptographic lifecycle:
  1. Top Lane: Data Ingress (Granular Encryption & Secure Storage Flow)
  2. Middle Zone: Cloud Mediator (Zero-Plaintext Store, O(1) Delegation & Hash Chain)
  3. Bottom Lane: Data Egress (Access Request, Delegation & Role-Gated In-Memory Decryption)
================================================================================
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUTPUT_DIR = "research_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Typography Configuration (Serif Academic Style)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "figure.autolayout": False,
})

def draw_rounded_card(ax, x, y, w, h, bg_color, border_color, lw=1.1, radius=0.6, zorder=2, linestyle='-'):
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle=f"round,pad=0.1,rounding_size={radius}",
                           facecolor=bg_color, edgecolor=border_color,
                           linewidth=lw, linestyle=linestyle, zorder=zorder)
    ax.add_patch(patch)
    return patch

def draw_badge(ax, cx, cy, text, bg_color="#1E293B", text_color="#FFFFFF", font_size=7.2, pad_w=1.2, h=2.8, zorder=5):
    w = max(len(text) * 0.9 + pad_w, 10.0)
    x = cx - w / 2.0
    y = cy - h / 2.0
    patch = FancyBboxPatch((x, y), w, h,
                           boxstyle="round,pad=0.1,rounding_size=1.0",
                           facecolor=bg_color, edgecolor="none",
                           zorder=zorder)
    ax.add_patch(patch)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=font_size,
            fontweight="bold", color=text_color, zorder=zorder+1)

def draw_arrow(ax, p1, p2, color="#334155", lw=1.3, style="-|>", rad=0.0, zorder=6, linestyle='-'):
    arrow = FancyArrowPatch(p1, p2,
                            connectionstyle=f"arc3,rad={rad}",
                            arrowstyle=f"{style},head_length=4.5,head_width=3.0",
                            color=color, linewidth=lw, linestyle=linestyle, zorder=zorder)
    ax.add_patch(arrow)
    return arrow

def generate_two_way_architecture():
    # Canvas: 21.0 x 14.5 inches landscape (High DPI Publication layout)
    fig, ax = plt.subplots(figsize=(21.0, 14.5), dpi=300)
    ax.set_xlim(0, 210)
    ax.set_ylim(0, 145)
    ax.axis("off")

    # =========================================================================
    # 0. MAIN TITLE & SUBTITLE BANNER
    # =========================================================================
    top_banner = FancyBboxPatch((4.0, 134.0), 202.0, 8.5,
                               boxstyle="round,pad=0.2,rounding_size=0.8",
                               facecolor="#0F172A", edgecolor="#020617", lw=1.4, zorder=2)
    ax.add_patch(top_banner)
    ax.text(105.0, 139.3, 
            "Two-Way Cryptographic Data Lifecycle: Ingress (Write/Encrypt) vs. Egress (Delegation/Decrypt)",
            ha="center", va="center", fontsize=12.2, weight="bold", color="#FFFFFF", zorder=3)
    ax.text(105.0, 136.2, 
            "End-to-End Security Architecture with ML-KEM-768 Key Encapsulation, Context-Bound AAD, O(1) Cloud Delegation & Role-Gated Decryption",
            ha="center", va="center", fontsize=8.2, style="italic", color="#94A3B8", zorder=3)

    # =========================================================================
    # 1. TOP LANE: DATA INGRESS PIPELINE (y = 81.0 to 131.0)
    # =========================================================================
    lane1 = FancyBboxPatch((4.0, 81.0), 202.0, 50.0,
                           boxstyle="round,pad=0.2,rounding_size=1.0",
                           facecolor="#F8FAFC", edgecolor="#94A3B8", lw=1.3, linestyle="--", zorder=1)
    ax.add_patch(lane1)

    # Lane 1 Header Ribbon
    l1_hdr = FancyBboxPatch((5.5, 125.0), 75.0, 5.0,
                            boxstyle="round,pad=0.1,rounding_size=0.5",
                            facecolor="#1E3A8A", edgecolor="none", zorder=2)
    ax.add_patch(l1_hdr)
    ax.text(43.0, 127.5, "PATH A: DATA INGRESS PIPELINE (RECORD CREATION & ENCRYPTION)",
            ha="center", va="center", fontsize=7.8, weight="bold", color="#FFFFFF", zorder=3)

    # Step 1.1: Plaintext Ingress & Field Splitting
    draw_rounded_card(ax, 7.0, 84.0, 36.0, 38.0, "#EFF6FF", "#3B82F6", lw=1.1)
    draw_badge(ax, 25.0, 119.0, "STEP 1: CLINICAL INGRESS", bg_color="#2563EB", text_color="#FFFFFF", font_size=6.8)
    ax.text(9.0, 114.5, "Input: Patient Clinical Data", fontsize=7.2, weight="bold", color="#1E3A8A", zorder=3)
    ax.text(9.0, 111.5, r"Patient Identity: $\mathrm{PID} \in \mathrm{UUID}$", fontsize=6.8, color="#1E40AF", zorder=3)
    
    fields = [
        ("diagnosis: Acute Coronary", "#DBEAFE", "#1D4ED8"),
        ("symptoms: Chest Pain, SOB", "#DBEAFE", "#1D4ED8"),
        ("treatment: Percutaneous Angio", "#DBEAFE", "#1D4ED8"),
        ("prescription: Nitroglycerin 0.4mg", "#DBEAFE", "#1D4ED8"),
        ("doctor_notes: High Risk Follow-up", "#DBEAFE", "#1D4ED8"),
    ]
    for idx, (f_txt, f_bg, f_border) in enumerate(fields):
        fy = 107.0 - idx * 3.8
        f_card = FancyBboxPatch((9.0, fy - 1.2), 32.0, 3.0,
                                boxstyle="round,pad=0.05,rounding_size=0.3",
                                facecolor=f_bg, edgecolor=f_border, lw=0.6, zorder=3)
        ax.add_patch(f_card)
        ax.text(10.5, fy + 0.3, f"• {f_txt}", fontsize=6.2, color="#1E293B", zorder=4)

    ax.text(25.0, 86.2, "Granular Field Decomposition", ha="center", fontsize=6.2, style="italic", color="#2563EB", zorder=3)

    # Step 1.2: Root Keygen & Context-Bound AAD Construction
    draw_rounded_card(ax, 47.0, 84.0, 42.0, 38.0, "#F5F3FF", "#8B5CF6", lw=1.1)
    draw_badge(ax, 68.0, 119.0, "STEP 2: KEY HIERARCHY & AAD", bg_color="#7C3AED", text_color="#FFFFFF", font_size=6.8)

    # Root keygen
    k_box = FancyBboxPatch((49.0, 108.5), 38.0, 7.5, boxstyle="round,pad=0.1,rounding_size=0.4",
                           facecolor="#EDE9FE", edgecolor="#7C3AED", lw=0.7, zorder=3)
    ax.add_patch(k_box)
    ax.text(68.0, 113.8, "1. Ephemeral Root Session Key:", ha="center", fontsize=6.6, weight="bold", color="#4C1D95", zorder=4)
    ax.text(68.0, 110.8, r"$K_{session} \leftarrow_R \mathrm{AESGCM.generate\_key}(256)$", ha="center", fontsize=6.5, color="#5B21B6", zorder=4)

    # Sub-key HKDF
    ax.text(49.0, 105.0, "2. HKDF-SHA256 Sub-Key Expansion:", fontsize=6.6, weight="bold", color="#4C1D95", zorder=3)
    ax.text(50.0, 102.2, r"$K_{field} = \mathrm{HKDF}(K_{session},\ \mathrm{'pqc\text{-}field:'}\parallel field\parallel\mathrm{PID})$", fontsize=6.3, color="#3730A3", zorder=3)

    # AAD Construction
    aad_box = FancyBboxPatch((49.0, 87.0), 38.0, 12.0, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor="#DDD6FE", edgecolor="#6D28D9", lw=0.8, zorder=3)
    ax.add_patch(aad_box)
    ax.text(68.0, 96.5, "3. Context-Bound AAD Construction:", ha="center", fontsize=6.6, weight="bold", color="#4C1D95", zorder=4)
    ax.text(68.0, 93.0, r"$AAD = \mathrm{'patient:'}\parallel\mathrm{PID}\parallel\mathrm{':field:'}\parallel field$", ha="center", fontsize=6.5, weight="bold", color="#2E1065", zorder=4)
    ax.text(68.0, 89.2, "Binds ciphertext to exact patient & field (Anti-Splicing)", ha="center", fontsize=5.8, style="italic", color="#4C1D95", zorder=4)

    # Step 1.3: Dual Hybrid Encryption (Field AEAD + Post-Quantum KEM)
    draw_rounded_card(ax, 93.0, 84.0, 52.0, 38.0, "#FEF3C7", "#D97706", lw=1.2)
    draw_badge(ax, 119.0, 119.0, "STEP 3: HYBRID ENCRYPTION", bg_color="#B45309", text_color="#FFFFFF", font_size=6.8)

    # Left sub-block: Field AEAD
    f_enc = FancyBboxPatch((95.0, 86.5), 24.0, 30.0, boxstyle="round,pad=0.1,rounding_size=0.4",
                           facecolor="#FFFBEB", edgecolor="#F59E0B", lw=0.8, zorder=3)
    ax.add_patch(f_enc)
    ax.text(107.0, 114.5, "Granular AES-256-GCM", ha="center", fontsize=6.5, weight="bold", color="#78350F", zorder=4)
    ax.text(107.0, 111.5, "Per-Field Encryption:", ha="center", fontsize=6.0, color="#92400E", zorder=4)
    ax.text(107.0, 105.5, r"$(c_i, \nu_i, \tau_i) \leftarrow$", ha="center", fontsize=6.5, color="#78350F", zorder=4)
    ax.text(107.0, 101.5, r"$\mathrm{Enc}_{K_{field}}(V_i, AAD)$", ha="center", fontsize=6.5, weight="bold", color="#B45309", zorder=4)
    ax.text(107.0, 95.0, "12-Byte Random Nonce\n16-Byte GHASH Tag\nPayload Protected", ha="center", fontsize=5.8, color="#78350F", zorder=4)
    ax.text(107.0, 88.5, r"Outputs: $\{c_1, c_2, \dots, c_m\}$", ha="center", fontsize=6.2, weight="bold", color="#78350F", zorder=4)

    # Right sub-block: ML-KEM Envelope
    k_enc = FancyBboxPatch((120.0, 86.5), 23.5, 30.0, boxstyle="round,pad=0.1,rounding_size=0.4",
                           facecolor="#FFFBEB", edgecolor="#F59E0B", lw=0.8, zorder=3)
    ax.add_patch(k_enc)
    ax.text(131.75, 114.5, "ML-KEM-768 Wrapping", ha="center", fontsize=6.5, weight="bold", color="#78350F", zorder=4)
    ax.text(131.75, 111.5, "NIST FIPS 203 Encaps:", ha="center", fontsize=6.0, color="#92400E", zorder=4)
    ax.text(131.75, 106.0, r"$\mathrm{Encaps}(pk_{doc}) \rightarrow$", ha="center", fontsize=6.5, color="#78350F", zorder=4)
    ax.text(131.75, 102.2, r"$(c_{kem},\ ss)$", ha="center", fontsize=6.5, weight="bold", color="#B45309", zorder=4)
    ax.text(131.75, 96.0, r"$KEK \leftarrow \mathrm{HKDF}(ss)$", ha="center", fontsize=6.2, color="#78350F", zorder=4)
    ax.text(131.75, 92.0, r"$c_{session\_key} \leftarrow \mathrm{Enc}_{KEK}(K_{session})$", ha="center", fontsize=6.0, weight="bold", color="#92400E", zorder=4)
    ax.text(131.75, 88.5, r"$|c_{kem}| = 1088\ \mathrm{B},\ |c_{key}| = 32\ \mathrm{B}$", ha="center", fontsize=5.8, color="#78350F", zorder=4)

    # Step 1.4: Aggregated Record Ciphertext Tuple
    draw_rounded_card(ax, 149.0, 84.0, 53.0, 38.0, "#ECFDF5", "#059669", lw=1.2)
    draw_badge(ax, 175.5, 119.0, "STEP 4: CIPHERTEXT TUPLE", bg_color="#047857", text_color="#FFFFFF", font_size=6.8)
    ax.text(175.5, 114.5, "Aggregated Record Payload for Database:", ha="center", fontsize=6.6, weight="bold", color="#064E3B", zorder=3)
    ax.text(175.5, 110.5, r"$\mathcal{C} = \left(\mathrm{PID},\ c_{kem},\ c_{session\_key},\ \nu_{key},\ \{(c_i, \nu_i, \tau_i)\}_{i=1}^m \right)$",
            ha="center", fontsize=6.6, weight="bold", color="#065F46", zorder=3)

    # Tuple Pills
    t_pills = [
        ("PID", "UUID", "#FED7AA"),
        ("c_kem", "1088 B", "#E9D5FF"),
        ("c_session_key", "32 B", "#FEF08A"),
        ("{c_field, tau}", "Granular", "#BBF7D0"),
    ]
    for p_idx, (p_name, p_size, p_col) in enumerate(t_pills):
        px = 151.0 + p_idx * 12.0
        p_card = FancyBboxPatch((px, 98.0), 11.0, 9.5, boxstyle="round,pad=0.08,rounding_size=0.3",
                                facecolor=p_col, edgecolor="#059669", lw=0.6, zorder=3)
        ax.add_patch(p_card)
        ax.text(px + 5.5, 104.5, p_name, ha="center", fontsize=6.4, weight="bold", color="#1E293B", zorder=4)
        ax.text(px + 5.5, 100.5, p_size, ha="center", fontsize=5.8, color="#334155", zorder=4)

    ax.text(175.5, 93.0, "Zero Plaintext Exposure  •  Lattice Security Guaranteed",
            ha="center", fontsize=6.2, weight="bold", color="#065F46", zorder=3)
    ax.text(175.5, 87.5, "Ready for Cloud Ingestion without trusting Mediator",
            ha="center", fontsize=5.8, style="italic", color="#047857", zorder=3)

    # Ingress internal connecting arrows
    draw_arrow(ax, (43.0, 103.0), (47.0, 103.0), color="#2563EB", lw=1.3)
    draw_arrow(ax, (89.0, 103.0), (93.0, 103.0), color="#7C3AED", lw=1.3)
    draw_arrow(ax, (145.0, 103.0), (149.0, 103.0), color="#D97706", lw=1.3)

    # =========================================================================
    # 2. MIDDLE ZONE: CLOUD MEDIATOR & TAMPER-EVIDENT REPOSITORY (y = 52.0 to 76.0)
    # =========================================================================
    mid_zone = FancyBboxPatch((4.0, 52.0), 202.0, 25.0,
                             boxstyle="round,pad=0.2,rounding_size=1.0",
                             facecolor="#F0FDF4", edgecolor="#10B981", lw=1.4, zorder=1)
    ax.add_patch(mid_zone)

    # Central Header
    m_hdr = FancyBboxPatch((70.0, 73.5), 70.0, 4.5,
                           boxstyle="round,pad=0.1,rounding_size=0.5",
                           facecolor="#065F46", edgecolor="none", zorder=2)
    ax.add_patch(m_hdr)
    ax.text(105.0, 75.75, "CENTRAL CLOUD MEDIATOR (HONEST-BUT-CURIOUS POSTGRESQL & AUDIT ENGINE)",
            ha="center", va="center", fontsize=7.5, weight="bold", color="#FFFFFF", zorder=3)

    # Box 2.1: PostgreSQL Storage Core
    draw_rounded_card(ax, 7.0, 54.5, 58.0, 18.0, "#FFFFFF", "#10B981", lw=1.0)
    ax.text(36.0, 69.5, "1. Zero-Knowledge Relational Storage (PostgreSQL)", ha="center", fontsize=7.2, weight="bold", color="#064E3B", zorder=3)
    ax.text(36.0, 65.5, r"Stores tuple: $\mathcal{C} = (\mathrm{PID}, c_{kem}, c_{session\_key}, \{c_{field}\})$", ha="center", fontsize=6.6, color="#047857", zorder=3)
    ax.text(36.0, 61.5, "Threat Model: Cloud provider is Honest-but-Curious", ha="center", fontsize=6.2, style="italic", color="#065F46", zorder=3)
    ax.text(36.0, 57.5, "Server CANNOT read clinical fields: Zero private key possession", ha="center", fontsize=6.2, weight="bold", color="#065F46", zorder=3)

    # Box 2.2: Zero-Payload Cryptographic Delegation Engine (O(1))
    draw_rounded_card(ax, 69.0, 54.5, 68.0, 18.0, "#ECFDF5", "#059669", lw=1.2)
    draw_badge(ax, 103.0, 70.5, "KEY DELEGATION ENGINE", bg_color="#047857", text_color="#FFFFFF", font_size=6.6)
    ax.text(103.0, 66.5, "O(1) Zero-Payload Access Delegation (Doctor A -> Doctor B)",
            ha="center", fontsize=7.0, weight="bold", color="#064E3B", zorder=3)
    ax.text(103.0, 62.5, r"• Re-encapsulate ONLY 32-Byte Envelope: $\mathrm{Encaps}(pk_{docB}) \longrightarrow (c_{kem}',\ c_{session\_key}')$",
            ha="center", fontsize=6.4, color="#065F46", zorder=3)
    ax.text(103.0, 58.8, "• Clinical Payload {c_field} 100% UNTOUCHED on disk! (No lattice blowup)",
            ha="center", fontsize=6.3, weight="bold", color="#047857", zorder=3)
    ax.text(103.0, 55.5, "Delegation Latency: 1.35 ms  |  Bandwidth Overhead: 0 Bytes Data Re-encryption",
            ha="center", fontsize=5.8, style="italic", color="#065F46", zorder=3)

    # Box 2.3: Intra-Database Cryptographic Hash Chain Audit
    draw_rounded_card(ax, 141.0, 54.5, 61.0, 18.0, "#FFFFFF", "#10B981", lw=1.0)
    ax.text(171.5, 69.5, "3. Tamper-Evident SHA-256 Hash Chaining", ha="center", fontsize=7.2, weight="bold", color="#064E3B", zorder=3)
    ax.text(171.5, 65.5, r"$\mathcal{H}_t = \mathrm{SHA\text{-}256}(\mathcal{H}_{t-1} \parallel T_t \parallel \mathrm{UID}_t \parallel \mathrm{Action}_t \parallel \mathrm{Res}_t)$",
            ha="center", fontsize=6.4, weight="bold", color="#047857", zorder=3)
    ax.text(171.5, 61.5, "Detects any unauthorized DB edit, insertion or back-dating", ha="center", fontsize=6.2, color="#065F46", zorder=3)
    ax.text(171.5, 57.5, "Audit Verification: 1.45 ms (15,700× Faster than Ethereum Blockchain)", ha="center", fontsize=6.0, weight="bold", color="#047857", zorder=3)

    # Big Arrow from Ingress (Top) down to Database (Middle)
    draw_arrow(ax, (175.5, 84.0), (175.5, 76.5), color="#059669", lw=1.8)
    ax.text(182.0, 80.0, "DB Ingestion\n& Hash Chain", ha="left", va="center", fontsize=6.2, weight="bold", color="#059669", zorder=7)

    # =========================================================================
    # 3. BOTTOM LANE: DATA EGRESS PIPELINE (y = 5.0 to 48.0)
    # =========================================================================
    lane2 = FancyBboxPatch((4.0, 5.0), 202.0, 44.0,
                           boxstyle="round,pad=0.2,rounding_size=1.0",
                           facecolor="#FFFBEB", edgecolor="#F59E0B", lw=1.3, linestyle="--", zorder=1)
    ax.add_patch(lane2)

    # Lane 2 Header Ribbon
    l2_hdr = FancyBboxPatch((5.5, 45.0), 75.0, 5.0,
                            boxstyle="round,pad=0.1,rounding_size=0.5",
                            facecolor="#B45309", edgecolor="none", zorder=2)
    ax.add_patch(l2_hdr)
    ax.text(43.0, 47.5, "PATH B: DATA EGRESS PIPELINE (ACCESS REQUEST & IN-MEMORY DECRYPTION)",
            ha="center", va="center", fontsize=7.8, weight="bold", color="#FFFFFF", zorder=3)

    # Big Arrow from Middle Delegation down to Egress
    draw_arrow(ax, (103.0, 54.5), (103.0, 48.5), color="#D97706", lw=1.8)
    ax.text(110.0, 51.5, "Access Granted: C'", ha="left", va="center", fontsize=6.2, weight="bold", color="#D97706", zorder=7)

    # Step 3.1: Doctor B Client Request & Decapsulation
    draw_rounded_card(ax, 7.0, 7.5, 44.0, 35.0, "#FEF3C7", "#D97706", lw=1.1)
    draw_badge(ax, 29.0, 39.5, "STEP 1: CLIENT DECAPSULATION", bg_color="#B45309", text_color="#FFFFFF", font_size=6.8)
    ax.text(9.0, 35.0, "Authorized Practitioner Device (Doctor B)", fontsize=7.0, weight="bold", color="#78350F", zorder=3)
    ax.text(9.0, 31.8, r"1. Local RAM holds $sk_{docB} \in \{0,1\}^{2400 \times 8}$", fontsize=6.5, color="#92400E", zorder=3)
    ax.text(9.0, 28.5, r"2. $\mathrm{ML\text{-}KEM.Decaps}(c_{kem}', sk_{docB}) \rightarrow ss'$", fontsize=6.5, weight="bold", color="#78350F", zorder=3)
    ax.text(9.0, 25.0, r"3. Derive $KEK' \leftarrow \mathrm{HKDF}(ss',\ \mathrm{'pqc\text{-}ehr\text{-}v1'})$", fontsize=6.3, color="#92400E", zorder=3)
    ax.text(9.0, 21.5, r"4. Recover $K_{session} \leftarrow \mathrm{Dec}_{KEK'}(c_{session\_key}')$", fontsize=6.5, weight="bold", color="#78350F", zorder=3)
    
    # Secure enclave box
    enc_box = FancyBboxPatch((9.0, 10.0), 40.0, 8.5, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor="#FFFBEB", edgecolor="#D97706", lw=0.7, zorder=3)
    ax.add_patch(enc_box)
    ax.text(29.0, 15.5, "Secure Isolated RAM Enclave", ha="center", fontsize=6.4, weight="bold", color="#78350F", zorder=4)
    ax.text(29.0, 12.0, "Zero Disk Plaintext Footprint  •  Side-Channel Protected", ha="center", fontsize=5.8, color="#92400E", zorder=4)

    # Step 3.2: Role-Based Fine-Grained Access Control (PQC-FLGC)
    draw_rounded_card(ax, 55.0, 7.5, 48.0, 35.0, "#FFF1F2", "#E11D48", lw=1.2)
    draw_badge(ax, 79.0, 39.5, "STEP 2: ROLE-BASED ACCESS GATING", bg_color="#BE123C", text_color="#FFFFFF", font_size=6.8)
    ax.text(79.0, 35.0, "Fine-Grained Role Permissions Check:", ha="center", fontsize=6.8, weight="bold", color="#881337", zorder=3)

    roles = [
        ("Attending Doctor", "Full Access (Diagnosis, Rx, Symptoms, Vitals, Notes)", "#FECDD3", "#9F1239"),
        ("Nurse / Triage", "Partial Access (Symptoms, Prescriptions, Vitals)", "#FFE4E6", "#BE123C"),
        ("Pharmacist", "Restricted Access (Prescription & Dosage Only)", "#FFE4E6", "#BE123C"),
        ("Billing / Insurance", "Zero Clinical Access (Metadata Only, Fields Masked)", "#FEE2E2", "#991B1B"),
    ]
    for r_idx, (r_name, r_desc, r_bg, r_text) in enumerate(roles):
        ry = 30.5 - r_idx * 5.2
        r_card = FancyBboxPatch((57.0, ry - 1.8), 44.0, 4.4, boxstyle="round,pad=0.08,rounding_size=0.3",
                                facecolor=r_bg, edgecolor=r_text, lw=0.6, zorder=3)
        ax.add_patch(r_card)
        ax.text(58.5, ry + 0.8, r_name, fontsize=6.3, weight="bold", color=r_text, zorder=4)
        ax.text(58.5, ry - 1.0, r_desc, fontsize=5.6, color="#4C0519", zorder=4)

    ax.text(79.0, 9.2, "Restricts sub-key derivation based strictly on verified role", ha="center", fontsize=5.8, style="italic", color="#881337", zorder=3)

    # Step 3.3: Authenticated Field Decryption & Tamper Check
    draw_rounded_card(ax, 107.0, 7.5, 46.0, 35.0, "#F3E8FF", "#7C3AED", lw=1.1)
    draw_badge(ax, 130.0, 39.5, "STEP 3: GHASH & AAD VERIFY", bg_color="#6D28D9", text_color="#FFFFFF", font_size=6.8)
    ax.text(109.0, 35.0, "Authenticated In-Memory Decryption:", fontsize=6.8, weight="bold", color="#4C1D95", zorder=3)
    ax.text(109.0, 31.5, r"1. Derive permitted $K_{field} \leftarrow \mathrm{HKDF}(K_{session},\ f_i)$", fontsize=6.3, color="#5B21B6", zorder=3)
    ax.text(109.0, 28.0, r"2. Reconstruct $AAD = \mathrm{'patient:'}\parallel\mathrm{PID}\parallel\mathrm{':field:'}\parallel f_i$", fontsize=6.1, color="#4C1D95", zorder=3)
    ax.text(109.0, 24.5, r"3. $\mathrm{AES\text{-}GCM\text{-}Dec}(c_i,\ \nu_i,\ K_{field},\ AAD)$", fontsize=6.4, weight="bold", color="#3B0764", zorder=3)
    
    # Tamper check badge
    t_box = FancyBboxPatch((109.0, 10.0), 42.0, 11.5, boxstyle="round,pad=0.1,rounding_size=0.4",
                           facecolor="#EDE9FE", edgecolor="#7C3AED", lw=0.7, zorder=3)
    ax.add_patch(t_box)
    ax.text(130.0, 18.5, "Integrity Check: GHASH Tag Verification", ha="center", fontsize=6.3, weight="bold", color="#4C1D95", zorder=4)
    ax.text(130.0, 15.0, r"Assert: $\tau_i == \mathrm{GHASH}(c_i,\ AAD)$", ha="center", fontsize=6.8, weight="bold", color="#2E1065", zorder=4)
    ax.text(130.0, 12.0, "Tag Mismatch $\\rightarrow$ Immediate Tamper Abort!", ha="center", fontsize=6.0, weight="bold", color="#991B1B", zorder=4)

    # Step 3.4: Final Plaintext Recovery (In-Memory Display)
    draw_rounded_card(ax, 157.0, 7.5, 45.0, 35.0, "#ECFDF5", "#059669", lw=1.2)
    draw_badge(ax, 179.5, 39.5, "STEP 4: PLAINTEXT VIEW", bg_color="#047857", text_color="#FFFFFF", font_size=6.8)
    ax.text(179.5, 35.0, "Decrypted In-Memory Clinical View:", ha="center", fontsize=6.8, weight="bold", color="#064E3B", zorder=3)

    out_views = [
        ("Diagnosis: Acute Coronary", "Doctor: Granted", "#4ADE80", "#14532D"),
        ("Rx: Nitroglycerin 0.4mg", "Doctor/Pharm: Granted", "#38BDF8", "#0C4A6E"),
        ("Symptoms: Chest Pain, SOB", "Doctor/Nurse: Granted", "#A78BFA", "#2E1065"),
        ("Notes: Follow-up required", "Doctor: Granted", "#F472B6", "#831843"),
        ("Billing/Financial Audit", "Clinical Masked [***]", "#FCA5A5", "#7F1D1D"),
    ]
    for o_idx, (o_title, o_role, o_fill, o_tcol) in enumerate(out_views):
        oy = 30.5 - o_idx * 4.3
        op = FancyBboxPatch((159.0, oy - 1.5), 41.0, 3.5, boxstyle="round,pad=0.06,rounding_size=0.3",
                            facecolor=o_fill, edgecolor=o_tcol, lw=0.6, zorder=3)
        ax.add_patch(op)
        ax.text(160.5, oy + 0.3, o_title, fontsize=6.0, weight="bold", color=o_tcol, zorder=4)
        ax.text(198.5, oy + 0.3, o_role, ha="right", fontsize=5.4, style="italic", color=o_tcol, zorder=4)

    ax.text(179.5, 9.2, "Strict Avalanche Criterion (SAC) = 50.00%  •  Quantum Secure",
            ha="center", fontsize=5.8, style="italic", color="#064E3B", zorder=3)

    # Egress internal connecting arrows
    draw_arrow(ax, (51.0, 25.0), (55.0, 25.0), color="#B45309", lw=1.3)
    draw_arrow(ax, (103.0, 25.0), (107.0, 25.0), color="#E11D48", lw=1.3)
    draw_arrow(ax, (153.0, 25.0), (157.0, 25.0), color="#7C3AED", lw=1.3)

    # Output paths
    png_path = os.path.join(OUTPUT_DIR, "fig_two_way_lifecycle_architecture.png")
    pdf_path = os.path.join(OUTPUT_DIR, "fig_two_way_lifecycle_architecture.pdf")

    plt.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.savefig(pdf_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close()

    print(f"[SUCCESS] Two-Way Lifecycle Architecture diagram generated:")
    print(f" -> PNG: {png_path}")
    print(f" -> PDF: {pdf_path}")

if __name__ == "__main__":
    generate_two_way_architecture()
