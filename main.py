# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, make_response
from lib.parser import extract_all
from lib.helper import get_legends, get_id_by_color, get_hpo_elements
import json

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] \
        in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('main.html')

    letter = request.files['letter']
    if not letter:
        return render_template('main.html', error='No file uploaded')

    if not allowed_file(letter.filename):
        return render_template('main.html', error='File not allowed')

    content = unicode(letter.stream.read(), 'utf-8')

    (matches, patients) = extract_all(content)
    hpo_elements = get_hpo_elements(content, matches)
    number_hpo_items = len(hpo_elements)
    words = len(content.split())

    return render_template(
        'main.html',
        data=content,
        matches=matches,
        legend=get_legends(),
        patients=patients,
        default_id=3,
        matches_hpo_json=json.dumps(hpo_elements).decode('unicode_escape'),
        number_hpo_items=number_hpo_items,
        words=words,
        ics='{0:.3g}'.format(float(number_hpo_items) / float(words) * 100),
    )


@app.route('/download', methods=['POST'])
def download():
    file_type = request.form['type']

    matches = json.loads(request.form['matches'])

    if file_type == 'base':
        result = u'cui|label\n'
    else:
        result = u'cui|label|type|score|frequency\n'

    for match in matches:
        if file_type == 'base':
            result += str(match[4]) + '|'
            result += match[0] + '\n'
        else:
            result += str(match[4]) + '|'
            result += match[0] + '|'
            result += str(match[2]) + '|'
            result += str(match[3]) + '|'
            result += str(match[5]) + '\n'

    response = make_response(result)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = \
        'attachment; filename=hpo_%s.txt' % file_type

    return response

@app.route('/download-data', methods=['POST'])
def download_data():
    data_elements = json.loads(request.form['data'])

    result = ''
    for parent_element, child_list in data_elements.iteritems():
        result += parent_element + '\n'
        for value in child_list:
            result += '\t' + value + '\n'

    response = make_response(result)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = 'attachment; filename=patients.txt'

    return response


@app.context_processor
def string_processor():

    def format_result(data, matches):
        ''' Now it builds a new html text from original text (data)
            matches in now the sorted result of the ordered dict (this has been also changed in main.html loop
            which shares the index of these elements)
        '''

        # current_positions_added = 0
        # last_painted_range = None
        # print "++",len(data)

        index = 0
        output = ''
        lastpos = 0
        texto = data
        lastann = []
        for match_data in matches:
            position = match_data[0]
            color = match_data[1][0][3]
            code = match_data[1][0][0]
            value = match_data[1][0][2]

            if position < lastpos:

               # print "Warning overlap:", value, code, lastann[1][0][0]

                pass
            else:

            # print position,texto[position:position+len(value)]

                new_value = \
                    u'<a href="#" data-toggle="modal" data-target="#modal-' \
                    + str(index) + '">'
                length = len(new_value)
                new_value = new_value + u'<span data-main="' \
                    + str(get_id_by_color(color)) \
                    + '" data-style="background-color: ' + color + '">' \
                    + value + '</span>'
                new_value = new_value + u'</a>'

                output += texto[lastpos:position] + new_value
                lastpos = position + len(value)

            # position = position + current_positions_added
            # next_position = position + len(value)

            # if last_painted_range is None or (not last_painted_range[0] < position < last_painted_range[1]):
            #    data = data[:position] + data[position:next_position].replace(value, new_value) + data[next_position:]
            #    current_positions_added = current_positions_added + 51 + length
            #    last_painted_range = [position, next_position + 51 + length]

            index = index + 1
            lastann = match_data

        output += texto[lastpos:]

        return output

    return dict(format_result=format_result)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5151)
