Django 신규 프로젝트 생성
django-admin startproject 프로젝트명
python manage.py startapp 앱이름
# settings.py
INSTALLED_APPS = [] 에 앱 이름 추가 하기

모델클래스 DB 설정
python manage.py makemigrations 앱이름
python manage.py migrate