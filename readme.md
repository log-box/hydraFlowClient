### 1. Создай systemd unit:

```bash
mkdir -p ~/.config/systemd/user
```

Файл: `~/.config/systemd/user/hydra-client.service`

```ini
[Unit]
Description=HydraFlow FastAPI App
After=network.target

[Service]
Type=simple
ExecStart=/home/USERNAME/PROJECT_FOLDER/run-local.sh
WorkingDirectory=/home/USERNAME/PROJECT_FOLDER
Restart=on-failure

[Install]
WantedBy=default.target
```

> Заменить `USERNAME` на своё имя пользователя.
> Заменить `PROJECT_FOLDER` на путь к папке с проектом

### 2. Включи автозапуск и запусти:

```bash
systemctl --user daemon-reexec
systemctl --user daemon-reload
systemctl --user enable hydra-client.service
systemctl --user start hydra-client.service
```

### 3. Убедись, что systemd user-режим включён:

```bash
loginctl enable-linger $USER
```

