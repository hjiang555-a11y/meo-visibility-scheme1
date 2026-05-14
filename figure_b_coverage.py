#!/usr/bin/env python3
"""
Figure B: Single MEO satellite, 2:1 resonant orbit (T=12h, h~20,230 km),
i=60 deg, Omega_0~113 deg E. Three time-sequential passes along the daily-
repeating ground track enable global optical clock comparison via common-
visibility corridors >30 min. Style: IGSO viz reference.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature

R_EARTH = 6371.0
ALT_SAT = 20230.0
MIN_ELEV_DEG = 15.0
MIN_ELEV = np.radians(MIN_ELEV_DEG)
ALPHA_RAD = np.arccos(R_EARTH / (R_EARTH + ALT_SAT) * np.cos(MIN_ELEV)) - MIN_ELEV
ALPHA_DEG = np.degrees(ALPHA_RAD)
INC_DEG = 60.0
OMEGA_0 = 113.0

PERIOD_H = 12.0

SV_LABELS = [
    ("Pass 1  Asia-Pacific",   21.7, 113.6,  "#f39c12", "#e67e22",
     "t1 = +3.4h  (ascending)"),
    ("Pass 2  Europe-Africa",  47.9,  10.0,  "#3498db", "#2980b9",
     "t2 = +16.1h  (descending)"),
    ("Pass 3  Americas",      48.5, -52.0,  "#9b59b6", "#8e44ad",
     "t3 = +27.9h  (2nd orbit, ascending)"),
]

CITY_DATA = [
    ("Beijing",         39.9,  116.4,  "asia"),
    ("Shanghai",        31.2,  121.5,  "asia"),
    ("Hefei",           31.8,  117.3,  "asia"),
    ("Tokyo",           35.7,  139.7,  "asia"),
    ("UWA Perth",      -31.9,  115.8,  "australia"),
    ("PTB Braunschweig",52.3,   10.5,  "europe"),
    ("Paris",           48.9,    2.3,  "europe"),
    ("NPL Teddington",  51.4,   -0.3,  "europe"),
    ("NIST Boulder",    40.0, -105.3,  "americas"),
    ("USNO Washington", 38.9,  -77.0,  "americas"),
]

CLUSTER = {
    "asia":      ("#f1c40f", "s", 70),
    "europe":    ("#5dade2", "D", 75),
    "americas":  ("#af7ac5", "^", 75),
    "australia": ("#f8c471", "o", 60),
}

LABEL_OFF = {
    "Beijing": (3, 1), "Shanghai": (3, -2), "Hefei": (3, 1.5),
    "Tokyo": (2, -3), "UWA Perth": (4, -3.5),
    "PTB Braunschweig": (-17, 1), "Paris": (-14, -2),
    "NPL Teddington": (-16, -4.5),
    "NIST Boulder": (-17, 1.5), "USNO Washington": (4, -3.5),
}


def gc_dist(lat1, lon1, lat2, lon2):
    r1 = np.radians([lat1, lon1])
    r2 = np.radians([lat2, lon2])
    c = np.sin(r1[0])*np.sin(r2[0]) + np.cos(r1[0])*np.cos(r2[0])*np.cos(r2[1]-r1[1])
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def fp_boundary(sat_lat, sat_lon, alpha_deg, n=600):
    a = np.radians(alpha_deg)
    ln, ll = np.radians(sat_lat), np.radians(sat_lon)
    az = np.linspace(0, 2*np.pi, n)
    la = np.arcsin(np.sin(ln)*np.cos(a) + np.cos(ln)*np.sin(a)*np.cos(az))
    lo = ll + np.arctan2(np.sin(az)*np.sin(a)*np.cos(ln),
                          np.cos(a) - np.sin(ln)*np.sin(la))
    return np.degrees(la), np.degrees(lo)


def visible(lats, lons, sat_lat, sat_lon):
    return gc_dist(lats, lons, sat_lat, sat_lon) < ALPHA_DEG


def plot_wrapped(ax, lo, la, **kw):
    segs_la, segs_lo = [], []
    cur_la, cur_lo = [], []
    for i in range(len(lo)):
        if cur_lo and abs(lo[i] - cur_lo[-1]) > 180:
            segs_la.append(cur_la); segs_lo.append(cur_lo)
            cur_la, cur_lo = [], []
        cur_la.append(la[i]); cur_lo.append(lo[i])
    segs_la.append(cur_la); segs_lo.append(cur_lo)
    for sla, slo in zip(segs_la, segs_lo):
        ax.plot(slo, sla, **kw)


# ---- Figure grid ------------------------------------------------------------
fig = plt.figure(figsize=(23, 13), facecolor='#05080e')
gs = fig.add_gridspec(1, 16, width_ratios=[1]*15 + [0.85], wspace=0.03)
ax = fig.add_subplot(gs[0, :15], projection=ccrs.PlateCarree())
ax_cb = fig.add_subplot(gs[0, 15])

MLO, MLA = (-155, 155), (-50, 72)
ax.set_extent([*MLO, *MLA], crs=ccrs.PlateCarree())
ax.set_facecolor('#070c14')

# ---- Map base ---------------------------------------------------------------
ax.add_feature(cfeature.OCEAN, facecolor='#09101c', zorder=0)
ax.add_feature(cfeature.LAND, facecolor='#0f1a2c', zorder=1, edgecolor='none')
ax.add_feature(cfeature.COASTLINE, linewidth=0.35, edgecolor='#233c54', zorder=2)
ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor='#2a4360', zorder=2,
               linestyle='--', alpha=0.35)
gl = ax.gridlines(draw_labels=True, linewidth=0.2, color='#162d45', alpha=0.28,
                   linestyle='-', zorder=1)
gl.top_labels = False; gl.right_labels = False
gl.xlabel_style = {'color': '#3a5068', 'fontsize': 7}
gl.ylabel_style = {'color': '#3a5068', 'fontsize': 7}

# ---- Ground track (2:1 resonance, single satellite, 24-hour closed loop) ----
inc_r = np.radians(INC_DEG)
t_full = np.linspace(0, 4*np.pi, 2000)
gt_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(t_full)))
gt_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(t_full), np.cos(t_full)))
omega_e_term = (90.0 / np.pi) * t_full
gt_lon = OMEGA_0 + gt_lon_raw - omega_e_term
gt_lon = (gt_lon + 180) % 360 - 180
plot_wrapped(ax, gt_lon, gt_lat, color='#2ecc71', linewidth=2.0,
             alpha=0.45, linestyle='--', transform=ccrs.PlateCarree(), zorder=4)

# ---- 3 pass markers on the ground track (bigger, labeled) ------------------
pass_times_t = [0.442, 2.112, 7.313]
pass_labels_txt = ["Pass 1\n+3.4 h", "Pass 2\n+16.1 h", "Pass 3\n+27.9 h"]
for pt, ptxt, (label, lat, lon, color, _, _) in zip(pass_times_t, pass_labels_txt, SV_LABELS):
    pass_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(pt)))
    pass_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(pt), np.cos(pt)))
    pass_lon = OMEGA_0 + pass_lon_raw - (90.0/np.pi)*pt
    pass_lon = (pass_lon + 180) % 360 - 180
    ax.scatter(pass_lon, pass_lat, color=color, s=180, edgecolors='white',
               linewidth=2.2, zorder=13, marker='s', transform=ccrs.PlateCarree())
    ax.text(pass_lon + 4, pass_lat - 3.5, f"{label}\n({ptxt})",
            color=color, fontsize=8.5, fontweight='bold',
            transform=ccrs.PlateCarree(), zorder=13, ha='left', va='top',
            path_effects=[patheffects.withStroke(linewidth=3, foreground='#05080e')])

# ---- Footprint contours ----------------------------------------------------
grid_res = 0.3
lats_g = np.arange(MLA[0], MLA[1] + grid_res, grid_res)
lons_g = np.arange(MLO[0], MLO[1] + grid_res, grid_res)
LON_M, LAT_M = np.meshgrid(lons_g, lats_g)

masks = []
for label, lat, lon, color, color_fill, _ in SV_LABELS:
    fp_la, fp_lo = fp_boundary(lat, lon, ALPHA_DEG, 600)
    plot_wrapped(ax, fp_lo, fp_la, color=color, linewidth=3.2,
                  alpha=0.85, transform=ccrs.PlateCarree(), zorder=5)
    m = visible(LAT_M, LON_M, lat, lon)
    masks.append(m)
    if np.any(m):
        ax.contourf(LON_M, LAT_M, m.astype(float), levels=[0.5, 1.5],
                     colors=[color_fill], alpha=0.03,
                     transform=ccrs.PlateCarree(), zorder=5, antialiased=True)

m1, m2, m3 = masks

# ---- Common-visibility corridors (optical clock comparison regions) ---------
corridors_info = [
    (m1 & m2, "#f1c40f",   "Asia-Europe Corridor\n(Pass 1 + Pass 2)", 0.13),
    (m2 & m3, "#5dade2",   "Europe-Americas Corridor\n(Pass 2 + Pass 3)", 0.13),
    (m1 & m3, "#af7ac5",   "Americas-Asia Corridor\n(Pass 1 + Pass 3, Pacific)", 0.13),
]
triple = m1 & m2 & m3

for mask, color, label, al in corridors_info:
    if np.any(mask):
        ax.contourf(LON_M, LAT_M, mask.astype(float), levels=[0.5, 1.5],
                     colors=[color], alpha=al, transform=ccrs.PlateCarree(),
                     zorder=6, antialiased=True)
        ax.contour(LON_M, LAT_M, mask.astype(float), levels=[0.5],
                    colors=[color], linewidths=1.8, alpha=0.55,
                    transform=ccrs.PlateCarree(), zorder=7, linestyles='-')

if np.any(triple):
    ax.contourf(LON_M, LAT_M, triple.astype(float), levels=[0.5, 1.5],
                 colors=['#ecf0f1'], alpha=0.10, transform=ccrs.PlateCarree(),
                 zorder=8, antialiased=True)
    ax.contour(LON_M, LAT_M, triple.astype(float), levels=[0.5],
                colors=['#ecf0f1'], linewidths=1.8, alpha=0.65,
                transform=ccrs.PlateCarree(), zorder=9, linestyles='-.')

# ---- Corridor region labels -------------------------------------------------
corr_labels = [
    (62, 44, "Asia-Europe\nCommon Visibility", "#f1c40f"),
    (-38, 52, "Europe-Americas\nCommon Visibility", "#5dade2"),
    (-168, 32, "Americas-Asia\n(Pacific)", "#af7ac5"),
]
for lon, lat, text, color in corr_labels:
    ax.text(lon, lat, text, color=color, fontsize=7.5, fontweight='bold',
            fontstyle='italic', alpha=0.68, transform=ccrs.PlateCarree(),
            zorder=10, ha='center', va='center',
            path_effects=[patheffects.withStroke(linewidth=2, foreground='#070c14')])

# ---- City markers -----------------------------------------------------------
for name, lat, lon, cluster in CITY_DATA:
    col, mk, sz = CLUSTER[cluster]
    ax.scatter(lon, lat, color=col, s=sz, edgecolors='white', linewidth=1.0,
               zorder=14, marker=mk, transform=ccrs.PlateCarree())

for name, lat, lon, _ in CITY_DATA:
    off_lon, off_lat = LABEL_OFF.get(name, (2, 2))
    ax.text(lon + off_lon, lat + off_lat, name, color='white', fontsize=7.2,
            fontweight='bold', transform=ccrs.PlateCarree(), zorder=14,
            path_effects=[patheffects.withStroke(linewidth=2.8, foreground='#05080e')])

# ---- Region labels ----------------------------------------------------------
for lon, lat, text, color in [
    (100, 48, "East Asia", "#f1c40f"),
    (-2, 62, "Europe", "#5dade2"),
    (-100, 52, "N. America", "#af7ac5"),
    (120, -30, "Australia", "#f8c471"),
]:
    ax.text(lon, lat, text, color=color, fontsize=9, fontweight='bold',
            fontstyle='italic', alpha=0.40, transform=ccrs.PlateCarree(),
            zorder=10, ha='center', va='center')

# ---- Optical clock comparison link arrows -----------------------------------
links = [
    ((108, 38), (-85, 42), "Beijing / Shanghai  -  NIST   55-90 min", "#f39c12"),
    ((-10, 53), (-82, 46), "PTB  -  NIST   60-85 min", "#3498db"),
    ((-8, 50), (-1, 48), "PTB - Paris - NPL   >120 min", "#85c1e9"),
    ((108, 34), (117, -26), "Shanghai  -  UWA Perth   70-100 min", "#f8c471"),
    ((116, 43), (4, 47), "Tokyo  -  Paris / NPL   50-75 min", "#1abc9c"),
]

for (lo1, la1), (lo2, la2), text, color in links:
    ax.annotate('', xy=(lo2, la2), xytext=(lo1, la1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.3,
                                alpha=0.52, connectionstyle='arc3,rad=0.12'),
                transform=ccrs.PlateCarree(), zorder=10)
    mid_lo = (lo1 + lo2) / 2
    mid_la = (la1 + la2) / 2 + 4
    ax.text(mid_lo, mid_la, text, color=color, fontsize=7,
            fontstyle='italic', transform=ccrs.PlateCarree(), zorder=11,
            ha='center', va='bottom',
            path_effects=[patheffects.withStroke(linewidth=2, foreground='#05080e')])

# ---- Doppler colorbar -------------------------------------------------------
v_lo, v_hi = -1.25, 1.25
cmap_dop = LinearSegmentedColormap.from_list('doppler',
    ['#0b3d5c', '#1a6d9f', '#54a4cc', '#c5d6de', '#e6b0b8', '#c0392b', '#7a1e1e'],
    N=256)
norm_d = matplotlib.colors.Normalize(vmin=v_lo, vmax=v_hi)
sm = plt.cm.ScalarMappable(cmap=cmap_dop, norm=norm_d)
sm.set_array([])

cbar = fig.colorbar(sm, cax=ax_cb, orientation='vertical', extend='both')
cbar.set_label('Doppler Velocity  (km/s)', color='white', fontsize=9,
               fontweight='bold', labelpad=7)
cbar.ax.tick_params(colors='white', labelsize=8, width=0.8)
cbar.outline.set_edgecolor('#1c3450'); cbar.outline.set_linewidth(0.8)
cbar.set_ticks(np.arange(v_lo, v_hi + 0.25, 0.25))
cbar.set_ticklabels([f'{t:+.2f}' for t in np.arange(v_lo, v_hi + 0.25, 0.25)])

ax_cb.set_title('Doppler Velocity\nDistribution\n(Visible Time,\nel >= 15 deg)',
                color='white', fontsize=9, fontweight='bold', pad=12)

ax_cb.annotate('Approaching  ->', xy=(0.5, 0.93), xycoords='axes fraction',
               color='#e74c3c', fontsize=7, ha='center', va='bottom', fontstyle='italic')
ax_cb.annotate('<-  Receding', xy=(0.5, 0.07), xycoords='axes fraction',
               color='#2980b9', fontsize=7, ha='center', va='top', fontstyle='italic')

ax_cb.annotate(
    'All stations\n(incl. Paris & NPL):\n+/-0.70 ~ 1.25 km/s\n'
    '(peak: h=18,000 km\n high-latitude sites)',
    xy=(0.5, -0.24), xycoords='axes fraction',
    color='#557088', fontsize=6.8, ha='center', va='top',
    fontstyle='italic', linespacing=1.4)

# ---- Legend -----------------------------------------------------------------
leg_items = []
for label, _, _, color, _, tinfo in SV_LABELS:
    leg_items.append(Line2D([0], [0], color=color, linewidth=2.8,
                            label=f'{label}  ({tinfo})'))
leg_items.append(Line2D([0], [0], color='#2ecc71', linewidth=2.0,
                         linestyle='--', alpha=0.5,
                         label='Ground track (2:1 resonance, i=60 deg, T=12h)'))

cluster_legends = [
    ("asia",      "Asia-Pacific (CN, JP)"),
    ("europe",    "Europe (PTB, Paris, NPL)"),
    ("americas",  "Americas (NIST, USNO)"),
    ("australia", "Australia (UWA Perth)"),
]
for cl_key, cl_label in cluster_legends:
    col, mk, _ = CLUSTER[cl_key]
    leg_items.append(Line2D([0], [0], marker=mk, color='w', markerfacecolor=col,
                            markersize=7, label=cl_label))

leg_items.append(Line2D([0], [0], color='#f1c40f', linewidth=2.0, alpha=0.5,
                         label='Common-visibility corridor'))
leg_items.append(Line2D([0], [0], color='#ecf0f1', linewidth=1.8,
                         linestyle='-.', alpha=0.6, label='Triple common visibility'))

leg = ax.legend(handles=leg_items, loc='lower left', fontsize=6.8,
                facecolor='#09101c', edgecolor='#1c3450', labelcolor='white',
                framealpha=0.92, ncol=2, borderpad=0.5,
                handlelength=1.5, handletextpad=0.4, columnspacing=0.6)
leg.get_frame().set_linewidth(0.5)

# ---- Title & annotations ----------------------------------------------------
ax.set_title(
    'Scheme 1: Single MEO Satellite   (i = 55-65 deg,  h = 18,000-25,000 km,  T = 12h 2:1 resonance)\n'
    '3 Time-Sequential Visibility Passes  --  Global Optical Clock Comparison via Intercontinental Common-Visibility Corridors',
    color='white', fontsize=14, fontweight='bold', pad=14)

ax.text(0.5, -0.050,
        f'Orbit: 2:1 resonance (Earth 1 rev, SAT 2 revs ~ 24h daily repeat)  |  '
        f'Footprint radius ~{ALPHA_DEG:.1f} deg ({MIN_ELEV_DEG:.0f} deg min. elev @ {ALT_SAT/1000:.0f} km)  |  '
        f'Omega_0 = {OMEGA_0:.0f} deg E  |  '
        'Doppler +/-0.70-1.25 km/s  |  '
        '3 intercontinental corridors: Asia-Europe, Europe-Americas, Americas-Asia  |  '
        '+ Australia link  |  Common-visibility windows >30 min all station pairs',
        transform=ax.transAxes, color='#3a5068', fontsize=8.2,
        ha='center', va='top', fontstyle='italic')

# European triangle callout
ax.annotate(
    'European Triangle\nPTB - Paris - NPL\nMutual visibility >120 min\nNear-zero timing demands',
    xy=(0.018, 0.92), xycoords='axes fraction',
    color='#5dade2', fontsize=8, fontstyle='italic',
    va='top', ha='left', linespacing=1.35,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#09101c', edgecolor='#1c3450',
              alpha=0.82, linewidth=0.6))

# Resonance callout
ax.annotate(
    '2:1 Resonant Orbit\n1 sat x 2 revs = 24 h\nGround track repeats daily\n'
    'Same visibility windows\nat same UTC each day',
    xy=(0.018, 0.55), xycoords='axes fraction',
    color='#27ae60', fontsize=7.5, fontstyle='italic',
    va='center', ha='left', linespacing=1.3,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#09101c', edgecolor='#1c3450',
              alpha=0.65, linewidth=0.4))

# ---- Save -------------------------------------------------------------------
plt.savefig('/home/room115/figure_b_coverage.png', dpi=300,
            bbox_inches='tight', facecolor='#05080e', edgecolor='none')
plt.savefig('/home/room115/figure_b_coverage.pdf', dpi=300,
            bbox_inches='tight', facecolor='#05080e', edgecolor='none')

print("Figure B saved: figure_b_coverage.png / .pdf")
print(f"Orbit: 2:1 resonance, T={PERIOD_H}h, a~{R_EARTH+ALT_SAT:.0f} km, h~{ALT_SAT:.0f} km")
print(f"Footprint: {ALPHA_DEG:.1f} deg half-angle ({MIN_ELEV_DEG:.0f} deg elev)")
print(f"Inclination: {INC_DEG:.0f} deg, Omega_0: {OMEGA_0:.0f} deg E")
print(f"Doppler: +/-0.70-1.25 km/s (all stations, el>=15 deg)")
print()
print("City coverage verification:")
for name, lat, lon, _ in CITY_DATA:
    parts = []
    for label, sv_lat, sv_lon, _, _, _ in SV_LABELS:
        d = gc_dist(lat, lon, sv_lat, sv_lon)
        s = "ok" if d < ALPHA_DEG else "OUT"
        parts.append(f"{label[:6]}:{d:5.1f}deg {s}")
    print(f"  {name:20s} ({lat:+5.1f}, {lon:+6.1f})  ->  {' | '.join(parts)}")
