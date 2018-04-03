import os
from bottle import route, request, static_file, run

@route('/upload', method='POST')
def do_upload():
    category = request.forms.get('category')
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    print("Received file: " + name + ext)
    if ext not in ('.png', '.jpg', '.jpeg'):
        return "File extension not allowed."

    save_path = "/tmp/{category}".format(category=category)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = "{path}/{file}".format(path=save_path, file=upload.filename)
    upload.save(file_path)
    # CALL FUNCTION TO GENERATE RESULTS HERE, RETURN SOLUTION RECOMMENDATIONS
    # AS JSON?
    return "File successfully saved to '{0}'.".format(save_path)

@route('/')
def upload():
    return '''<form action="/upload" method="post" enctype="multipart/form-data">
                Category:      <input type="text" name="category" />
                Select a file: <input type="file" name="upload" />
                <input type="submit" value="Upload" />
              </form>'''

if __name__ == '__main__':
    run(host='localhost', port=8080)