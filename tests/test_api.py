from unittest.mock import AsyncMock, Mock

import pytest

from neuromorphopy.api import NeuroMorphoClient


@pytest.fixture
def mock_response():
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json = Mock(return_value={})
    resp.text = "content"
    return resp


@pytest.fixture
def mock_session(mocker, mock_response):
    # Mock the AsyncClient class to return our mock session
    session = AsyncMock()
    # When session.get() is awaited, it returns mock_response
    session.get.return_value = mock_response

    mocker.patch("httpx.AsyncClient", return_value=session)
    return session


@pytest.mark.asyncio
async def test_get_search_details_no_filters(mock_session, mock_response):
    mock_response.json.return_value = {"page": {"totalElements": 100}}

    async with NeuroMorphoClient() as client:
        endpoint, total, q_str = await client._get_search_details({})

    assert endpoint.endswith("/neuron")
    assert total == 100
    assert q_str is None


@pytest.mark.asyncio
async def test_get_search_details_with_filters(mock_session, mock_response):
    mock_response.json.return_value = {"page": {"totalElements": 50}}
    query = {"species": ["mouse"], "_sort": {"field": "brain_region", "order": "asc"}}

    async with NeuroMorphoClient() as client:
        endpoint, _total, q_str = await client._get_search_details(query)

    assert endpoint.endswith("/neuron/select")
    assert "species:mouse" in q_str
    # Check that sort was passed in params, not logic here but in the call args
    mock_session.get.assert_called()
    call_kwargs = mock_session.get.call_args[1]
    assert "sort" in call_kwargs["params"]
    assert call_kwargs["params"]["sort"] == "brain_region,asc"


@pytest.mark.asyncio
async def test_search_neurons_pagination(mock_session, mock_response):
    # Setup mock to return different pages
    # Total 150 neurons, page size 100 -> 2 pages

    def side_effect(url, params=None):
        resp = Mock()
        resp.raise_for_status = Mock()

        # Check if this is the count request or page request
        # Count request uses size=1, page=0
        if params and params.get("size") == 1:
            resp.json = Mock(return_value={"page": {"totalElements": 150}})
        else:
            # Page request
            page_num = params.get("page", 0)
            # Return fake neurons
            neurons = [
                {"neuron_name": f"n{i}"} for i in range(page_num * 100, (page_num + 1) * 100)
            ]
            # Slice to 150 total (last page has 50)
            if page_num == 1:
                neurons = neurons[:50]

            resp.json = Mock(return_value={"_embedded": {"neuronResources": neurons}})
        return resp

    mock_session.get.side_effect = side_effect

    async with NeuroMorphoClient() as client:
        neurons = await client.search_neurons({"species": ["mouse"]}, show_progress=False)

    assert len(neurons) == 150
    assert neurons[0]["neuron_name"] == "n0"
    assert neurons[-1]["neuron_name"] == "n149"


@pytest.mark.asyncio
async def test_download_neurons_logic(mock_session, mocker, tmp_path):
    # Mock get_swc_url to return a dummy url
    mocker.patch.object(NeuroMorphoClient, "get_swc_url", return_value="http://swc.url")

    # Mock session get for the SWC content
    swc_resp = Mock()
    swc_resp.raise_for_status = Mock()
    swc_resp.text = "SWC CONTENT"
    mock_session.get.return_value = swc_resp

    neurons = [{"neuron_name": "n1"}, {"neuron_name": "n2"}]

    async with NeuroMorphoClient() as client:
        await client.download_neurons(neurons, tmp_path, show_progress=False)

    downloads = tmp_path / "downloads"
    assert (downloads / "n1.swc").exists()
    assert (downloads / "n2.swc").exists()
    assert (downloads / "n1.swc").read_text() == "SWC CONTENT"
