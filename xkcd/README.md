
#commands to run the project
- docker-compose config
- docker-compose up -d
- docker-compose down -v
- docker-compose logs -f
- docker-compose ps

#postgres database:
Host: localhost
Port: 5433 (since we mapped 5432->5433 in docker-compose)
Database: xkcd
Username: airflow
Password: airflow

#airflow:
Host:http://localhost:8080/
Username: admin
Password: admin

#ingestion comics table query:
SELECT comic_id, title, alt_text, img_url, publish_date, created_at
FROM public.comics;