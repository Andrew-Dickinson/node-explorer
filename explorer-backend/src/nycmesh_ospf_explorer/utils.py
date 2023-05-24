def compute_ip_from_nn(nn: int) -> str:
    return f"10.69.{nn // 100}.{nn % 100}"


def compute_nn_from_ip(ip: str) -> int:
    if not ip.startswith("10.69."):
        raise ValueError(f"Invalid IP for NN conversion: {ip}")

    components = ip.split(".")

    third_octet = int(components[2])
    fourth_octet = int(components[3])

    while fourth_octet > 100:
        fourth_octet -= 100

    if third_octet > 100:
        raise ValueError(f"Invalid IP for NN conversion: {ip}")

    return 100 * third_octet + fourth_octet


def compute_nn_string_from_ip(ip: str) -> str:
    if not ip.startswith("10.69."):
        raise ValueError(f"Invalid IP for NN conversion: {ip}")

    components = ip.split(".")

    third_octet = int(components[2])
    fourth_octet = int(components[3])

    router_idx = fourth_octet // 100

    while fourth_octet >= 100:
        fourth_octet -= 100

    if third_octet > 100:
        raise ValueError(f"Invalid IP for NN conversion: {ip}")

    suffix = ""
    if router_idx > 0:
        suffix = f" (.{router_idx}xx)"

    return str(100 * third_octet + fourth_octet) + suffix
