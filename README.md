# MEO Satellite Visibility — Scheme 1

**Single MEO satellite, 2:1 resonant orbit, global optical clock comparison via common-visibility corridors.**

## 24h Animation

![Animation](satellite_visibility_24h.mp4)

The satellite moves along its ground track over 24 hours (2 complete orbits). The visibility footprint (circular region, 61.6° radius at ≥15° elevation) moves with the satellite. Ground stations light up when they enter the footprint. Common-view links appear when two stations are simultaneously visible — enabling optical clock comparison between them.

## Orbit Parameters

| Parameter | Value |
|---|---|
| Orbit type | 2:1 resonance (Earth 1 rev, SAT 2 revs = 24h daily repeat) |
| Period | 12 hours |
| Semi-major axis | 26,601 km (~20,230 km altitude) |
| Inclination | 60° (optimized, range 55–65°) |
| Ω₀ (RAAN) | 113°E |
| Visibility footprint | 61.6° half-angle (15° min. elevation) |
| Doppler range | ±0.70–1.25 km/s |

## 2 Rounds (Orbits) per 24h

With the 2:1 resonance, the satellite completes exactly 2 orbits in 24 hours. Round 3 = Round 1 (repeats daily at same UTC).

| Round | Orbit | Key Coverage |
|---|---|---|
| Round 1 (0–12h) | Orbit 1 | Asia-Pacific (Pass 1, +3.4h), Europe (Pass 2, +16.1h) |
| Round 2 (12–24h) | Orbit 2 | Americas + Europe (Pass 3, +28.1h ≡ +4.1h next day) |

## 3 Intercontinental Common-Visibility Corridors

- **China–Europe** (Round 1, Pass 1 ∩ Pass 2): Central Asia — 55–90 min
- **China–US** (Round 1+2, Pass 1 ∩ Pass 3): Pacific — 55–90 min
- **Europe–US** (Round 1+2, Pass 2 ∩ Pass 3): North Atlantic — 60–85 min

## Institution Stations

| Region | Stations |
|---|---|
| Asia-Pacific | Beijing, Shanghai, Hefei, Tokyo |
| Europe | PTB (Braunschweig), Paris, NPL (Teddington) |
| Americas | NIST (Boulder), USNO (Washington D.C.) |
| Australia | UWA (Perth) |

## Key Link Windows

| Link | Window |
|---|---|
| Beijing/Shanghai ↔ NIST | 55–90 min |
| PTB ↔ NIST | 60–85 min |
| PTB–Paris–NPL (European triangle) | >120 min |
| Shanghai ↔ UWA Perth | 70–100 min |
| Tokyo ↔ Paris/NPL | 50–75 min |

## Files

- `figure_b_coverage.py` — Static map script (China-centered Plate Carrée)
- `figure_b_coverage.png` — Static raster output (300 dpi)
- `figure_b_coverage.pdf` — Static vector output (300 dpi)
- `figure_b_animation.py` — Animation script (480 frames, 40s @ 12fps)
- `satellite_visibility_24h.mp4` — Animated satellite visibility over 24h (6.1 MB)
