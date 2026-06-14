from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class RegionProfile:
    code: str
    name: str
    headquarters: str
    divisions: tuple[str, ...]
    terrain: str
    operating_condition: str
    climate_hazards: tuple[str, ...]
    speed_factor: float
    vibration_factor: float
    weather_factor: float
    maintenance_factor: float
    max_speed_bias: int
    rainfall_baseline_mm: float
    temperature_baseline_c: float
    visibility_baseline_m: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


REGION_PROFILES: dict[str, RegionProfile] = {
    "NR": RegionProfile(
        code="NR",
        name="Northern Railway",
        headquarters="New Delhi",
        divisions=("Delhi", "Ambala", "Firozpur", "Lucknow", "Moradabad"),
        terrain="dense junctions, fog-prone plains, high passenger density",
        operating_condition="winter fog, congestion, mixed-speed corridors",
        climate_hazards=("fog", "cold_wave", "heat"),
        speed_factor=0.98,
        vibration_factor=1.05,
        weather_factor=1.12,
        maintenance_factor=1.03,
        max_speed_bias=0,
        rainfall_baseline_mm=18,
        temperature_baseline_c=31,
        visibility_baseline_m=4200,
    ),
    "CR": RegionProfile(
        code="CR",
        name="Central Railway",
        headquarters="Mumbai CSMT",
        divisions=("Mumbai", "Bhusawal", "Nagpur", "Pune", "Solapur"),
        terrain="ghat sections, suburban density, heavy freight interfaces",
        operating_condition="steep gradients, curve wear, monsoon disruption",
        climate_hazards=("flood", "landslide", "heat"),
        speed_factor=0.95,
        vibration_factor=1.16,
        weather_factor=1.18,
        maintenance_factor=1.08,
        max_speed_bias=-5,
        rainfall_baseline_mm=34,
        temperature_baseline_c=32,
        visibility_baseline_m=5200,
    ),
    "WR": RegionProfile(
        code="WR",
        name="Western Railway",
        headquarters="Mumbai Churchgate",
        divisions=("Mumbai Central", "Vadodara", "Ahmedabad", "Ratlam", "Rajkot", "Bhavnagar"),
        terrain="coastal belts, desert approaches, high-speed trunk routes",
        operating_condition="salinity, heat, dust, long-distance express traffic",
        climate_hazards=("heat", "dust", "cyclone"),
        speed_factor=1.04,
        vibration_factor=1.02,
        weather_factor=1.07,
        maintenance_factor=1.02,
        max_speed_bias=10,
        rainfall_baseline_mm=22,
        temperature_baseline_c=35,
        visibility_baseline_m=6800,
    ),
    "ER": RegionProfile(
        code="ER",
        name="Eastern Railway",
        headquarters="Kolkata",
        divisions=("Howrah", "Sealdah", "Asansol", "Malda"),
        terrain="deltaic plains, bridges, dense suburban operations",
        operating_condition="waterlogging, bridge approaches, crowding",
        climate_hazards=("flood", "fog", "cyclone"),
        speed_factor=0.96,
        vibration_factor=1.09,
        weather_factor=1.20,
        maintenance_factor=1.07,
        max_speed_bias=-5,
        rainfall_baseline_mm=42,
        temperature_baseline_c=31,
        visibility_baseline_m=4700,
    ),
    "SR": RegionProfile(
        code="SR",
        name="Southern Railway",
        headquarters="Chennai",
        divisions=("Chennai", "Tiruchirappalli", "Madurai", "Salem", "Palakkad", "Thiruvananthapuram"),
        terrain="coastal sections, humid climate, hill approaches",
        operating_condition="humidity, coastal corrosion, monsoon bursts",
        climate_hazards=("flood", "cyclone", "heat"),
        speed_factor=0.98,
        vibration_factor=1.04,
        weather_factor=1.14,
        maintenance_factor=1.05,
        max_speed_bias=0,
        rainfall_baseline_mm=30,
        temperature_baseline_c=33,
        visibility_baseline_m=6200,
    ),
    "NFR": RegionProfile(
        code="NFR",
        name="Northeast Frontier Railway",
        headquarters="Maligaon",
        divisions=("Katihar", "Alipurduar", "Rangiya", "Lumding", "Tinsukia"),
        terrain="hills, forests, rivers, landslide-prone formations",
        operating_condition="washouts, landslides, tight curves, remote maintenance",
        climate_hazards=("flood", "landslide", "fog"),
        speed_factor=0.88,
        vibration_factor=1.22,
        weather_factor=1.30,
        maintenance_factor=1.14,
        max_speed_bias=-15,
        rainfall_baseline_mm=58,
        temperature_baseline_c=27,
        visibility_baseline_m=3600,
    ),
    "NWR": RegionProfile(
        code="NWR",
        name="North Western Railway",
        headquarters="Jaipur",
        divisions=("Jaipur", "Jodhpur", "Bikaner", "Ajmer"),
        terrain="desert, heat, sand ingress, long sparse routes",
        operating_condition="thermal stress, dust, sparse emergency access",
        climate_hazards=("heat", "dust"),
        speed_factor=1.02,
        vibration_factor=1.03,
        weather_factor=1.08,
        maintenance_factor=1.06,
        max_speed_bias=5,
        rainfall_baseline_mm=8,
        temperature_baseline_c=38,
        visibility_baseline_m=7200,
    ),
}

REGION_ALIASES = {
    "north": "NR",
    "northern": "NR",
    "northern railway": "NR",
    "central": "CR",
    "central railway": "CR",
    "west": "WR",
    "western": "WR",
    "western railway": "WR",
    "east": "ER",
    "eastern": "ER",
    "eastern railway": "ER",
    "south": "SR",
    "southern": "SR",
    "southern railway": "SR",
    "northeast": "NFR",
    "north east": "NFR",
    "northeast frontier": "NFR",
    "nfr": "NFR",
    "northwest": "NWR",
    "north west": "NWR",
    "north western": "NWR",
}


def normalize_region_code(region: Optional[str]) -> str:
    if not region:
        return "CR"
    key = region.strip()
    if not key:
        return "CR"
    upper = key.upper().replace(" ", "")
    if upper in REGION_PROFILES:
        return upper
    return REGION_ALIASES.get(key.strip().lower(), "CR")


def get_region_profile(region: Optional[str]) -> RegionProfile:
    return REGION_PROFILES[normalize_region_code(region)]


def list_region_profiles() -> list[dict[str, object]]:
    return [profile.to_dict() for profile in REGION_PROFILES.values()]
