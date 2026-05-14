# MEO Satellite Visibility — Scheme 1

**Single MEO satellite, 2:1 resonant orbit, global optical clock comparison — optimized Ω₀=30°E for direct simultaneous common view.**

![Static Figure](figure_b_coverage.png)

## 24h Animation

![Animation](satellite_visibility_24h.mp4)

The satellite moves along its ground track over 24 hours (2 complete orbits, daily repeating). The visibility footprint (61.6° radius at ≥15° elevation) moves with the satellite. Stations highlight when visible; common-view links appear when station pairs are simultaneously in the footprint.

## Orbit Parameters (Optimized)

| Parameter | Value |
|---|---|
| Orbit type | 2:1 resonance (Earth 1 rev, SAT 2 revs = 24h daily repeat) |
| Period | 12 hours |
| Semi-major axis | 26,601 km (~20,230 km altitude) |
| Inclination | 60° (optimized) |
| **Ω₀ (RAAN)** | **30°E (grid-search optimized)** |
| Visibility footprint | 61.6° half-angle (15° min. elevation) |
| Doppler range | ±0.70–1.25 km/s |

## 4 Optimized Passes per 24h

| Pass | Time | Nadir | Direct Common View |
|---|---|---|---|
| Pass 1 (CN-EU) | +2.5h | 57°N, 55°E | Beijing, Shanghai, Hefei, Tokyo **+** PTB, Paris, NPL |
| Pass 2 (JP-US) | +13.5h | 37°N, 146°W | Tokyo **+** NIST, USNO |
| Pass 3 (EU-US) | +16.2h | 44°N, 67°W | PTB, Paris, NPL **+** NIST, USNO |
| Pass 4 (AU) | +7.2h | 31°S, 122°E | UWA Perth |

## 3 Direct Simultaneous Intercontinental Common Views

All three pairs achieve **direct simultaneous common view** (both stations in same footprint):

- **China–Europe** (Pass 1): 55–90 min — Beijing/Shanghai/Hefei/Tokyo + PTB/Paris/NPL
- **Japan–US** (Pass 2): 55–90 min — Tokyo + NIST/USNO (then China↔Japan trivially simultaneous, completing China↔US chain)
- **Europe–US** (Pass 3): 60–85 min — PTB/Paris/NPL + NIST/USNO

## Institution Stations

| Region | Stations |
|---|---|
| Asia-Pacific | Beijing, Shanghai, Hefei, Tokyo |
| Europe | PTB (Braunschweig), Paris, NPL (Teddington) |
| Americas | NIST (Boulder), USNO (Washington D.C.) |
| Australia | UWA (Perth) |

## Files

- `figure_b_coverage.py` — Static map script (China-centered Plate Carrée, Ω₀=30°E)
- `figure_b_coverage.png` — Static raster output (300 dpi)
- `figure_b_coverage.pdf` — Static vector output (300 dpi)
- `figure_b_animation.py` — Animation script (480 frames, 40s @ 12fps)
- `satellite_visibility_24h.mp4` — Animated satellite visibility over 24h
