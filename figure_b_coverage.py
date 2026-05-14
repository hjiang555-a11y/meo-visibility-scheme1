#!/usr/bin/env python3
"""
Figure B: China-centered MEO satellite visibility (Scheme 1).
2:1 resonant orbit (T=12h), single satellite, 3 intercontinental corridors.
All text enlarged. No annotation boxes. Satellite + 2-link inset.
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
CENTER_LON = 115.0

SV_LABELS = [
    ("Pass 1", 21.7, 113.6, "#f39c12", "#e67e22", "+3.4h"),
    ("Pass 2", 47.9,  10.0, "#3498db", "#2980b9", "+16.1h"),
    ("Pass 3", 48.5, -52.0, "#9b59b6", "#8e44ad", "+28.1h"),
]

CITY_DATA = [
    ("Beijing",  39.9,  116.4, "asia"),
    ("Shanghai", 31.2,  121.5, "asia"),
    ("Hefei",    31.8,  117.3, "asia"),
    ("Tokyo",    35.7,  139.7, "asia"),
    ("UWA Perth",-31.9, 115.8, "australia"),
    ("PTB",      52.3,   10.5, "europe"),
    ("Paris",    48.9,    2.3, "europe"),
    ("NPL",      51.4,   -0.3, "europe"),
    ("NIST",     40.0, -105.3, "americas"),
    ("USNO",     38.9,  -77.0, "americas"),
]

CLUSTER = {
    "asia":      ("#f1c40f", "s", 150),
    "europe":    ("#5dade2", "D", 150),
    "americas":  ("#af7ac5", "^", 150),
    "australia": ("#f8c471", "o", 120),
}

LABEL_OFF = {
    "Beijing": (5, 2), "Shanghai": (5, -4), "Hefei": (5, 3),
    "Tokyo": (3, -5), "UWA Perth": (7, -7),
    "PTB": (-15, -1.5), "Paris": (-12, -4.5), "NPL": (-13, -7.5),
    "NIST": (-13, 3), "USNO": (5, -5.5),
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


fig = plt.figure(figsize=(34, 20), facecolor='#020508')
proj = ccrs.PlateCarree(central_longitude=CENTER_LON)
ax = fig.add_subplot(111, projection=proj)
ax.set_extent([-180, 180, -50, 72], crs=proj)
ax.set_facecolor('#040810')

ax.add_feature(cfeature.OCEAN, facecolor='#050c18', zorder=0)
ax.add_feature(cfeature.LAND, facecolor='#152840', zorder=1, edgecolor='none')
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#2c5070', zorder=2)
ax.add_feature(cfeature.BORDERS, linewidth=0.25, edgecolor='#325878', zorder=2,
               linestyle='--', alpha=0.28)

gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='#1a3450', alpha=0.28,
                   linestyle='-', zorder=1,
                   xformatter=LongitudeFormatter(), yformatter=LatitudeFormatter())
gl.top_labels = False; gl.right_labels = False
gl.xlabel_style = {'color': '#507090', 'fontsize': 12}
gl.ylabel_style = {'color': '#507090', 'fontsize': 12}

inc_r = np.radians(INC_DEG)
t_full = np.linspace(0, 4*np.pi, 3000)
gt_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(t_full)))
gt_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(t_full), np.cos(t_full)))
omega_e_term = (90.0 / np.pi) * t_full
gt_lon = OMEGA_0 + gt_lon_raw - omega_e_term
plot_wrapped(ax, gt_lon, gt_lat, color='#2ecc71', linewidth=2.5,
             alpha=0.42, linestyle='--', transform=ccrs.PlateCarree(), zorder=4)

pass_times_t = [0.442, 2.112, 7.313]
pass_labels_txt = ["Pass 1  Asia-Pacific\n+3.4h", "Pass 2  Europe-Africa\n+16.1h",
                    "Pass 3  Americas\n+28.1h"]
for pt, ptxt, (label, lat, lon, color, _, _) in zip(pass_times_t, pass_labels_txt, SV_LABELS):
    pass_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(pt)))
    pass_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(pt), np.cos(pt)))
    pass_lon = OMEGA_0 + pass_lon_raw - (90.0/np.pi)*pt
    ax.scatter(pass_lon, pass_lat, color=color, s=300, edgecolors='white',
               linewidth=3, zorder=13, marker='s', transform=ccrs.PlateCarree())
    ax.text(pass_lon + 6, pass_lat - 5, ptxt, color=color, fontsize=14,
            fontweight='bold', transform=ccrs.PlateCarree(), zorder=13,
            ha='left', va='top',
            path_effects=[patheffects.withStroke(linewidth=4, foreground='#020508')])

grid_res = 0.3
lats_g = np.arange(-50, 72 + grid_res, grid_res)
lons_g = np.arange(-180, 180 + grid_res, grid_res)
LON_M, LAT_M = np.meshgrid(lons_g, lats_g)

masks = []
for label, lat, lon, color, color_fill, _ in SV_LABELS:
    fp_la, fp_lo = fp_boundary(lat, lon, ALPHA_DEG, 600)
    plot_wrapped(ax, fp_lo, fp_la, color=color, linewidth=4.5,
                  alpha=0.82, transform=ccrs.PlateCarree(), zorder=5)
    m = visible(LAT_M, LON_M, lat, lon)
    masks.append(m)
    if np.any(m):
        ax.contourf(LON_M, LAT_M, m.astype(float), levels=[0.5, 1.5],
                     colors=[color_fill], alpha=0.03,
                     transform=ccrs.PlateCarree(), zorder=5, antialiased=True)

m1, m2, m3 = masks
corridors_info = [
    (m1 & m2, "#f1c40f", 0.20, 3.5, "China-Europe\n(Pass 1+2)"),
    (m1 & m3, "#e74c3c", 0.22, 3.5, "China-US  (Pacific)\n(Pass 1+3)"),
    (m2 & m3, "#5dade2", 0.20, 3.5, "Europe-US\n(Pass 2+3)"),
]
triple = m1 & m2 & m3

for mask, color, al, lw, _ in corridors_info:
    if np.any(mask):
        ax.contourf(LON_M, LAT_M, mask.astype(float), levels=[0.5, 1.5],
                     colors=[color], alpha=al, transform=ccrs.PlateCarree(),
                     zorder=6, antialiased=True)
        ax.contour(LON_M, LAT_M, mask.astype(float), levels=[0.5],
                    colors=[color], linewidths=lw, alpha=0.65,
                    transform=ccrs.PlateCarree(), zorder=7, linestyles='-')

if np.any(triple):
    ax.contourf(LON_M, LAT_M, triple.astype(float), levels=[0.5, 1.5],
                 colors=['#ecf0f1'], alpha=0.16, transform=ccrs.PlateCarree(),
                 zorder=8, antialiased=True)
    ax.contour(LON_M, LAT_M, triple.astype(float), levels=[0.5],
                colors=['#ecf0f1'], linewidths=3.0, alpha=0.70,
                transform=ccrs.PlateCarree(), zorder=9, linestyles='-.')

corridor_labels = [
    (55, 48, "China-Europe\nSeq. Comparison\n(Pass 1+2, 55-90 min)", "#f1c40f"),
    (-155, 35, "China-US\nSeq. Comparison\n(Pass 1+3, 55-90 min)", "#e74c3c"),
    (-35, 58, "Europe-US\nSeq. Comparison\n(Pass 2+3, 60-85 min)", "#5dade2"),
]
for lon, lat, text, color in corridor_labels:
    ax.text(lon, lat, text, color=color, fontsize=13, fontweight='bold',
            fontstyle='italic', alpha=0.85, transform=ccrs.PlateCarree(),
            zorder=11, ha='center', va='center',
            path_effects=[patheffects.withStroke(linewidth=3.5, foreground='#040810')])

for name, lat, lon, cluster in CITY_DATA:
    col, mk, sz = CLUSTER[cluster]
    ax.scatter(lon, lat, color=col, s=sz, edgecolors='white', linewidth=1.5,
               zorder=14, marker=mk, transform=ccrs.PlateCarree())

for name, lat, lon, _ in CITY_DATA:
    off_lon, off_lat = LABEL_OFF.get(name, (2, 2))
    ax.text(lon + off_lon, lat + off_lat, name, color='white', fontsize=12,
            fontweight='bold', transform=ccrs.PlateCarree(), zorder=14,
            path_effects=[patheffects.withStroke(linewidth=3.5, foreground='#020508')])

for lon, lat, text, color in [
    (80, 48, "East Asia", "#f1c40f"),
    (-10, 65, "Europe", "#5dade2"),
    (-100, 55, "N. America", "#af7ac5"),
    (120, -32, "Australia", "#f8c471"),
]:
    ax.text(lon, lat, text, color=color, fontsize=13, fontweight='bold',
            fontstyle='italic', alpha=0.35, transform=ccrs.PlateCarree(),
            zorder=10, ha='center', va='center')

links = [
    ((105, 35), (-85, 43), "Beijing/SH  -  NIST  55-90 min", "#e74c3c"),
    ((-10, 53), (-78, 48), "PTB  -  NIST  60-85 min", "#3498db"),
    ((-6, 50), (-0.5, 49), "PTB - Paris - NPL  >120 min", "#85c1e9"),
    ((108, 30), (117, -28), "Shanghai  -  UWA Perth  70-100 min", "#f8c471"),
    ((115, 44), (7, 48), "Tokyo  -  Paris/NPL  50-75 min", "#1abc9c"),
]

for (lo1, la1), (lo2, la2), text, color in links:
    ax.annotate('', xy=(lo2, la2), xytext=(lo1, la1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8,
                                alpha=0.50, connectionstyle='arc3,rad=0.08'),
                transform=ccrs.PlateCarree(), zorder=10)
    mid_lo = (lo1 + lo2) / 2
    mid_la = (la1 + la2) / 2 + 5.5
    ax.text(mid_lo, mid_la, text, color=color, fontsize=10,
            fontstyle='italic', transform=ccrs.PlateCarree(), zorder=11,
            ha='center', va='bottom',
            path_effects=[patheffects.withStroke(linewidth=3, foreground='#020508')])

leg_items = []
for label, _, _, color, _, tinfo in SV_LABELS:
    leg_items.append(Line2D([0], [0], color=color, linewidth=4,
                            label=f'{label}  ({tinfo})'))
leg_items.append(Line2D([0], [0], color='#2ecc71', linewidth=2.5,
                         linestyle='--', alpha=0.5,
                         label='Ground track (2:1 resonance, T=12h)'))

cluster_legends = [
    ("asia",      "Asia-Pacific (Beijing, Shanghai, Hefei, Tokyo)"),
    ("europe",    "Europe (PTB, Paris, NPL)"),
    ("americas",  "Americas (NIST, USNO)"),
    ("australia", "Australia (UWA Perth)"),
]
for cl_key, cl_label in cluster_legends:
    col, mk, _ = CLUSTER[cl_key]
    leg_items.append(Line2D([0], [0], marker=mk, color='w', markerfacecolor=col,
                            markersize=11, label=cl_label))

leg_items.append(Line2D([0], [0], color='#e74c3c', linewidth=3, alpha=0.6,
                         label='China-US common vis. (Pass 1+3)'))
leg_items.append(Line2D([0], [0], color='#f1c40f', linewidth=3, alpha=0.6,
                         label='China-Europe common vis. (Pass 1+2)'))
leg_items.append(Line2D([0], [0], color='#5dade2', linewidth=3, alpha=0.6,
                         label='Europe-US common vis. (Pass 2+3)'))
leg_items.append(Line2D([0], [0], color='#ecf0f1', linewidth=3,
                         linestyle='-.', alpha=0.6, label='Triple common visibility'))

leg = ax.legend(handles=leg_items, loc='lower left', fontsize=11,
                facecolor='#050c18', edgecolor='#2c5070', labelcolor='white',
                framealpha=0.92, ncol=2, borderpad=0.6,
                handlelength=2.0, handletextpad=0.5, columnspacing=0.8)
leg.get_frame().set_linewidth(0.6)

ax.set_title(
    'Scheme 1: MEO Single-Satellite Global Optical Clock Comparison  |  '
    'i = 55-65 deg  |  h = 18,000-25,000 km  |  T = 12h  (2:1 resonance)  |  '
    'Footprint 61.6 deg (el >= 15 deg)  |  '
    'Doppler +/-0.70-1.25 km/s  |  '
    'Sequential comparison via satellite onboard clock',
    color='white', fontsize=20, fontweight='bold', pad=16)

ax.text(0.5, -0.04,
        'China-centered Plate Carree projection  |  Extended map for contiguous common-visibility corridors  '
        '|  Common-visibility windows >30 min for all station pairs',
        transform=ax.transAxes, color='#507090', fontsize=12,
        ha='center', va='top', fontstyle='italic')

inset_ax = fig.add_axes([0.80, 0.62, 0.16, 0.28], facecolor='#050c18')
inset_ax.set_xlim(-1.8, 1.8)
inset_ax.set_ylim(-0.3, 2.8)
inset_ax.set_aspect('equal')
inset_ax.axis('off')
for spine in inset_ax.spines.values():
    spine.set_edgecolor('#2c5070')
    spine.set_linewidth(1.0)
    spine.set_visible(True)

theta = np.linspace(np.pi, 2*np.pi, 100)
earth_x = 1.3 * np.cos(theta)
earth_y = 1.3 * np.sin(theta) + 0.3
inset_ax.fill(earth_x, earth_y, color='#152840', alpha=0.9, zorder=2)
inset_ax.plot(earth_x, earth_y, color='#2c5070', linewidth=1.0, zorder=3)

sat_x, sat_y = 0.0, 2.3
inset_ax.scatter([sat_x], [sat_y], color='#f1c40f', s=120, edgecolors='white',
                 linewidth=1.5, zorder=5, marker='s')
inset_ax.text(sat_x + 0.15, sat_y + 0.1, 'MEO SAT\n(h~20,000 km)',
              color='#f1c40f', fontsize=9, fontweight='bold', va='bottom')

for gx, label, col in [(-0.7, 'Station A\n(e.g. NIST)', '#af7ac5'),
                        (0.7, 'Station B\n(e.g. PTB)', '#5dade2')]:
    gy = earth_y[np.argmin(np.abs(earth_x - gx))]
    inset_ax.scatter([gx], [gy], color=col, s=50, edgecolors='white',
                     linewidth=1, zorder=5, marker='^')
    inset_ax.plot([sat_x, gx], [sat_y, gy], color=col, linewidth=1.5,
                  alpha=0.6, linestyle='--', zorder=4)
    inset_ax.text(gx, gy - 0.3, label, color=col, fontsize=8,
                  fontweight='bold', ha='center', va='top')

inset_ax.text(0, 0.6, 'Common-view\nClock Comparison',
              color='white', fontsize=9, fontweight='bold',
              ha='center', va='center',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='#050c18',
                        edgecolor='#2c5070', alpha=0.8, linewidth=0.6))

plt.savefig('/home/room115/figure_b_coverage.png', dpi=300,
            bbox_inches='tight', facecolor='#020508', edgecolor='none')
plt.savefig('/home/room115/figure_b_coverage.pdf', dpi=300,
            bbox_inches='tight', facecolor='#020508', edgecolor='none')

print("Figure B saved: figure_b_coverage.png / .pdf")
print(f"Orbit: 2:1 resonance, T=12h, a~{R_EARTH+ALT_SAT:.0f} km, h~{ALT_SAT:.0f} km")
print(f"Footprint: {ALPHA_DEG:.1f} deg half-angle ({MIN_ELEV_DEG:.0f} deg elev)")
print(f"Inclination: {INC_DEG:.0f} deg, Omega_0: {OMEGA_0:.0f} deg E, Center lon: {CENTER_LON:.0f} deg E")
print()
for name, lat, lon, _ in CITY_DATA:
    parts = []
    for label, sv_lat, sv_lon, _, _, _ in SV_LABELS:
        d = gc_dist(lat, lon, sv_lat, sv_lon)
        s = "ok" if d < ALPHA_DEG else "OUT"
        parts.append(f"{label}:{d:5.1f}deg {s}")
    print(f"  {name:12s} ({lat:+5.1f}, {lon:+6.1f})  ->  {' | '.join(parts)}")
