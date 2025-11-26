# docker-gammu-smsd

A Docker container for [Gammu SMS Daemon](https://wammu.eu/smsd/) that receives SMS messages and forwards them to Telegram.

## Features

- Receives SMS messages using Gammu SMSD
- Forwards received messages to a Telegram chat
- Supports proxy configuration for Telegram API
- Multi-architecture support (amd64, arm64, armv6, armv7)

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/m0ntyG/docker-gammu-smsd.git
   cd docker-gammu-smsd
   ```

2. Create the SMS directories:

   ```bash
   mkdir -p sms/{inbox,outbox,sent,error}
   ```

3. Modify the parameters in `docker-compose.yml`:
   - Set the correct device path for your USB modem
   - Set your Telegram `CHAT_ID` and `BOT_TOKEN`
   - Optionally set `PROXY` if needed

4. Start the container:

   ```bash
   docker compose up -d
   ```

## Configuration

### Environment Variables

| Variable    | Description                          | Required |
|-------------|--------------------------------------|----------|
| `CHAT_ID`   | Telegram chat ID to receive messages | Yes      |
| `BOT_TOKEN` | Telegram Bot API token               | Yes      |
| `PROXY`     | HTTP/HTTPS proxy URL                 | No       |

### Gammu Configuration

The `gammu-smsd` file contains the Gammu SMSD configuration. Key settings:

- `port`: Serial port of your USB modem (default: `/dev/ttyUSB0`)
- `connection`: Connection type (default: `at19200`)
- `PIN`: SIM card PIN if required

## License

See [LICENSE](LICENSE) for details.