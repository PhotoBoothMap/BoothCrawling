from dataclasses import dataclass
from typing import Optional


@dataclass
class BoothData:
    confirm_id: Optional[int]
    booth_name: Optional[str]
    brand_id: Optional[int]
    brand_name: Optional[str]
    address: Optional[str]
    address_disp: Optional[str]
    new_address: Optional[str]
    new_address_disp: Optional[str]
    homepage: Optional[str]
    pay_keywords: Optional[str]
    booth_type: Optional[str]
    x_coordinate: Optional[float]
    y_coordinate: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    tel: Optional[str]
    status: Optional[str]

