import pytest

from nycmesh_ospf_explorer.utils import (
    compute_nn_from_ip,
    compute_ip_from_nn,
    compute_nn_string_from_ip,
)


def test_convert_nn_to_ip():
    assert compute_ip_from_nn(2) == "10.69.0.2"
    assert compute_ip_from_nn(10) == "10.69.0.10"
    assert compute_ip_from_nn(14) == "10.69.0.14"
    assert compute_ip_from_nn(145) == "10.69.1.45"
    assert compute_ip_from_nn(531) == "10.69.5.31"
    assert compute_ip_from_nn(1455) == "10.69.14.55"
    assert compute_ip_from_nn(2397) == "10.69.23.97"


def test_convert_ip_to_nn():
    # First router
    assert compute_nn_from_ip("10.69.0.2") == 2
    assert compute_nn_from_ip("10.69.0.10") == 10
    assert compute_nn_from_ip("10.69.0.14") == 14
    assert compute_nn_from_ip("10.69.1.45") == 145
    assert compute_nn_from_ip("10.69.5.31") == 531
    assert compute_nn_from_ip("10.69.14.55") == 1455
    assert compute_nn_from_ip("10.69.23.97") == 2397

    # Second Router
    assert compute_nn_from_ip("10.69.0.102") == 2
    assert compute_nn_from_ip("10.69.0.110") == 10
    assert compute_nn_from_ip("10.69.0.114") == 14
    assert compute_nn_from_ip("10.69.1.145") == 145
    assert compute_nn_from_ip("10.69.5.131") == 531
    assert compute_nn_from_ip("10.69.14.155") == 1455
    assert compute_nn_from_ip("10.69.23.197") == 2397

    # Third Router  (where applicable)
    assert compute_nn_from_ip("10.69.0.202") == 2
    assert compute_nn_from_ip("10.69.0.210") == 10
    assert compute_nn_from_ip("10.69.0.214") == 14
    assert compute_nn_from_ip("10.69.1.245") == 145
    assert compute_nn_from_ip("10.69.5.231") == 531


def test_convert_ip_to_nn_string():
    # First router
    assert compute_nn_string_from_ip("10.69.0.2") == "2"
    assert compute_nn_string_from_ip("10.69.0.10") == "10"
    assert compute_nn_string_from_ip("10.69.0.14") == "14"
    assert compute_nn_string_from_ip("10.69.1.45") == "145"
    assert compute_nn_string_from_ip("10.69.5.31") == "531"
    assert compute_nn_string_from_ip("10.69.14.55") == "1455"
    assert compute_nn_string_from_ip("10.69.23.97") == "2397"

    # Second Router
    assert compute_nn_string_from_ip("10.69.0.102") == "2 (.1xx)"
    assert compute_nn_string_from_ip("10.69.0.110") == "10 (.1xx)"
    assert compute_nn_string_from_ip("10.69.0.114") == "14 (.1xx)"
    assert compute_nn_string_from_ip("10.69.1.145") == "145 (.1xx)"
    assert compute_nn_string_from_ip("10.69.5.131") == "531 (.1xx)"
    assert compute_nn_string_from_ip("10.69.14.155") == "1455 (.1xx)"
    assert compute_nn_string_from_ip("10.69.23.197") == "2397 (.1xx)"

    # Third Router  (where applicable)
    assert compute_nn_string_from_ip("10.69.0.202") == "2 (.2xx)"
    assert compute_nn_string_from_ip("10.69.0.210") == "10 (.2xx)"
    assert compute_nn_string_from_ip("10.69.0.214") == "14 (.2xx)"
    assert compute_nn_string_from_ip("10.69.1.245") == "145 (.2xx)"
    assert compute_nn_string_from_ip("10.69.5.231") == "531 (.2xx)"
