# MEO Satellite Visibility — Scheme 1

**Single MEO satellite, 2:1 resonant orbit, global optical clock comparison via common-visibility corridors.**

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

## 3 Time-Sequential Passes (single ground track)

| Pass | Time | Nadir Position | Covered Stations |
|---|---|---|---|
| Pass 1 | t₁ = +3.4h | 21.7°N, 113.6°E | Beijing, Shanghai, Hefei, Tokyo, UWA Perth |
| Pass 2 | t₂ = +16.1h | 47.9°N, 10.0°E | PTB, Paris, NPL, USNO |
| Pass 3 | t₃ = +27.9h | 48.5°N, 52.0°W | NIST, USNO, PTB, Paris, NPL |

## Intercontinental Common-Visibility Corridors

- **Asia–Europe**: Pass 1 ∩ Pass 2
- **Europe–Americas**: Pass 2 ∩ Pass 3 (European triangle visible from both)
- **Americas–Asia**: Pass 1 ∩ Pass 3 (Pacific)

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

- `figure_b_coverage.py` — Python script (matplotlib + cartopy)
- `figure_b_coverage.png` — Raster output (300 dpi)
- `figure_b_coverage.pdf` — Vector output (300 dpi)
