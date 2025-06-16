import requests
import os


def get_coordinates_from_kakao(address: str):
    headers = {
        "Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}",
    }
    params = {
        "query": address
    }
    response = requests.get("https://dapi.kakao.com/v2/local/search/address.json", headers=headers, params=params)
    result = response.json()

    if result.get("documents"):
        first = result["documents"][0]
        return float(first["y"]), float(first["x"])  # latitude, longitude
    else:
        return None, None


def get_korean_road_address(latitude: float, longitude: float) -> str | None:
    headers = {
        "Authorization": f"KakaoAK {os.getenv('KAKAO_API_KEY')}"
    }
    params = {
        "x": str(longitude),
        "y": str(latitude),
        "input_coord": "WGS84"
    }
    response = requests.get("https://dapi.kakao.com/v2/local/geo/coord2address.json", headers=headers, params=params)
    data = response.json()

    if "documents" in data and len(data["documents"]) > 0:
        doc = data["documents"][0]
        road_address = doc.get("road_address")
        if road_address:
            return road_address.get("address_name")  # This is the 도로명 주소
        # Fallback to jibun address if no road address is found
        address = doc.get("address")
        if address:
            return address.get("address_name")
    return None