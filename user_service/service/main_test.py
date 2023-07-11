from service.main import main

TEST_IP_ADDRESS = "127.0.0.1"
TEST_PORT = 8000
TEST_LOG_CONFIG = {"version": 1}


def test_main_calls_expected_functions(mocker):
    mock_load_config_file = mocker.patch(
        "service.main.load_config_file", return_value=TEST_LOG_CONFIG
    )
    mock_getenv = mocker.patch(
        "service.main.os.getenv", side_effect=[TEST_IP_ADDRESS, str(TEST_PORT)]
    )
    mock_run_server = mocker.patch("service.main.run_server")

    main()

    mock_load_config_file.assert_called_once()
    assert mock_getenv.call_count == 2
    mock_run_server.assert_called_once()
