# Import dependencies
# -------------------
import psycopg2 # For Postgres operations.
from flask import Flask
from flask import render_template # Show HTML page.
from flask import request # Get user input from HTML page, in this case uploaded file data.
import json
from base64 import b64encode



# datetime object containing current date and time

# ---------------------
# PostgreSQL connection
# ---------------------


app = Flask(__name__)


t_host = "db-postgresql-blr1-98615-do-user-8626824-0.b.db.ondigitalocean.com"
t_port = "25060"
t_dbname = "image"
t_name_user = "doadmin"
t_password = "tjjq7tc0wad2vc59"
data_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_name_user, password=t_password)
db_cursor = data_conn.cursor()

# ------------
# Route to use
# ------------

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template('imageUploader.html')
    if request.method == "POST":
        msg = ""
        if request.files:
            form_data = request.files
            data = form_data.to_dict(flat = False)
            length_files = len(data['image_file'])

            # print(length_files)
            for i in data['image_file']:
                fileData = i.read()
                filename = i.filename
                try:
                    data_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_name_user, password=t_password)
                    db_cursor = data_conn.cursor()
                    db_cursor.execute("INSERT INTO image_upload (filename, filedata) VALUES (%s,%s)", (filename, psycopg2.Binary(fileData)))
                        # commit the changes to the database
                    data_conn.commit()
                    msg = "Uploaded images to database successfully"
        # close the communication with the PostgresQL database
                    db_cursor.close()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)

            # Make sure you have an item ID.
            #   We used an arbitrary number here.
            # Pass both item ID and image file data to a function
            
            return render_template("imageUploader.html", msg = msg)

        else:
            msg = "No file picked. Please choose one from your device."
            return render_template("imageUploader.html", msg = msg)

@app.route('/viewall', methods=['GET','POST'])
def viewall():
    if request.method == 'GET':
        return render_template('imageViewer.html')
    if request.method == 'POST':
        form_data = request.form
        data = form_data.to_dict(flat = False)
        print(data)
        try:
            data_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_name_user, password=t_password)
            db_cursor = data_conn.cursor()
            db_cursor.execute("SELECT * from image_upload")
            data = db_cursor.fetchall()
            print(data)
            db_cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            data = str(error)
        return render_template('imageViewer.html', data = data)
@app.route('/deleteDuplicate', methods=['POST'])
def delete_duplicates():

    try:
        data_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_name_user, password=t_password)
        db_cursor = data_conn.cursor()
        db_cursor.execute(""" DELETE FROM image_upload a USING image_upload b WHERE a.id > b.id AND a.filename = b.filename """)
                # Commit the changes to the database
        rows_deleted = db_cursor.rowcount
        data_conn.commit()
        db_cursor.close()
        print('Before if')
        if rows_deleted == 0:
            print('Inside if')
            msg = 'Image Duplicates not found'
        else:
            print('Inside else')
            msg = 'Image Duplicates deleted successfully'
    except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            msg = 'Image Duplicates could not deleted due to some error'
    return render_template('imageViewer.html', msg = msg)

@app.route("/viewImage", methods = ['GET','POST'])
def view():
    if request.method == 'GET':
        data = False
        return render_template('singleImageViewer.html', data = data)
    if request.method == 'POST':
        data_1 = True
        search_term = str(request.form['file_name']).strip()
        print(search_term)
        try:
            msg = ''
            data_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_name_user, password=t_password)
            db_cursor = data_conn.cursor()
            db_cursor.execute(""" SELECT * from image_upload WHERE filename = %s """, (search_term,))
            data = db_cursor.fetchall()
            db_cursor.close()
            print(data)
            print(len(data))
            image_list = []
            if len(data) == 0:
                msg = 'No image found in database. Check the filename'
            elif len(data) == 1:
                msg = 'Only one image found'
                image_1 = data[0][2]
                image_id = data[0][0]
                image_name = data[0][1]

                image_orig = b64encode(bytes(image_1)).decode('utf-8')

                image_details = (image_orig, image_id, image_name)
                image_list.append(image_details)
            else:
                msg = 'Multiple images found'
                for i in data:
                    image_1 = i[2]
                    image_id = i[0]
                    image_name = i[1]
                    image_orig = b64encode(bytes(image_1)).decode('utf-8')
                    image_details = (image_orig, image_id, image_name)
                    image_list.append(image_details)
                # print(image_list)
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        return render_template('singleImageViewer.html', data = data_1, images = image_list, msg =msg)
@app.route('/deleteImage', methods = ['GET','POST'])
def delete():
    if request.method == 'GET':
        return render_template('deleteImage.html')
    if request.method == 'POST':
        
        # print(search_term)
        # print(request.form)
        form_data = request.form
        data = form_data.to_dict(flat = False)
        print(data)
        search_term = str(data['file_name'][0]).strip()
        # print(data)
 
        try:
            data_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_name_user, password=t_password)
            db_cursor = data_conn.cursor()
            db_cursor.execute(""" DELETE from image_upload WHERE filename = %s """, (search_term,))
            rows_deleted = db_cursor.rowcount
            data_conn.commit()
            db_cursor.close()
            print(rows_deleted)
            if rows_deleted == 0:
                msg = 'No Image with name ' + search_term
        # Commit the changes to the database
            else:
                msg = 'Image deleted successfully'
        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
            msg = 'Image could not deleted due to some error'

        return render_template('deleteImage.html', msg = msg)




if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5500,use_reloader=False,debug=True,threaded=True)