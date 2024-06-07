import datetime
import psycopg2
import boto3
from flask import Flask, render_template
import urllib3

app = Flask(__name__)

# Configuración de la conexión a la base de datos PostgreSQL en RDS
db_host = 'database-2.c3m2a2wsmvys.us-east-1.rds.amazonaws.com'
db_port = '5432'
db_name = 'AWS'
db_user = 'postgres'
db_password = 'postgres'

# Conexión a la base de datos
conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)

# Configuración del cliente S3
s3 = boto3.client('s3')
bucket_name = 'musicapj'

@app.route('/')
def index():
    # Consulta a la base de datos para obtener las canciones ordenadas alfabéticamente por nombre
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM canciones ORDER BY nombre')
    songs = cursor.fetchall()
    cursor.close()
    print(songs)

    return render_template('index.html', songs=songs)


from urllib.parse import urlparse

@app.route('/play/<song_id>')
# def play_song(song_id):
#     # Consulta a la base de datos para obtener la ruta de la canción
#     cursor = conn.cursor()
#     cursor.execute('SELECT ruta FROM canciones WHERE id = %s', (song_id,))
#     song_path = cursor.fetchone()[0]
#     cursor.close()

#     # Verifica si la ruta ya contiene la URL base de S3
#     parsed_url = urlparse(song_path)
#     if parsed_url.netloc == bucket_name + ".s3.amazonaws.com":
#         # Si la URL ya contiene la URL base de S3, usa la ruta directamente
#         url = song_path
#     else:
#         # Si la URL no contiene la URL base de S3, construye la URL completa
#         url = f"https://{bucket_name}.s3.amazonaws.com/{song_path}"

#     # Renderiza solo el contenido necesario para el reproductor de música
#     return render_template('play.html', url=url)
def play_song(song_id):
    # Consulta a la base de datos para obtener la ruta de la canción
    cursor = conn.cursor()
    cursor.execute('SELECT ruta, img, nombre, artista, album  FROM canciones WHERE id = %s', (song_id,))
    data = cursor.fetchone()
    song_path = data[0]
    # img_url = data[1]
    cursor.close()

    # Verifica si la ruta ya contiene la URL base de S3
    parsed_url = urlparse(song_path)
    if parsed_url.netloc == bucket_name + ".s3.amazonaws.com":
        # Si la URL ya contiene la URL base de S3, usa la ruta directamente
        url = song_path
    else:
        # Si la URL no contiene la URL base de S3, construye la URL completa
        url = f"https://{bucket_name}.s3.amazonaws.com/{song_path}"

    # Renderiza solo el contenido necesario para el reproductor de música
    return render_template('play.html', url=url, data=data)


if __name__ == '__main__':
    app.run(debug=True)
