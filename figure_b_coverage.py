#!/usr/bin/env python3
"""
Figure B: Single MEO satellite, 2:1 resonant orbit (T=12h, h~20,230 km).
3 time-sequential passes — global optical clock comparison corridors.
Style: IGSO visualization reference.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter

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
    ("Pass 1  Asia-Pacific",   21.7, 113.6,  "#f39c12", "#e67e22", "+3.4h  asc"),
    ("Pass 2  Europe-Africa",  47.9,  10.0,  "#3498db", "#2980b9", "+16.1h  desc"),
    ("Pass 3  Americas",       48.5, -52.0,  "#9b59b6", "#8e44ad", "+28.1h  2nd asc"),
]

CITY_DATA = [
    ("Beijing",         39.9,  116.4,  "asia"),
    ("Shanghai",        31.2,  121.5,  "asia"),
    ("Hefei",           31.8,  117.3,  "asia"),
    ("Tokyo",           35.7,  139.7,  "asia"),
    ("UWA Perth",      -31.9,  115.8,  "australia"),
    ("PTB",             52.3,   10.5,  "europe"),
    ("Paris",           48.9,    2.3,  "europe"),
    ("NPL",             51.4,   -0.3,  "europe"),
    ("NIST",            40.0, -105.3,  "americas"),
    ("USNO",            38.9,  -77.0,  "americas"),
]

CLUSTER = {
    "asia":      ("#f1c40f", "s", 110),
    "europe":    ("#5dade2", "D", 110),
    "americas":  ("#af7ac5", "^", 110),
    "australia": ("#f8c471", "o", 90),
}

LABEL_OFF = {
    "Beijing": (3.5, 1.5), "Shanghai": (3.5, -3), "Hefei": (3.5, 2),
    "Tokyo": (2.5, -4), "UWA Perth": (5, -5),
    "PTB": (-12, -1), "Paris": (-9, -3.5), "NPL": (-10, -6),
    "NIST": (-10, 2.5), "USNO": (4, -4.5),
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


fig = plt.figure(figsize=(30, 17), facecolor='#05080e')
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

MLO, MLA = (-210, 210), (-50, 72)
ax.set_extent([*MLO, *MLA], crs=ccrs.PlateCarree())
ax.set_facecolor('#070c14')

ax.add_feature(cfeature.OCEAN, facecolor='#09101c', zorder=0)
ax.add_feature(cfeature.LAND, facecolor='#0f1a2c', zorder=1, edgecolor='none')
ax.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor='#233c54', zorder=2)
ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor='#2a4360', zorder=2,
               linestyle='--', alpha=0.30)
gl = ax.gridlines(draw_labels=True, linewidth=0.25, color='#162d45', alpha=0.25,
                   linestyle='-', zorder=1,
                   xformatter=LongitudeFormatter(), yformatter=LatitudeFormatter())
gl.top_labels = False; gl.right_labels = False
gl.xlabel_style = {'color': '#4a5f75', 'fontsize': 10}
gl.ylabel_style = {'color': '#4a5f75', 'fontsize': 10}

# Ground track
inc_r = np.radians(INC_DEG)
t_full = np.linspace(0, 4*np.pi, 2500)
gt_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(t_full)))
gt_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(t_full), np.cos(t_full)))
omega_e_term = (90.0 / np.pi) * t_full
gt_lon = OMEGA_0 + gt_lon_raw - omega_e_term
plot_wrapped(ax, gt_lon, gt_lat, color='#2ecc71', linewidth=2.2,
             alpha=0.40, linestyle='--', transform=ccrs.PlateCarree(), zorder=4)

# Pass markers
pass_times_t = [0.442, 2.112, 7.313]
pass_labels_txt = ["Pass 1  +3.4h\nAsia-Pacific", "Pass 2  +16.1h\nEurope-Africa",
                    "Pass 3  +28.1h\nAmericas"]
for pt, ptxt, (label, lat, lon, color, _, _) in zip(pass_times_t, pass_labels_txt, SV_LABELS):
    pass_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(pt)))
    pass_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(pt), np.cos(pt)))
    pass_lon = OMEGA_0 + pass_lon_raw - (90.0/np.pi)*pt
    ax.scatter(pass_lon, pass_lat, color=color, s=250, edgecolors='white',
               linewidth=2.5, zorder=13, marker='s', transform=ccrs.PlateCarree())
    ax.text(pass_lon + 5, pass_lat - 5, ptxt, color=color, fontsize=11,
            fontweight='bold', transform=ccrs.PlateCarree(), zorder=13,
            ha='left', va='top',
            path_effects=[patheffects.withStroke(linewidth=3.5, foreground='#05080e')])

# Footprints
grid_res = 0.3
lats_g = np.arange(MLA[0], MLA[1] + grid_res, grid_res)
lons_g = np.arange(MLO[0], MLO[1] + grid_res, grid_res)
LON_M, LAT_M = np.meshgrid(lons_g, lats_g)

masks = []
for label, lat, lon, color, color_fill, _ in SV_LABELS:
    fp_la, fp_lo = fp_boundary(lat, lon, ALPHA_DEG, 600)
    plot_wrapped(ax, fp_lo, fp_la, color=color, linewidth=3.8,
                  alpha=0.82, transform=ccrs.PlateCarree(), zorder=5)
    m = visible(LAT_M, LON_M, lat, lon)
    masks.append(m)
    if np.any(m):
        ax.contourf(LON_M, LAT_M, m.astype(float), levels=[0.5, 1.5],
                     colors=[color_fill], alpha=0.03,
                     transform=ccrs.PlateCarree(), zorder=5, antialiased=True)

m1, m2, m3 = masks

# Common-visibility corridors — PROMINENT
corridors_info = [
    (m1 & m2, "#f1c40f", 0.18, 3.0),
    (m2 & m3, "#5dade2", 0.18, 3.0),
    (m1 & m3, "#af7ac5", 0.18, 3.0),
]
triple = m1 & m2 & m3

for mask, color, al, lw in corridors_info:
    if np.any(mask):
        ax.contourf(LON_M, LAT_M, mask.astype(float), levels=[0.5, 1.5],
                     colors=[color], alpha=al, transform=ccrs.PlateCarree(),
                     zorder=6, antialiased=True)
        ax.contour(LON_M, LAT_M, mask.astype(float), levels=[0.5],
                    colors=[color], linewidths=lw, alpha=0.65,
                    transform=ccrs.PlateCarree(), zorder=7, linestyles='-')

if np.any(triple):
    ax.contourf(LON_M, LAT_M, triple.astype(float), levels=[0.5, 1.5],
                 colors=['#ecf0f1'], alpha=0.14, transform=ccrs.PlateCarree(),
                 zorder=8, antialiased=True)
    ax.contour(LON_M, LAT_M, triple.astype(float), levels=[0.5],
                colors=['#ecf0f1'], linewidths=2.5, alpha=0.70,
                transform=ccrs.PlateCarree(), zorder=9, linestyles='-.')

# Corridor labels — BOLD, with arrows
def corridor_arrow(ax, lon, lat, dlon, dlat, text, color):
    ax.annotate(text, xy=(lon + dlon, lat + dlat), xytext=(lon, lat),
                fontsize=10, fontweight='bold', fontstyle='italic',
                color=color, ha='center', va='center',
                transform=ccrs.PlateCarree(), zorder=11,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8, alpha=0.7,
                                connectionstyle='arc3,rad=0'),
                path_effects=[patheffects.withStroke(linewidth=3, foreground='#070c14')])

corridor_arrow(ax, 50, 48, 20, -5, "Asia-Europe\nCommon Visibility\n(Pass 1 + 2)", "#f1c40f")
corridor_arrow(ax, -45, 55, -20, -5, "Europe-Americas\nCommon Visibility\n(Pass 2 + 3)", "#5dade2")
corridor_arrow(ax, -178, 38, 0, -10, "Americas-Asia\n(Pacific)\n(Pass 1 + 3)", "#af7ac5")

# City markers
for name, lat, lon, cluster in CITY_DATA:
    col, mk, sz = CLUSTER[cluster]
    ax.scatter(lon, lat, color=col, s=sz, edgecolors='white', linewidth=1.2,
               zorder=14, marker=mk, transform=ccrs.PlateCarree())

for name, lat, lon, _ in CITY_DATA:
    off_lon, off_lat = LABEL_OFF.get(name, (2, 2))
    ax.text(lon + off_lon, lat + off_lat, name, color='white', fontsize=10,
            fontweight='bold', transform=ccrs.PlateCarree(), zorder=14,
            path_effects=[patheffects.withStroke(linewidth=3, foreground='#05080e')])

# Region labels
for lon, lat, text, color in [
    (100, 48, "East Asia", "#f1c40f"),
    (-2, 64, "Europe", "#5dade2"),
    (-100, 54, "N. America", "#af7ac5"),
    (120, -32, "Australia", "#f8c471"),
]:
    ax.text(lon, lat, text, color=color, fontsize=11, fontweight='bold',
            fontstyle='italic', alpha=0.38, transform=ccrs.PlateCarree(),
            zorder=10, ha='center', va='center')

# Link arrows
links = [
    ((108, 36), (-85, 42), "Beijing / SH  -  NIST  55-90 min", "#f39c12"),
    ((-12, 53), (-80, 47), "PTB  -  NIST  60-85 min", "#3498db"),
    ((-8, 49), (-1, 48), "PTB - Paris - NPL  >120 min", "#85c1e9"),
    ((108, 32), (117, -27), "Shanghai  -  UWA Perth  70-100 min", "#f8c471"),
    ((116, 44), (5, 47), "Tokyo  -  Paris / NPL  50-75 min", "#1abc9c"),
]

for (lo1, la1), (lo2, la2), text, color in links:
    ax.annotate('', xy=(lo2, la2), xytext=(lo1, la1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.6,
                                alpha=0.50, connectionstyle='arc3,rad=0.10'),
                transform=ccrs.PlateCarree(), zorder=10)
    mid_lo = (lo1 + lo2) / 2
    mid_la = (la1 + la2) / 2 + 5
    ax.text(mid_lo, mid_la, text, color=color, fontsize=9,
            fontstyle='italic', transform=ccrs.PlateCarree(), zorder=11,
            ha='center', va='bottom',
            path_effects=[patheffects.withStroke(linewidth=2.5, foreground='#05080e')])

# Info box — timing, Doppler, visibility conditions
info_text = (
    'Visibility & Timing\n'
    f'  Min. elevation: {MIN_ELEV_DEG:.0f} deg\n'
    f'  Footprint radius: ~{ALPHA_DEG:.0f} deg central angle\n'
    f'  Satellite motion: ~0.5 deg/min along track\n\n'
    'Key Common-Visibility Windows\n'
    '  Beijing/Shanghai - NIST:   55-90 min\n'
    '  PTB - NIST:                60-85 min\n'
    '  PTB - Paris - NPL:        >120 min\n'
    '  Tokyo - Paris/NPL:         50-75 min\n'
    '  Shanghai - UWA Perth:      70-100 min\n\n'
    'Doppler Velocity (el >= 15 deg)\n'
    '  All stations: +/-0.70 ~ 1.25 km/s\n'
    '  Peak at h = 18,000 km, high-latitude sites\n'
    '  (Includes Paris & NPL)\n\n'
    'Orbit\n'
    '  2:1 resonance (Earth:SAT)\n'
    '  T = 12h, daily repeating ground track\n'
    '  i = 55-65 deg, h = 18,000-25,000 km'
)
ax.annotate(info_text, xy=(0.985, 0.50), xycoords='axes fraction',
            color='#bdc3c7', fontsize=9, fontfamily='monospace',
            va='center', ha='right', linespacing=1.35,
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#09101c',
                      edgecolor='#1c3450', alpha=0.88, linewidth=0.8),
            zorder=20)

# Legend
leg_items = []
for label, _, _, color, _, tinfo in SV_LABELS:
    leg_items.append(Line2D([0], [0], color=color, linewidth=3.5,
                            label=f'{label}  ({tinfo})'))
leg_items.append(Line2D([0], [0], color='#2ecc71', linewidth=2.2,
                         linestyle='--', alpha=0.5,
                         label='Ground track (2:1 resonance, i=60 deg, T=12h)'))

cluster_legends = [
    ("asia",      "Asia-Pacific  (Beijing, Shanghai, Hefei, Tokyo)"),
    ("europe",    "Europe  (PTB Braunschweig, Paris, NPL Teddington)"),
    ("americas",  "Americas  (NIST Boulder, USNO Washington DC)"),
    ("australia", "Australia  (UWA Perth)"),
]
for cl_key, cl_label in cluster_legends:
    col, mk, _ = CLUSTER[cl_key]
    leg_items.append(Line2D([0], [0], marker=mk, color='w', markerfacecolor=col,
                            markersize=9, label=cl_label))

leg_items.append(Line2D([0], [0], color='#f1c40f', linewidth=2.5, alpha=0.6,
                         label='Common-visibility corridor (2-pass overlap)'))
leg_items.append(Line2D([0], [0], color='#ecf0f1', linewidth=2.5,
                         linestyle='-.', alpha=0.7,
                         label='Triple common visibility'))

leg = ax.legend(handles=leg_items, loc='lower left', fontsize=9,
                facecolor='#09101c', edgecolor='#1c3450', labelcolor='white',
                framealpha=0.92, ncol=2, borderpad=0.6,
                handlelength=1.8, handletextpad=0.5, columnspacing=0.8)
leg.get_frame().set_linewidth(0.5)

# Title
ax.set_title(
    'Scheme 1: Single MEO Satellite  —  Global Optical Clock Comparison via Common-Visibility Corridors',
    color='white', fontsize=18, fontweight='bold', pad=16)

ax.text(0.5, -0.045,
        '3 time-sequential passes on a single 24h-repeating ground track  '
        '|  Common-visibility windows >30 min for all station pairs  '
        '|  Doppler +/-0.70-1.25 km/s (el >= 15 deg)  '
        '|  Extended map [-210, 210] deg for contiguous Pacific corridor',
        transform=ax.transAxes, color='#3a5068', fontsize=10.5,
        ha='center', va='top', fontstyle='italic')

# European triangle callout
ax.annotate(
    'European Triangle\nPTB - Paris - NPL\nMutual visibility >120 min\n'
    'Near-zero timing demands\n(FR+DE+UK equal partnership)',
    xy=(0.016, 0.92), xycoords='axes fraction',
    color='#5dade2', fontsize=10, fontstyle='italic',
    va='top', ha='left', linespacing=1.3,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#09101c', edgecolor='#1c3450',
              alpha=0.84, linewidth=0.7))

# Save
plt.savefig('/home/room115/figure_b_coverage.png', dpi=300,
            bbox_inches='tight', facecolor='#05080e', edgecolor='none')
plt.savefig('/home/room115/figure_b_coverage.pdf', dpi=300,
            bbox_inches='tight', facecolor='#05080e', edgecolor='none')

print("Figure B saved.")
print(f"Orbit: 2:1 resonance, T={PERIOD_H}h, a~{R_EARTH+ALT_SAT:.0f} km, h~{ALT_SAT:.0f} km")
print(f"Footprint: {ALPHA_DEG:.1f} deg half-angle ({MIN_ELEV_DEG:.0f} deg elev)")
print(f"Inclination: {INC_DEG:.0f} deg, Omega_0: {OMEGA_0:.0f} deg E")
print()
for name, lat, lon, _ in CITY_DATA:
    parts = []
    for label, sv_lat, sv_lon, _, _, _ in SV_LABELS:
        d = gc_dist(lat, lon, sv_lat, sv_lon)
        s = "ok" if d < ALPHA_DEG else "OUT"
        parts.append(f"{label[:6]}:{d:5.1f}deg {s}")
    print(f"  {name:20s} ({lat:+5.1f}, {lon:+6.1f})  ->  {' | '.join(parts)}")
