import os
import leakage_detector
from bottle import route, request, run, static_file, template
from leakage_types import LeakageTypes
from object_types import ObjectTypes

RECOMMENDATION_MAP = {(ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_TOP): ["door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_BOTTOM): ["door draft stopper", "door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_LEFT): ["door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_RIGHT): ["door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.POOR_INSULATION_SMALL): [],
                      (ObjectTypes.DOOR, LeakageTypes.POOR_INSULATION_LARGE): []}

@route('/upload', method='POST')
def do_upload():
    category = request.forms.get('category')
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    print("Received file: " + name + ext)
    if ext not in ('.png', '.jpg', '.jpeg'):
        return "File extension not allowed."

    save_path = os.path.dirname(os.path.realpath(__file__)) + "/data/{category}".format(category=category)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = "{path}/{file}".format(path=save_path, file=upload.filename)
    upload.save(file_path, overwrite=True)
    leakage = leakage_detector.process(file_path)
    output_file_name = upload.filename.split('.')[0] + "_detected.jpeg"
    static_path = "/static/data/{category}".format(category=category)
    static_addr = "{path}/{file}".format(path=static_path, file=output_file_name)

    print("File successfully saved to '{0}'.".format(save_path))
    #output = '<img src="' + static_addr + '">'
    #print("Accessing static address: " + output)

    return template('results', leakage=leakage, link=static_addr, recommendations=RECOMMENDATION_MAP[leakage])

@route('/')
def upload():
    return '''<form action="/upload" method="post" enctype="multipart/form-data">
                Category:      <input type="text" name="category" />
                Select a file: <input type="file" name="upload" />
                <input type="submit" value="Upload" />
              </form>'''

@route('/test')
def test():
    return '<img src="/static/denoised.jpg">'

@route('/static/<filename:path>')
def server_static(filename):
    """Serves static files from project directory."""
    root_path = os.path.dirname(os.path.realpath(__file__))
    return static_file(filename, root=root_path)


if __name__ == '__main__':
    run(host='localhost', port=8080)
