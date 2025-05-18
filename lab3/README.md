# scaling-octo-waddle

## Запуск
### 1. Собрать образ
   
``docker-compose build``
  
### 2. Запустить контейнер. Весь код запустится автоматически из-за того, что в docker-compose указаны соответствующие команды
   
``docker-compose up -d``

### 3. В файле ``logs/app.log`` можно смотреть логи из контейнера.
   
![image](https://github.com/user-attachments/assets/4bafedc8-111b-4b69-9995-eba0d7b3ca04)

### 4. По адресу ``http://localhost:5000/`` можно посмотреть на залогированные модели/метрики/параметры/артефакты
   
![image](https://github.com/user-attachments/assets/b498e6a4-0f9f-47c8-ba7e-b44d7858cc70)
