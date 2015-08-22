# -*- coding: UTF-8 -*-

from flask import Flask, request, render_template
from lib.parser import extract_all

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
    
    matches, patients = extract_all(content)
    legend = {
        'Persons and personal relations': '#81BEF7',
        'Observations':'#FA5858',
        'HPO': '#BD7AFF',
        'Shifters': '#A9F5A9',
        'Modifiers': '#F4FA58',
        'Genes/Anatomy': '#DF7401'
    }

    return render_template(
        'main.html',
        data=content,
        matches=matches,
        legend=legend,
        patients=patients
    )

@app.context_processor
def string_processor():
    def format_result(data, matches):
        ''' Now it builds a new html text from original text (data)
            matches in now the sorted result of the ordered dict (this has been also changed in main.html loop
            which shares the index of these elements)
        '''
        #current_positions_added = 0
        #last_painted_range = None
        #print "++",len(data)
        index = 0
        output = ""
        lastpos = 0
        texto=data
        lastann= []
        for match_data in matches:
            position = match_data[0]
            color = match_data[1][0][3]
            code =  match_data[1][0][0]
            value = match_data[1][0][2]

            if position<lastpos:
               #print "Warning overlap:", value, code, lastann[1][0][0]
               pass
            #print position,texto[position:position+len(value)]
            else:
               new_value = u'<a href="#" data-toggle="modal" data-target="#modal-' + str(index) + '">'
               length = len(new_value)
               new_value = new_value + u'<span style="background-color: ' + color + '">' + value + '</span>'
               new_value = new_value + u'</a>'

               output += texto[lastpos:position] + new_value
               lastpos = position + len(value)

            #position = position + current_positions_added
            #next_position = position + len(value)

            #if last_painted_range is None or (not last_painted_range[0] < position < last_painted_range[1]):
            #    data = data[:position] + data[position:next_position].replace(value, new_value) + data[next_position:]
            #    current_positions_added = current_positions_added + 51 + length
            #    last_painted_range = [position, next_position + 51 + length]

            index = index + 1
            lastann = match_data

        output += texto[lastpos:]

        return output

    return dict(
        format_result=format_result
    )

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=5151)
