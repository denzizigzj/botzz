🚀 **Инструкция: Развертывание бота на VPS**  

### 1. **Клонируем репозиторий**  
```bash
git clone -b denzizigzj-patch-1 https://github.com/denzizigzj/botzz.git && cd botzz
```

### 2. **Ставим Python и зависимости**  
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
```

### 3. **Создаем виртуальное окружение**  
```bash
python3 -m venv venv && source venv/bin/activate
```

### 4. **Устанавливаем зависимости**  
```bash
pip3 install -r requirements.txt
```

### 5. **Тестируем бота**  
```bash
python3 gopota_bot.py
```
(Если работает — `Ctrl+C` для остановки.)

---

### 🔄 **Настраиваем автозапуск через systemd**  
1. Создаем файл сервиса:  
   ```bash
   sudo nano /etc/systemd/system/gopota_bot.service
   ```  
2. Вставляем конфиг (заменить `user` и пути при необходимости):  
   ```ini
   [Unit]
   Description=Gopota Telegram Bot
   After=network.target

   [Service]
   User=user
   WorkingDirectory=/home/user/botzz  # Путь к папке с ботом
   ExecStart=/home/user/botzz/venv/bin/python3 /home/user/botzz/gopota_bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```  
3. Включаем сервис:  
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start gopota_bot
   sudo systemctl enable gopota_bot
   ```

---

### 🔍 **Проверяем работу**  
- Логи:  
  ```bash
  journalctl -u gopota_bot -f
  ```  
- Статус сервиса:  
  ```bash
  systemctl status gopota_bot
  ```

