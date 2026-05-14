#!/usr/bin/env python3
"""
MEO Satellite visibility animation — Scheme 1 (2:1 resonance, i=60 deg).
Shows satellite moving along ground track with live visibility footprint,
highlighting which stations are in common view during 24h (2 orbits).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.animation import FuncAnimation
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
OMEGA_0 = 30.0
CENTER_LON = 115.0
PERIOD_H = 12.0

SAT_COLOR = '#f39c12'
FP_COLOR = '#f39c12'
VIS_COLOR = '#2ecc71'
CV_COLOR = '#e74c3c'
GT_COLOR = '#27ae60'

CITIES = [
    ("BJ",  39.9,  116.4,  "asia"),
    ("SH",  31.2,  121.5,  "asia"),
    ("HF",  31.8,  117.3,  "asia"),
    ("TK",  35.7,  139.7,  "asia"),
    ("PRTH",-31.9, 115.8,  "australia"),
    ("PTB", 52.3,   10.5,  "europe"),
    ("PAR", 48.9,    2.3,  "europe"),
    ("NPL", 51.4,   -0.3,  "europe"),
    ("NIST",40.0, -105.3,  "americas"),
    ("USNO",38.9,  -77.0,  "americas"),
]

CLUSTER_COL = {
    "asia": "#f1c40f", "europe": "#5dade2",
    "americas": "#af7ac5", "australia": "#f8c471",
}

def gc_dist(lat1, lon1, lat2, lon2):
    r1, r2 = np.radians([lat1, lon1]), np.radians([lat2, lon2])
    c = np.sin(r1[0])*np.sin(r2[0]) + np.cos(r1[0])*np.cos(r2[0])*np.cos(r2[1]-r1[1])
    return np.degrees(np.arccos(np.clip(c, -1, 1)))

def fp_boundary(sat_lat, sat_lon, n=360):
    a = np.radians(ALPHA_DEG)
    ln, ll = np.radians(sat_lat), np.radians(sat_lon)
    az = np.linspace(0, 2*np.pi, n)
    la = np.arcsin(np.sin(ln)*np.cos(a) + np.cos(ln)*np.sin(a)*np.cos(az))
    lo = ll + np.arctan2(np.sin(az)*np.sin(a)*np.cos(ln),
                          np.cos(a) - np.sin(ln)*np.sin(la))
    return np.degrees(la), np.degrees(lo)

def sat_position(t_rad):
    inc_r = np.radians(INC_DEG)
    lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(t_rad)))
    lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(t_rad), np.cos(t_rad)))
    lon = OMEGA_0 + lon_raw - (90.0/np.pi)*t_rad
    return lat, lon

N_FRAMES = 480
FPS = 12
TOTAL_HOURS = 24.0
# A wrapped footprint can be split at both map seams; four artists cover all pieces.
MAX_FOOTPRINT_SEGMENTS = 4
t_frames = np.linspace(0, 4*np.pi, N_FRAMES)

sat_lats = np.zeros(N_FRAMES)
sat_lons = np.zeros(N_FRAMES)
for i, t in enumerate(t_frames):
    sat_lats[i], sat_lons[i] = sat_position(t)

station_visible = np.zeros((N_FRAMES, len(CITIES)), dtype=bool)
for i in range(N_FRAMES):
    for j, (_, lat, lon, _) in enumerate(CITIES):
        station_visible[i, j] = gc_dist(lat, lon, sat_lats[i], sat_lons[i]) < ALPHA_DEG

fig = plt.figure(figsize=(20, 11), facecolor='#020508')
proj = ccrs.PlateCarree(central_longitude=CENTER_LON)
ax = fig.add_subplot(111, projection=proj)
ax.set_extent([-180, 180, -50, 72], crs=proj)
ax.set_facecolor('#040810')

ax.add_feature(cfeature.OCEAN, facecolor='#060e1a', zorder=0)
ax.add_feature(cfeature.LAND, facecolor='#162d45', zorder=1, edgecolor='none')
ax.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor='#2c5070', zorder=2)
ax.add_feature(cfeature.BORDERS, linewidth=0.2, edgecolor='#325878', zorder=2,
               linestyle='--', alpha=0.25)

gl = ax.gridlines(draw_labels=True, linewidth=0.25, color='#1a3450', alpha=0.25,
                   linestyle='-', zorder=1,
                  xformatter=LongitudeFormatter(),
                  yformatter=LatitudeFormatter())
gl.top_labels = False; gl.right_labels = False
gl.xlabel_style = {'color': '#507090', 'fontsize': 10}
gl.ylabel_style = {'color': '#507090', 'fontsize': 10}

inc_r = np.radians(INC_DEG)
t_gt = np.linspace(0, 4*np.pi, 2000)
gt_lat = np.degrees(np.arcsin(np.sin(inc_r) * np.sin(t_gt)))
gt_lon_raw = np.degrees(np.arctan2(np.cos(inc_r)*np.sin(t_gt), np.cos(t_gt)))
gt_lon = OMEGA_0 + gt_lon_raw - (90.0/np.pi)*t_gt

def split_wrapped(lo, la):
    segs_la, segs_lo = [], []
    cur_la, cur_lo = [], []
    for i in range(len(lo)):
        if cur_lo and abs(lo[i] - cur_lo[-1]) > 180:
            segs_la.append(cur_la); segs_lo.append(cur_lo)
            cur_la, cur_lo = [], []
        cur_la.append(la[i]); cur_lo.append(lo[i])
    segs_la.append(cur_la); segs_lo.append(cur_lo)
    return segs_lo, segs_la

def plot_wrapped_static(ax, lo, la, **kw):
    segs_lo, segs_la = split_wrapped(lo, la)
    lines = []
    for sla, slo in zip(segs_la, segs_lo):
        l, = ax.plot(slo, sla, **kw)
        lines.append(l)
    return lines

plot_wrapped_static(ax, gt_lon, gt_lat, color=GT_COLOR, linewidth=1.8,
                     alpha=0.35, linestyle='--', transform=ccrs.PlateCarree(), zorder=4)

city_scatters = []
city_labels = []
label_offs = {
    "BJ": (4, 1.5), "SH": (4, -3), "HF": (4, 2),
    "TK": (2.5, -4), "PRTH": (5, -5),
    "PTB": (-9, -1), "PAR": (-7, -3.5), "NPL": (-8, -6),
    "NIST": (-8, 2), "USNO": (3, -4.5),
}
for name, lat, lon, cluster in CITIES:
    sc = ax.scatter([], [], color=CLUSTER_COL[cluster], s=80,
                     edgecolors='white', linewidth=1.5, zorder=14,
                     marker='s' if cluster == 'asia' else
                            'D' if cluster == 'europe' else
                            '^' if cluster == 'americas' else 'o',
                     transform=ccrs.PlateCarree())
    city_scatters.append(sc)
    off_lon, off_lat = label_offs.get(name, (2, 2))
    txt = ax.text(lon + off_lon, lat + off_lat, name,
                  color=CLUSTER_COL[cluster], fontsize=9, fontweight='bold',
                  alpha=0.55, transform=ccrs.PlateCarree(), zorder=14,
                  path_effects=[patheffects.withStroke(linewidth=2.5, foreground='#020508')])
    city_labels.append(txt)

round_labels = [
    (0.25, 0.08, "Round 1  (Orbit 1, 0-12h)\nAsia-Pacific + Europe", "#f1c40f"),
    (0.75, 0.08, "Round 2  (Orbit 2, 12-24h)\nAmericas + Europe", "#af7ac5"),
]
for x, y, text, col in round_labels:
    ax.text(x, y, text, color=col, fontsize=11, fontweight='bold',
            transform=ax.transAxes, ha='center', va='bottom', alpha=0.7,
            zorder=20)

sat_dot, = ax.plot([], [], color=SAT_COLOR, marker='s', markersize=16,
                    markeredgecolor='white', markeredgewidth=2.0, linestyle='None',
                    transform=ccrs.PlateCarree(), zorder=15)

fp_lines = [
    ax.plot([], [], color=FP_COLOR, linewidth=2.5, alpha=0.65,
            transform=ccrs.PlateCarree(), zorder=6)[0]
    for _ in range(MAX_FOOTPRINT_SEGMENTS)
]

time_text = ax.text(0.02, 0.96, '', transform=ax.transAxes,
                     color='white', fontsize=12, fontweight='bold',
                     fontfamily='monospace', zorder=20,
                     path_effects=[patheffects.withStroke(linewidth=3, foreground='#020508')])

vis_text = ax.text(0.02, 0.88, '', transform=ax.transAxes,
                    color=VIS_COLOR, fontsize=10, fontweight='bold',
                    fontfamily='monospace', zorder=20,
                    path_effects=[patheffects.withStroke(linewidth=3, foreground='#020508')])

cv_links = []
for _ in range(5):
    l, = ax.plot([], [], color=CV_COLOR, linewidth=1.2, alpha=0.6,
                  linestyle='-', transform=ccrs.PlateCarree(), zorder=11)
    cv_links.append(l)

title = ax.set_title(
    'Scheme 1: MEO Single-Satellite Visibility Animation  |  '
    'i=60 deg  |  h=18,000-25,000 km  |  T=12h  |  Omega_0=30 deg E (optimized)  |  '
    f'Footprint {ALPHA_DEG:.0f} deg (el>={MIN_ELEV_DEG:.0f} deg)  |  '
    'Direct CN-EU, JP-US, EU-US common view',
    color='white', fontsize=14, fontweight='bold', pad=10)

def update(frame):
    t = t_frames[frame]
    hour = (frame / N_FRAMES) * TOTAL_HOURS

    sat_lat, sat_lon = sat_lats[frame], sat_lons[frame]

    fp_la, fp_lo = fp_boundary(sat_lat, sat_lon, 360)

    segs_lo, segs_la = split_wrapped(fp_lo, fp_la)
    for i, line in enumerate(fp_lines):
        if i < len(segs_lo) and len(segs_lo[i]) > 0:
            line.set_data(segs_lo[i], segs_la[i])
            line.set_visible(True)
        else:
            line.set_data([], [])
            line.set_visible(False)

    sat_dot.set_data([sat_lon], [sat_lat])

    round_num = 1 if hour < 12 else 2
    hour_12 = hour % 12
    time_text.set_text(
        f'Time: {hour:5.1f}h UTC  |  Round {round_num}  '
        f'(Orbit {"1" if round_num==1 else "2"}, +{hour_12:.1f}h)  '
        f'SAT: {sat_lat:+5.1f}deg, {sat_lon:+6.1f}deg')

    vis_names = []
    for j, (name, _, _, _) in enumerate(CITIES):
        if station_visible[frame, j]:
            city_scatters[j].set_sizes([160])
            city_scatters[j].set_linewidth(2.5)
            city_labels[j].set_alpha(1.0)
            city_labels[j].set_fontsize(11)
            vis_names.append(name)
        else:
            city_scatters[j].set_sizes([80])
            city_scatters[j].set_linewidth(1.0)
            city_labels[j].set_alpha(0.35)
            city_labels[j].set_fontsize(8)

    n_vis = len(vis_names)
    if n_vis > 0:
        vis_text.set_text(f'Visible ({n_vis}): {" ".join(vis_names[:8])}')
    else:
        vis_text.set_text('Visible: (none)')

    pairs = []
    for j1 in range(len(CITIES)):
        for j2 in range(j1+1, len(CITIES)):
            if station_visible[frame, j1] and station_visible[frame, j2]:
                name1, lat1, lon1, _ = CITIES[j1]
                name2, lat2, lon2, _ = CITIES[j2]
                dist = gc_dist(lat1, lon1, lat2, lon2)
                if 5 < dist < 150:
                    pairs.append(((lon1, lat1), (lon2, lat2)))

    for i, l in enumerate(cv_links):
        if i < len(pairs):
            (lo1, la1), (lo2, la2) = pairs[i]
            l.set_data([lo1, lo2], [la1, la2])
            l.set_visible(True)
            l.set_alpha(0.5)
        else:
            l.set_visible(False)

    artists = [*fp_lines, sat_dot, time_text, vis_text]
    for sc in city_scatters:
        artists.append(sc)
    for txt in city_labels:
        artists.append(txt)
    for l in cv_links:
        artists.append(l)
    return artists

anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=1000/FPS,
                      blit=False, repeat=True)

anim.save('/home/room115/satellite_visibility_24h.mp4', writer='ffmpeg',
          fps=FPS, dpi=150, bitrate=3000,
          savefig_kwargs={'facecolor': '#020508'})

print(f"Animation saved: satellite_visibility_24h.mp4")
print(f"Frames: {N_FRAMES}, FPS: {FPS}, Duration: {N_FRAMES/FPS:.1f}s")
print(f"Coverage: 24h, 2 orbits, footprint {ALPHA_DEG:.1f} deg")
