# proxy    
Запуск:    
sudo gunicorn -w 4 --threads 2 -b 0.0.0.0:5000 proxy:app
sudo gunicorn --threads 2 -b 127.0.0.1:3200 statistic:app
  
    
Запускаем через screen    
