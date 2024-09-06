import pytest
from unittest.mock import MagicMock, patch
import bot  # Adjust import based on your project structure

# import os
# print(os.getcwd())

@pytest.fixture
def mock_channel():
    return MagicMock()

@pytest.fixture
def mock_ctx(mock_channel):
    mock_ctx = MagicMock()
    mock_ctx.channel = mock_channel
    return mock_ctx

@patch('discord.ext.commands.Bot.get_channel')
async def test_check_market_alerts(mock_get_channel, mock_ctx):
    mock_channel = MagicMock()
    mock_get_channel.return_value = mock_channel

    bot.global_alert_channel_id = 1234567890
    bot.alert_threshold = 5.0
    bot.last_global_cap = 1_000_000_000

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {'total_market_cap': {'usd': 950_000_000}}
        }
        mock_get.return_value = mock_response

        await bot.check_market_alerts()

        mock_channel.send.assert_called_with(
            "**Global Market Alert:** The global market cap has changed by -5.00% to $950,000,000.00."
        )

@patch('discord.ext.commands.Bot.get_channel')
async def test_volatility_alert(mock_get_channel, mock_ctx):
    mock_channel = MagicMock()
    mock_get_channel.return_value = mock_channel

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {'price_change_percentage_24h': 12.0}  # Simulate significant change
        }
        mock_get.return_value = mock_response

        await bot.volatility_alert(mock_ctx, 'bitcoin')

        mock_channel.send.assert_called_with(
            "**Volatility Alert:** Bitcoin has experienced a significant price change of 12.00% in the last 24 hours."
        )

def test_tuto_command(mock_ctx):
    bot.tutorials = {
        'blockchain': 'A blockchain is a decentralized ledger...',
        'wallet': 'A wallet is used to store cryptocurrencies...'
    }
    
    async def run_command():
        await bot.get_command('tuto')(mock_ctx, 'blockchain')
    
    with patch('discord.ext.commands.Context.send') as mock_send:
        bot.loop.run_until_complete(run_command())
        mock_send.assert_called_with("**Tutorial on blockchain:**\nA blockchain is a decentralized ledger...")
