import os
import sys
sys.path.append("/home/Charlie/ThermalLeakageDetector")
import leakage_detector
from bottle import route, request, run, static_file, template
from leakage_types import LeakageTypes
from object_types import ObjectTypes



RECOMMENDATION_MAP = {(ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_TOP): ["door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_BOTTOM): ["door draft stopper", "door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_LEFT): ["door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_RIGHT): ["door weatherstrip", "foam tape", "felt tape", "caulk"],
                      (ObjectTypes.DOOR, LeakageTypes.POOR_INSULATION_SMALL): ["cellular window shade", "insulated curtain", "storm door"],
                      (ObjectTypes.DOOR, LeakageTypes.POOR_INSULATION_LARGE): ["storm door", "insulated curtain", "cellular window shade"],
                      (ObjectTypes.WINDOW, LeakageTypes.AIR_LEAK_TOP): ["foam sealant", "caulk", "window weatherstrip", "clear window insulation film"],
                      (ObjectTypes.WINDOW, LeakageTypes.AIR_LEAK_BOTTOM): ["foam sealant", "caulk", "window weatherstrip", "clear window insulation film"],
                      (ObjectTypes.WINDOW, LeakageTypes.AIR_LEAK_LEFT): ["foam sealant", "caulk", "window weatherstrip", "clear window insulation film"],
                      (ObjectTypes.WINDOW, LeakageTypes.AIR_LEAK_RIGHT): ["foam sealant", "caulk", "window weatherstrip", "clear window insulation film"],
                      (ObjectTypes.WINDOW, LeakageTypes.POOR_INSULATION_SMALL): ["cellular shades", "insulated curtains", "double pane window", "storm window", "clear window insulation film"],
                      (ObjectTypes.WINDOW, LeakageTypes.POOR_INSULATION_LARGE): ["double pane window", "storm window", "cellular shades", "insulated curtains", "clear window insulation film"]
                      }

OBJECT_DESC_MAP = {ObjectTypes.DOOR: "Your home's exterior doors can contribute significantly to heat loss via air leakage and through conduction. ",
                   ObjectTypes.WINDOW: "Your home's exterior windows can contribute significantly to heat loss via air leakage and through conduction. "}


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
    leakage = leakage_detector.process(file_path, append_os=False)
    leakage_types = leakage[1]
    description = OBJECT_DESC_MAP[leakage[0]]
    recommendations = []
    if leakage[0] == ObjectTypes.DOOR:
        if LeakageTypes.AIR_LEAK_BOTTOM in leakage_types:
            description += "Reducing the amount of air that leaks in and out of your home is a cost-effective way to cut heating " \
                           "and cooling costs, improve durability, increase comfort, and create a healthier indoor environment. " \
                           "Caulking and weatherstripping are simple and effective air-sealing techniques that offer quick returns on investment. " \
                           "A draft stopper placed in the bottom crack of doors can effectively reduce air leakage. "
            recommendations.extend(RECOMMENDATION_MAP[(ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_BOTTOM)])
        elif any(lk in leakage_types for lk in [LeakageTypes.AIR_LEAK_TOP, LeakageTypes.AIR_LEAK_LEFT, LeakageTypes.AIR_LEAK_RIGHT]):
            description += "Reducing the amount of air that leaks in and out of your home is a cost-effective way to cut heating " \
                           "and cooling costs, improve durability, increase comfort, and create a healthier indoor environment. " \
                           "Caulking and weatherstripping are simple and effective air-sealing techniques that offer quick returns on investment. "
            recommendations.extend(RECOMMENDATION_MAP[(ObjectTypes.DOOR, LeakageTypes.AIR_LEAK_TOP)])
        if LeakageTypes.POOR_INSULATION_LARGE in leakage_types or LeakageTypes.POOR_INSULATION_SMALL in leakage_types:
            description += "Old and poorly insulated doors can cause significant heat loss through conduction. New exterior doors often fit and insulate better than older types. " \
                           "If you have older doors in your home, replacing them with more energy-efficient doors might be a good investment, resulting in lower heating and cooling costs. " \
                           "Windows on doors can result in greater heat loss through conduction, and this may be mitigated with cellular shades or insulated curtains.",
            recommendations.extend(RECOMMENDATION_MAP[(ObjectTypes.DOOR, LeakageTypes.POOR_INSULATION_LARGE)])
    else:
        if any(lk in leakage_types for lk in [LeakageTypes.AIR_LEAK_TOP, LeakageTypes.AIR_LEAK_LEFT, LeakageTypes.AIR_LEAK_RIGHT, LeakageTypes.AIR_LEAK_BOTTOM]):
            description += "Reducing the amount of air that leaks in and out of your home is a cost-effective way to cut heating " \
                           "and cooling costs, improve durability, increase comfort, and create a healthier indoor environment. " \
                           "Window insulation films wrapped around windows help mitigate air leaks and block against solar heat gain. " \
                           "Caulking and weatherstripping are simple and effective air-sealing techniques that offer quick returns on investment. ",
            recommendations.extend(RECOMMENDATION_MAP[(ObjectTypes.WINDOW, LeakageTypes.AIR_LEAK_BOTTOM)])
        if LeakageTypes.POOR_INSULATION_LARGE in leakage_types or LeakageTypes.POOR_INSULATION_SMALL in leakage_types:
            description += "Poorly insulated windows can waste energy through conduction. " \
                           "When selecting new windows, consider the frame materials, the glazing or glass features, gas fills and spacers, and the type of operation. " \
                           "If your budget is tight, storm windows are less expensive than new, energy-efficient windows. " \
                           "Window coverings can also reduce energy loss through the windows, lower heating and cooling bills, and improve home comfort. " \
                           "Window insulation films wrapped around windows help mitigate air leaks and block against solar heat gain. "
            recommendations.extend(RECOMMENDATION_MAP[(ObjectTypes.WINDOW, LeakageTypes.POOR_INSULATION_LARGE)])

    output_file_name = upload.filename.split('.')[0] + "_detected.jpeg"
    static_path = "/static/data/{category}".format(category=category)
    static_addr = "{path}/{file}".format(path=static_path, file=output_file_name)

    print("File successfully saved to '{0}'.".format(save_path))

    return template('results', leakage=leakage, link=static_addr, infosite="https://www.energy.gov/energysaver/energy-saver",
                    description=description, recommendations=list(set(recommendations)))

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
